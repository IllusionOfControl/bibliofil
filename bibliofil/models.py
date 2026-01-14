from dataclasses import dataclass, replace


@dataclass(slots=True)
class BiblioFile:
    id: int
    name: str
    extension: str
    path: str
    size: int
    md5: str | None = None
    created_at: str | None = None
    archive_id: int | None = None
    is_archive: int = 0

    def update(self, **changes):
        return replace(self, **changes)

    def to_tuple(self):
        return (
            self.name,
            self.extension,
            self.path,
            self.size,
            self.md5,
            self.created_at,
            self.archive_id,
            self.is_archive,
        )

    def __repr__(self):
        return f"BiblioFile(id='{self.id}' name='{self.name}' size={self.size} md5='{self.md5}' archive_id={self.archive_id})')"


@dataclass(slots=True)
class BiblioExtStat:
    extension: str
    count: int
    size: int
