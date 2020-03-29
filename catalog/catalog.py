from dataclasses import dataclass
from typing import Iterable, Optional, Union
from pathlib import Path

from .db import DatabaseHandler


@dataclass
class Category:
    id: int
    name: str

    def __hash__(self):
        return self.id.__hash__()

@dataclass
class Product:
    id: int
    name: str


class Catalog:
    def __init__(self, path: Path):
        assert path.exists()
        self._db = DatabaseHandler(path)

    def get_categories(self, offset: Optional[int] = None, limit: Optional[int] = None) -> Iterable[Category]:
        return [Category(id, name) for id, name in self._db.get_categories(offset=offset, limit=limit)]

    def get(self,
            category: Union[Category, int, None] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None) -> Iterable[Product]:

        if isinstance(category, Category):
            category = category.id

        return [Product(id, name) for id, name in
            self._db.get_products(category=category, offset=offset, limit=limit)]

    def find(self, request: str, offset: Optional[int] = None, limit: Optional[int] = None):
        count, raw = self._db.find_products(request, offset, limit)
        raw = ((Category(cid, cname), Product(pid, pname)) for cid, cname, pid, pname in raw)

        result = {}
        for category, product in raw:
            result[category] = result.get(category) or []
            result[category].append(product)

        return count, result

    def find_products(self, products_ids: Iterable[int], offset: Optional[int] = None, limit: Optional[int] = None) -> Iterable['Product']:
        raw = self._db.get_products_names(products_ids)
        products = []
        for index in range(offset + 1, offset + limit + 1):
            products.append(raw[index])
        return products

    def get_url(self, product: Product) -> Optional[str]:
        return self._db.get_product_url(product.id)

    def get_png_path(self, product_id: int) -> Optional[Path]:
        path, photo_id = self._db.get_png_path(product_id)
        if photo_id != '-1':
            return photo_id
        assert path.exists()
        return path

    def update_photo_id(self, photo_id: int, id: int):
        self._db.update_column("photo_id", photo_id, id)

    def get_description(self, id: int) -> str:
        return self._db.get_description(id)

    def insert_into_basket(self, user_id: int, good_id: int, count: int):
        self._db.insert_into_basket_version2(user_id, good_id, count)

    def get_basket(self, user_id: int, offset: int, limit: int) -> Iterable[Product]:
        count, buttons = self._db.get_basket(user_id, offset, limit)
        return count, buttons[0]

    def delete_product_from_basket(self, user_id: int, good_id: int):
        self._db.delete_product_from_basket(user_id, good_id)
