import sqlite3
import pathlib
import zipfile

from bibliofil.models import BiblioFile


def save_entry(cursor, entry: BiblioFile) -> int:
    query = '''
        INSERT INTO files (name, extension, path, size, md5, created_at, parent_id, is_archive)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, entry.to_tuple())
    return cursor.lastrowid


def index_archive(archive_path: str, parent_id: int, conn: sqlite3.Connection):
    ext = pathlib.Path(archive_path).suffix.lower()
    cursor = conn.cursor()

    if ext == '.7z':
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                    archive.extractall(path=tmpdir)
                for p in Path(tmpdir).rglob('*'):
                    if p.is_file():
                        entry = FileEntry(
                            name=p.name,
                            extension=p.suffix.lower(),
                            path=f"{archive_path}://{p.relative_to(tmpdir)}",
                            size=p.stat().st_size,
                            md5=get_md5(p),
                            parent_id=parent_id
                        )
                        save_entry(cursor, entry)
        except Exception as e:
            print(f"  [Error 7z] {archive_path}: {e}")

    elif ext == '.zip':
        try:
            with zipfile.ZipFile(archive_path, 'r') as z:
                for info in z.infolist():
                    if info.is_dir(): continue
                    with z.open(info) as f:
                        entry = FileEntry(
                            name=os.path.basename(info.filename),
                            extension=Path(info.filename).suffix.lower(),
                            path=f"{archive_path}://{info.filename}",
                            size=info.file_size,
                            md5=get_md5(f),
                            parent_id=parent_id
                        )
                        save_entry(cursor, entry)
        except Exception as e:
            print(f"  [Error ZIP] {archive_path}: {e}")


def run_index(args):
    init_db(args.db)
    conn = get_db_conn(args.db)
    archive_exts = {'.zip', '.7z', '.tar', '.gz'}

    print(f"[*] Сканирование: {args.path}")
    for root, dirs, files in os.walk(args.path):
        for name in files:
            full_path = os.path.join(root, name)
            p = Path(full_path)
            print(f"Indexing: {name}")

            try:
                stats = p.stat()
                is_arch = 1 if p.suffix.lower() in archive_exts else 0

                entry = FileEntry(
                    name=name,
                    extension=p.suffix.lower(),
                    path=str(p.absolute()),
                    size=stats.st_size,
                    md5=get_md5(full_path),
                    created_at=datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    is_archive=is_arch
                )

                cursor = conn.cursor()
                file_id = save_entry(cursor, entry)

                if is_arch:
                    index_archive(full_path, file_id, conn)

                conn.commit()
            except Exception as e:
                print(f"  [Skip] {full_path}: {e}")
    conn.close()


def start_indexing(root_path, db_path):
    conn = create_db(db_path)
    cursor = conn.cursor()

    archive_exts = {'.zip', '.7z', '.tar', '.gz', '.bz2', '.xz'}

    for root, dirs, files in os.walk(root_path):
        for name in files:
            full_path = os.path.join(root, name)
            ext = Path(name).suffix.lower()
            is_arch = 1 if ext in archive_exts else 0

            print(f"Обработка: {full_path}")

            try:
                stats = os.stat(full_path)
                md5_val = get_file_md5(full_path)
                mtime = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

                # 1. Сначала сохраняем сам файл (или файл-архив)
                cursor.execute('''
                    INSERT INTO files (name, extension, path, size, md5, created_at, is_archive)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, ext, full_path, stats.st_size, md5_val, mtime, is_arch))

                # 2. Получаем ID только что созданной записи
                current_file_id = cursor.lastrowid
                conn.commit()

                # 3. Если это архив, заходим внутрь и передаем ему archive_id (current_file_id)
                if is_arch:
                    process_archive_contents(full_path, current_file_id, conn)

            except Exception as e:
                print(f"  [Ошибка системы] {full_path}: {e}")

    conn.close()
    print("\nИндексация завершена успешно.")