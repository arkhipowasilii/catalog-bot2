import logging

from bot import Bot

def main():
    token = "564367094:AAHofwd0C8yWU68DxcWlGXyT7t1A_o7bDyA"
    logging.basicConfig(level=logging.DEBUG)
    Bot(token).start()

if __name__ == '__main__':
    main()