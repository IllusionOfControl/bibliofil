from dataclasses import dataclass, replace


@dataclass(slots=True)
class BiblioFile:
    name: str
    extension: str
    path: str
    size: int
    md5: str | None = None
    created_at: str | None = None
    parent_id: int | None = None
    is_archive: int = 0

    def update(self, **changes):
        return replace(self, **changes)

    def to_tuple(self):
        return (
            self.name, self.extension, self.path, self.size,
            self.md5, self.created_at, self.parent_id, self.is_archive
        )

    def __repr__(self):
        return f"BiblioFile(name='{self.name}')"


@dataclass(slots=True)
class BiblioExtStat:
    extension: str
    count: int
    size: int
    percent: float