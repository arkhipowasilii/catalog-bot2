from dataclasses import dataclass
import sqlite3 as sqlite
from pathlib import Path
from typing import Iterable, Optional, Tuple, Union


class DatabaseHandler:
    def __init__(self, path: Path):
        assert path.exists()
        self._connect = sqlite.connect(str(path), check_same_thread=False)

    def get_categories(self, offset: Optional[int] = None, limit: Optional[int] = None) -> Iterable[Tuple[int, str]]:
        return self._connect.cursor().execute(f"SELECT id, name FROM categories "
                                              f"LIMIT {limit or -1} OFFSET {offset or 0}")

    def get_products(self,
                     category: Optional[int] = None,
                     offset: Optional[int] = None,
                     limit: Optional[int] = None) -> Iterable[Tuple[int, str]]:

        if category:
            category = f"WHERE category_id = {category}"
        else:
            category = ""

        return self._connect.cursor().execute(f"SELECT id, name FROM goods "
                                              f"{category} "
                                              f"LIMIT {limit or -1} OFFSET {offset or 0}")

    def find_products(self,
                      request: str,
                      offset: Optional[int] = None,
                      limit: Optional[int] = None) -> Iterable[Tuple[int, str, int, str]]:

        sql = f"SELECT ct.id, ct.name, gd.id, gd.name FROM goods as gd " \
              f"LEFT JOIN categories as ct ON gd.category_id = ct.id " \
              f"WHERE UPPER(gd.name) like '%{request.upper()}%' " \
              f"LIMIT {limit or -1} OFFSET {offset or 0}"

        return self._connect.cursor().execute(sql)

    def get_product_url(self, product: Union[str, int]) -> Optional[str]:
        sql = "SELECT url from goods "
        if isinstance(product, str):
            sql += f"WHERE name like '%{product}%' "
        elif isinstance(product, int):
            sql += f"WHERE id = {product} "
        else:
            assert False, type(product)

        sql += f"LIMIT 1"

        raw = self._connect.cursor().execute(sql).fetchmany(1)

        if len(raw) != 0:
            return raw[0]
        else:
            return None