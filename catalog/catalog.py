import sqlite3 as sqlite
from collections import Iterable
from dataclasses import dataclass
from pathlib import Path


class DatabaseHandler:
    def __init__(self, path: Path):
        assert path.exists()
        self._connect = sqlite.connect(str(path), check_same_thread=False)

@dataclass
class Category:
    name: str

@dataclass
class Position:
    name: str

class Catalog:
    def __init__(self, path: Path):
        assert path.exists()
        self._db = DatabaseHandler(path)

    def find(self, request: str, offset: int) -> Iterable[Position]:
        pass

    def get_categories(self, offset: int) -> Iterable[Category]:
        pass

    def get(self, category: Category, offset: int) -> Iterable[Position]:
        pass