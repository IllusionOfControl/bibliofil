import logging
import pathlib
import tarfile
import tempfile
import zipfile
from datetime import datetime
from typing import Callable, Generator

import py7zr

from bibliofil.database import Database
from bibliofil.models import BiblioFile
from bibliofil.utils import calculate_md5

logger = logging.getLogger(__name__)


class ArchiveProcessor:
    _registry: dict[str, Callable[[pathlib.Path], Generator[BiblioFile, None, None]]] = {}

    @classmethod
    def register(cls, *extensions: str):
        def decorator(func: Callable):
            for ext in extensions:
                cls._registry[ext.lower()] = func
            return func

        return decorator

    @classmethod
    def get_entries(cls, path: str | pathlib.Path) -> Generator[BiblioFile, None, None]:
        ext = path.suffix.lower()
        handler = cls._registry.get(ext)
        if handler:
            yield from handler(path)

    @classmethod
    def is_archive(cls, path: pathlib.Path) -> bool:
        ext = path.suffix.lower()
        return ext in cls._registry

    @classmethod
    def supported_extensions(cls) -> list[str]:
        return list(cls._registry.keys())


@ArchiveProcessor.register('.zip')
def _handle_zip(full_path: str | pathlib.Path) -> Generator[BiblioFile]:
    with zipfile.ZipFile(full_path, 'r') as z:
        for info in z.infolist():
            if info.is_dir(): continue
            with z.open(info) as f:
                yield BiblioFile(
                    name=pathlib.Path(info.filename).name,
                    extension=pathlib.Path(info.filename).suffix.lower(),
                    path=f"{full_path}://{info.filename}",
                    size=info.file_size,
                    md5=calculate_md5(f)
                )


@ArchiveProcessor.register('.tar', '.gz', '.bz2', '.xz')
def _handle_tar(full_path: str | pathlib.Path) -> Generator[BiblioFile]:
    with tarfile.open(full_path, "r:*") as t:
        for member in t.getmembers():
            if not member.isfile(): continue
            f = t.extractfile(member)
            if f:
                yield BiblioFile(
                    name=member.name,
                    extension=pathlib.Path(member.name).suffix.lower(),
                    path=f"{full_path}://{member.name}",
                    size=member.size,
                    md5=calculate_md5(f)
                )


@ArchiveProcessor.register('.7z')
def _handle_7z(full_path: str | pathlib.Path) -> Generator[BiblioFile]:
    with tempfile.TemporaryDirectory() as tmpdir:
        with py7zr.SevenZipFile(full_path, mode='r') as archive:
            archive.extractall(path=tmpdir)
        for p in pathlib.Path(tmpdir).rglob('*'):
            if p.is_file():
                yield BiblioFile(
                    name=p.name,
                    extension=p.suffix.lower(),
                    path=f"{full_path}://{p.relative_to(tmpdir)}",
                    size=p.stat().st_size,
                    md5=calculate_md5(p)
                )


def run_indexing(database: Database, root_path: str) -> None:
    root = pathlib.Path(root_path)

    for file_path in root.rglob('*'):
        if not file_path.is_file(): continue

        try:
            is_arch = ArchiveProcessor.is_archive(file_path)

            main_entry = BiblioFile(
                name=file_path.name,
                extension=file_path.suffix.lower(),
                path=str(file_path.absolute()),
                size=file_path.stat().st_size,
                md5=calculate_md5(file_path),
                created_at=datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                is_archive=is_arch
            )

            archive_id = database.insert_file(main_entry)

            if is_arch:
                for sub_entry in ArchiveProcessor.get_entries(file_path):
                    database.insert_file(sub_entry.update(parent_id=archive_id))
        except Exception as e:
            logger.error(e)
