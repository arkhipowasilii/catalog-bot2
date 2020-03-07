import logging
from pathlib import Path

from bot import Bot
from catalog import Catalog


def main():
    token = "701721190:AAEtlb05Fbi7VO9jRaOd6TARNv-kYhQj-ys"
    db = Path("./catalog.db")
    logging.basicConfig(level=logging.DEBUG)
    Bot(token, Catalog(db)).start()

if __name__ == '__main__':
    main()