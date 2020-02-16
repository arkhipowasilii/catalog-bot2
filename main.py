import logging
from pathlib import Path

from bot import Bot
from catalog import Catalog


def main():
    token = "564367094:AAHofwd0C8yWU68DxcWlGXyT7t1A_o7bDyA"
    db = Path("./catalog.db")
    logging.basicConfig(level=logging.DEBUG)
    Bot(token, Catalog(db)).start()

if __name__ == '__main__':
    main()