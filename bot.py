from telegram import Update
from typing import List, Tuple, Dict, Iterable, Callable
from catalog import Catalog, Product
from service.keyboard_builder import KeyboardBuilder as KB, Serializer
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from PIL import Image
from pathlib import Path

IN_PAGE = 1

class Bot:
    def __init__(self, token: str, catalog):
        self._updater = Updater(token=token, use_context=True)
        self._serializer = Serializer(self)
        self._catalog: Catalog = catalog
        self._connect()

    def start(self):
        self._updater.start_polling()

    @property
    def _dispatcher(self) -> Dispatcher:
        return self._updater.dispatcher

    def _connect(self):
        self._dispatcher.add_handler(CommandHandler('start', self._start_callback))
        self._dispatcher.add_handler(CallbackQueryHandler(self._query_callback))
        self._dispatcher.add_handler(MessageHandler(Filters.text, self._message_callback))

    def _start_callback(self, update: Update, context, *args):
        kb = KB(self._serializer).button("Open", self.open_categories)
        self.send_message(update, context, "I'm catalog! Insert your request or open categories!", kb)

    def _query_callback(self, update: Update, context):
        callback, args = self._serializer.deserialize(update.callback_query.data)
        if callback:
            callback(update, context, *args)
        else:
            raise NotImplementedError(f"{update.callback_query.data}")

    #ToDO
    def _message_callback(self, update: Update, context):
        request = update.message.text
        result = self._catalog.find(update.message.text)
        all_products = []
        for products in result.values():
            all_products += products

        kb = self._get_products_keyboard(self.open_particular_products,
                                         all_products,
                                         0, 0, len(all_products), False, request)
        self.send_message(update, context, "Products", kb)

    def open_particular_products(self, update: Update, context,
                                 offset: int, request: str):
        offset = int(offset)
        result = self._catalog.find(request)

        all_products = []
        for products in result.values():
            all_products += products

        kb = self._get_products_keyboard(self.open_particular_products,
                                         all_products,
                                         offset, 0, len(all_products), False, request)

        self.edit_message(update, context, "Products:", kb)

    #ToDO
    def _open_product(self, update: Update, context, product_id: int, back_offset: int):
        product_id, back_offset = int(product_id), int(back_offset)
        image_path = self._catalog.get_png_path(product_id)
        desciption = self._catalog.get_description(product_id)

        if isinstance(image_path, Path):
            fp = image_path.open('rb')
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=fp, caption=desciption)
            fp.close()

        elif isinstance(image_path, int):
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                     caption="Products:",
                                     photo=image_path)

    def _open_category(self, update: Update, context, offset: int, category_id: int, back_offset: int):
        offset, category_id, back_offset = int(offset), int(category_id), int(back_offset)

        kb = self._get_products_keyboard(self._open_category, self._catalog.get(category_id, offset, IN_PAGE),
                                         offset, back_offset,
                                         len(self._catalog.get(category_id)), True,
                                         category_id, back_offset)
        self.edit_message(update, context, "Catalog:", kb)

    def open_categories(self, update: Update, context, offset: int):
        if offset is '':
            offset = 0
        else:
            offset = int(offset)
        kb = self._abs_open_categories(self._open_category, self._catalog.get_categories(offset=offset, limit=IN_PAGE),
                                       offset, max_offset=len(self._catalog.get_categories()))
        self.edit_message(update, context, "Catalog:", kb)

    def edit_message(self, update: Update, context, text: str, kb: KB):
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id,
                                      text=text,
                                      reply_markup=kb.get())

    def send_message(self, update: Update, context, text: str, kb: KB = None):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text,
                                 reply_markup=kb.get())

    def _abs_open_categories(self, func: Callable, categories: Iterable, offset: int, max_offset: int) -> KB:
        kb = KB(self._serializer)
        for category in categories:
            kb.button(category.name, func, (0, category.id, offset))

        kb.pager(self.open_categories, IN_PAGE, offset, max_offset)
        return kb

    def _get_products_keyboard(self, func: Callable,
                               products: Iterable[Product],
                               offset: int,
                               back_offset: int,
                               max_offset: int,
                               is_need_back: bool = None,
                               *args):
        is_need_back = True if is_need_back is None else False
        kb = KB(self._serializer)

        for index, product in enumerate(products):
            if index >= IN_PAGE:
                break
            kb.button(product.name, self._open_product, (product.id, back_offset))

        if is_need_back:
            pager = kb.pager(func, IN_PAGE, offset, max_offset, back_offset, *args)
        else:
            pager = kb.pager(func, IN_PAGE, offset, max_offset, *args)

        if pager is not None and is_need_back:
            pager.back(self.open_categories, back_offset)

        return kb
