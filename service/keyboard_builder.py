from collections import Callable
from typing import Optional, Tuple, Any, Iterable

from telegram import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button


class Serializer:
    def __init__(self, handler):
        self._handler = handler

    def serialize(self, cb: Callable, data: Tuple[Any]) -> str:
        assert getattr(self._handler, cb.__name__) == cb
        return f"{cb.__name__}|{','.join(map(str, data))}"

    def deserialize(self, raw: str) -> Optional[Tuple[Callable, Tuple[str], Tuple[int]]]:
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
        data = self._serializer.serialize(callback, data or [])
        self._buttons[-1].append(Button(text=text, callback_data=data))
        return self

    def line(self) -> 'KeyboardBuilder':
        self._buttons.append([])
        return self

    def pager(self, callback: Callable,
              in_page: int,
              current_offset: int,
              max_offset: int,
              *args) -> Optional['KeyboardBuilder']:
        if not self._buttons[0]:
            return None
        self.line()
        if current_offset > 0:
            self.button('<-', callback, (current_offset - in_page, *args))
        if current_offset < max_offset - in_page:
            self.button('->', callback, (current_offset + in_page, *args))
        self.line()
        return self

    def back(self, callback: Callable, *args) -> 'KeyboardBuilder':
        return self.button('Back', callback, args)

    def get(self) -> Markup:
        if len(self._buttons[-1]) == 0:
            self._buttons = self._buttons[:-1]
        return Markup(self._buttons)


from telegram import ReplyKeyboardMarkup as MenuMarkup
from telegram import KeyboardButton as MenuButton

class MenuBuilder:
    def __init__(self, serializer):
        self._serializer = serializer
        self._buttons = []
        self._buttons.append([])

    def button(self, text: str, callback: Callable, data: Iterable[Any] = None) -> 'MenuBuilder':
        data = self._serializer.serialize(callback, data or [])
        self._buttons[-1].append(MenuButton(text=text, callback_data=data))
        return self

    def line(self) -> 'KeyboardBuilder':
        self._buttons.append([])
        return self

    def get(self) -> MenuMarkup:
        if len(self._buttons[-1]) == 0:
            self._buttons = self._buttons[:-1]
        return MenuMarkup(self._buttons)
