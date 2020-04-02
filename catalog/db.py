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

        sql2 = f"SELECT count(*) FROM goods " \
               f"WHERE upper_name like '%{request.upper()}%' "

        result = self._connect.cursor().execute(sql)
        count = self._connect.cursor().execute(sql2).fetchone()
        return count[0], result

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

    def update_upper_name(self):
        for id, name in self._connect.cursor().execute("SELECT id, name FROM goods").fetchall():
            self._connect.cursor().execute(f"UPDATE goods SET upper_name = '{name.upper()}' WHERE id = {id}")
            self._connect.commit()

    def alter_table(self, column_name):
        sql = f"ALTER TABLE goods ADD COLUMN {column_name} text"
        self._connect.cursor().execute(sql)
        self._connect.commit()

    def add_description(self):
        for id in self._connect.cursor().execute("SELECT id FROM goods").fetchall():
            self._connect.cursor().execute(f"UPDATE goods SET photo_id = -1 WHERE id = {id[0]}")
            self._connect.commit()

    def get_png_path(self, id: int) -> Tuple[Path, int]:
        sql = f'SELECT png_filename, photo_id FROM goods WHERE id = {id}'
        result = self._connect.cursor().execute(sql).fetchone()
        filename = f"{result[0]}"
        return (Path.cwd() / 'resources' / 'png' / filename), result[1]

    def get_description(self, id: int) -> str:
        sql = f'SELECT description FROM goods WHERE id = {id}'
        return self._connect.cursor().execute(sql).fetchone()[0]

    def update_column(self, column: str, value: int, id: int):
        if isinstance(value, str):
            value = f"'{value}'"
        sql = f"UPDATE goods SET {column} = {value} WHERE id = {id}"
        self._connect.cursor().execute(sql)
        self._connect.commit()

    def insert_into_basket(self, user_id: int, good_id: int, count: int):
        sql_update = f"UPDATE basket SET count = count + {count} " \
            f"WHERE user_id = {user_id} AND good_id = {good_id}"
        sql_insert = f"INSERT INTO basket (user_id, good_id, count) " \
            f"SELECT {user_id}, {good_id}, 1 " \
            f"WHERE (SELECT Changes() = 0)"
        cursor = self._connect.cursor()
        cursor.execute(sql_update)
        cursor.execute(sql_insert)
        self._connect.commit()

    def get_basket(self, user_id: int, offset: int, limit: int) -> Union[int, Iterable[Tuple[int, str, str, int]]]:
        sql1 = f"SELECT gd.id, gd.name, gd.photo_id, ba.count FROM basket as ba "\
            f"LEFT JOIN goods as gd ON ba.good_id = gd.id " \
            f"WHERE ba.user_id = {user_id} " \
            f"ORDER BY gd.name " \
            f"LIMIT {limit} OFFSET {offset}"

        sql2 = f"SELECT count(*) FROM basket " \
            f"WHERE user_id = {user_id}"
        return self._connect.cursor().execute(sql2).fetchone()[0], self._connect.cursor().execute(sql1).fetchall()

    def delete_product_from_basket(self, user_id: int, good_id: int):
        sql = f"DELETE FROM basket WHERE user_id = {user_id} AND good_id = {good_id}"
        self._connect.cursor().execute(sql)
        self._connect.commit()


if __name__ == '__main__':
    db = DatabaseHandler(Path(r'/Users/arkhipowasilii/PycharmProjects/catalog-bot2/catalog.db'))
    db.add_description()
