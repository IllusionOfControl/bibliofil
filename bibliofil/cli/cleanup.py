import os

from bibliofil.database import Database
from bibliofil.utils import parse_to_bytes


def run_cleanup(
    database: Database,
    include: list[str],
    exclude: list[str],
    min_size: str = None,
    max_size: str = None,
    dry_run: bool = True,
):
    min_b = parse_to_bytes(min_size)
    max_b = parse_to_bytes(max_size)

    dupes = database.get_duplicates(include, exclude, min_b, max_b)

    if not dupes:
        print("No duplicates to clean.")
        return

    current_md5 = None
    deleted_count = 0
    freed_space = 0

    print(f"{'ACTION':<10} | {'NAME'}")
    print("-" * 60)

    for biblio_file in dupes:
        if biblio_file.md5 != current_md5:
            current_md5 = biblio_file.md5
            print(f"{'[KEEP]':<10} | {biblio_file.name} (Original)")
            continue

        file_path = biblio_file.path

        if dry_run:
            print(f"{'[WILL DEL]':<10} | {biblio_file.name}")
            deleted_count += 1
            freed_space += biblio_file.size
        else:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"{'[DELETED]':<10} | {biblio_file.name}")
                    deleted_count += 1
                    freed_space += biblio_file.size
                    database.delete_file(biblio_file.id)
                else:
                    print(f"{'[SKIP]':<10} | {biblio_file.name} (File not found)")
            except Exception as e:
                print(f"{'[ERROR]':<10} | {biblio_file.name} : {e}")

    print("-" * 60)
    mode_str = " (DRY RUN)" if dry_run else ""
    print(f"Total files to delete: {deleted_count}")
    print(f"Total space to free{mode_str}: {freed_space / (1024 * 1024):.2f} MB")
