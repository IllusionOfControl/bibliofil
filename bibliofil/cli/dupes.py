from bibliofil.database import Database


def run_dupes(database: Database, include: list[str], exclude: list[str]):
    for biblio_file in database.get_duplicates(include, exclude):
        curr_md5 = None
        if biblio_file.md5 != curr_md5:
            print(f"\nSHA: {biblio_file.md5} ({biblio_file.size / 1024 / 1024:.2f} MB)")
            curr_md5 = biblio_file.md5
        loc = "[ARCHIVE]" if biblio_file.parent_id else "[DISK]"
        print(f"  {loc} {biblio_file.path}")
