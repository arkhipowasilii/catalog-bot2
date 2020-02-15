from collections import Callable
from typing import Optional, Tuple

from telegram import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button

class Serializer:
    def __init__(self, handler):
        self._handler = handler

    def serialize(self, cb: Callable, data: str) -> str:
        assert getattr(self._handler, str(cb)) == cb
        return f"{cb}|{data}"

    def deserialize(self, raw: str) -> Optional[Tuple[Callable, str]]:
        cb, data = raw.split('|')
        cb = getattr(self._handler, cb)
        if cb:
            return cb, data
        else:
            return None

class KeyboardBuilder:
    def __init__(self, serializer):
        self._serializer = serializer
        self._buttons = []
        self._buttons.append([])

    def button(self, text: str, callback: Callable, data: str = None) -> 'KeyboardBuilder':
        self._buttons[-1].append(Button(text=text, callback_data=self._serializer.serialize(callback, data or '')))
        return self

    def line(self) -> 'KeyboardBuilder':
        self._buttons.append([])
        return self

    def get(self) -> Markup:
        return Markup(self._buttons)
