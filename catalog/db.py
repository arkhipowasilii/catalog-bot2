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
                                              f"ORDER BY name "
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
                                              f"ORDER BY name "
                                              f"LIMIT {limit or -1} OFFSET {offset or 0}")

    def find_products(self,
                      request: str,
                      offset: Optional[int] = None,
                      limit: Optional[int] = None) -> Iterable[Tuple[int, str, int, str]]:

        sql = f"SELECT ct.id, ct.name, gd.id, gd.name FROM goods as gd " \
              f"LEFT JOIN categories as ct ON gd.category_id = ct.id " \
              f"WHERE gd.upper_name like '%{request.upper()}%' " \
              f"ORDER BY ct.name, gd.name " \
              f"LIMIT {limit or -1} OFFSET {offset or 0}"

        result = self._connect.cursor().execute(sql)
        return result

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

    def update_name(self):
        for id, name in self._connect.cursor().execute("SELECT id, name FROM goods").fetchall():
            self._connect.cursor().execute(f"UPDATE goods SET upper_name = '{name.upper()}' WHERE id = {id}")
            self._connect.commit()

    def alter_table(self):
        sql = "ALTER TABLE goods ADD COLUMN png_filename text"
        self._connect.cursor().execute(sql)
        self._connect.commit()

    def add_description(self):
        for id in self._connect.cursor().execute("SELECT id FROM goods").fetchall():
            self._connect.cursor().execute(f"UPDATE goods SET png_filename = 'spam.png' WHERE id = {id[0]}")
            self._connect.commit()

    def get_products_names(self, products_ids: Iterable[int], offset: Optional[int] = None, limit: Optional[int] = None):
        result = []
        for index in range(offset, offset + limit):
            result.append(self._connect.cursor().execute(f"SELECT id, name FROM goods WHERE id = {id} "))

    def get_png_path(self, id: int) -> 'Path':
        result = {self._connect.cursor().execute(f'SELECT png_filename FROM goods WHERE id = {id}')}
        result = f"{result[0]}"
        return Path(r'C:\Users\Intel Core i7\PycharmProjects\catalog-bot\resources\png') / result

if __name__ == '__main__':
    db = DatabaseHandler(Path(r'C:\Users\Intel Core i7\PycharmProjects\catalog-bot\catalog.db'))
    db.add_description()
