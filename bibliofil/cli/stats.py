import logging
from bibliofil.database import Database

logging = logging.getLogger(__name__)


def run_stats(database: Database):
    total_size = database.get_total_size()

    print(f"{'EXT':<10} | {'COUNTS':<10} | {'SIZE (MB)':<12} | {'%':<5}")
    for ext_stat in database.get_extension_stats():
        print(
            "{ext:<10} | {count:<10} | {size:.2f} MB | {perc:<5.1f}".format(
                ext=ext_stat.extension,
                count=ext_stat.count,
                size=ext_stat.size / 1024 / 1024,
                perc=round(ext_stat.count * 100 / total_size, 2),
            )
        )
