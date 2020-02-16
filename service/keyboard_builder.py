from collections import Callable
from typing import Optional, Tuple, Any, Iterable

from telegram import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button

class Serializer:
    def __init__(self, handler):
        self._handler = handler

    def serialize(self, cb: Callable, data: Tuple[Any]) -> str:
        assert getattr(self._handler, cb.__name__) == cb
        return f"{cb.__name__}|{','.join(data)}"

    def deserialize(self, raw: str) -> Optional[Tuple[Callable, Tuple[str]]]:
        cb, data = raw.split('|')

        cb = getattr(self._handler, cb)
        data = data.split(',')

        if cb:
            return cb, data
        else:
            return None

class KeyboardBuilder:
    def __init__(self, serializer):
        self._serializer = serializer
        self._buttons = []
        self._buttons.append([])

    def button(self, text: str, callback: Callable, data: Iterable[Any] = None) -> 'KeyboardBuilder':
        self._buttons[-1].append(Button(text=text, callback_data=self._serializer.serialize(callback, data or [])))
        return self

    def line(self) -> 'KeyboardBuilder':
        self._buttons.append([])
        return self

    def pager(self, callback: Callable, in_page: int, current_offset: int, *args) -> 'KeyboardBuilder':
        self.line()
        if current_offset > 0:
            self.button('<-', callback, (current_offset - in_page, *args))
        return self.button('->', callback, (current_offset + in_page, *args)).line()

    def back(self, callback: Callable, *args) -> 'KeyboardBuilder':
        return self.button('<-', callback, args)

    def get(self) -> Markup:
        return Markup(self._buttons)
