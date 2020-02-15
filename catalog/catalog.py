from dataclasses import dataclass
from typing import Iterable, Optional, Union
from pathlib import Path

from .db import DatabaseHandler


@dataclass
class Category:
    id: int
    name: str


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
        raw = [(Category(cid, cname), Product(pid, pname)) for cid, cname, pid, pname in self._db.find_products(request, offset, limit)]

        result = {}
        for category, product in raw:
            result[category] = result.get(category) or []
            result[category].append(product)

        return result

    def get_url(self, product: Product) -> Optional[str]:
        return self._db.get_product_url(product.id)