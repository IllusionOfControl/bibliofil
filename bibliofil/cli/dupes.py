from bibliofil.database import Database
from bibliofil.utils import parse_to_bytes


def run_dupes(
    database: Database,
    include: list[str],
    exclude: list[str],
    min_size: str,
    max_size: str,
):
    min_b = parse_to_bytes(min_size)
    max_b = parse_to_bytes(max_size)

    dupes = database.get_duplicates(include, exclude, min_b, max_b)

    if not dupes:
        print("No duplicates found")
        return

    print(f"{'EXT':<6} | {'SIZE (MB)':<12} | {'NAME AND PATH'}")
    print("-" * 110)

    current_md5 = None
    total_wasted_space = 0

    for biblio_file in dupes:
        size_mb = biblio_file.size / (1024 * 1024)

        if biblio_file.md5 != current_md5:
            if current_md5 is not None:
                print("-" * 40)
            current_md5 = biblio_file.md5
            print(f"md5 hash: {biblio_file.md5}")
            status = "[ORIGIN]"
        else:
            total_wasted_space += biblio_file.size
            status = "[DUP]"

        print(
            f"{biblio_file.extension or 'no_ext':<6} | {size_mb:<12.2f} | {status} {biblio_file.name} ({biblio_file.path})"
        )

    print("-" * 110)
    print(f"Total can be cleaned: {total_wasted_space / (1024 * 1024):.2f} МБ")
