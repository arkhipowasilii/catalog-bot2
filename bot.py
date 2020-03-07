from telegram import Update
from typing import List, Tuple, Dict, Iterable, Callable
from catalog import Catalog
from service.keyboard_builder import KeyboardBuilder as KB, Serializer
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from PIL import Image

in_page = 2

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
        kb = KB(self._serializer).button("Open", self._open_categories)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm catalog! Insert your request or open categories!",
                                 reply_markup=kb.get())

    def _query_callback(self, update: Update, context):
        callback, args, products_ids = self._serializer.deserialize(update.callback_query.data)
        if callback:
            if products_ids is None:
                callback(update, context, *args)
            else:
                callback(update, context, *args, products_ids)
        else:
            raise NotImplementedError(f"{update.callback_query.data}")

    #ToDO
    def _message_callback(self, update: Update, context):
        result = self._catalog.find(update.message.text)
        kb = KB(self._serializer)
        if len(result) == 1:
            pass
        for products in result.values():
            self.open_particular_products(update, context, products, 0, 0)

    def open_particular_products(self, update: Update, context,
                                 product_ids: Iterable[int],
                                 offset: int,
                                 back_offset: int):
        offset, back_offset = int(offset), int(back_offset)

        kb = self._abs_open_products(self.open_particular_products,
                                     self._catalog.find_products(product_ids),
                                     offset, back_offset, len(product_ids))

        self.edit_message(update, context, "Products:", kb)

    #ToDO
    def _open_product(self, update: Update, context, product_id: int, back_offset: int):
        product_id, back_offset = int(product_id), int(back_offset)
        png_path = self._catalog.get_png_path(product_id)
        if png_path:
            fp = Image.open(png_path)
            context.bot.send_photo(photo=fp)
            fp.close()
        raise NotImplementedError

    def _open_category(self, update: Update, context, offset: int, category_id: int, back_offset: int):
        offset, category_id, back_offset = int(offset), int(category_id), int(back_offset)

        kb = self._abs_open_products(self._catalog.get(category_id, offset, in_page),
                                     offset, back_offset, len(self._catalog.get(category_id)), category_id)
        self.edit_message(update, context, "Catalog:", kb)

    def _open_categories(self, update: Update, context, offset: int):
        if offset is '':
            offset = 0
        else:
            offset = int(offset)
        kb = self._abs_open_categories(self._open_categories, self._catalog.get_categories(offset=offset, limit=in_page),
                                       offset, max_offset=len(self._catalog.get_categories()))
        self.edit_message(update, context, "Catalog:", kb)

    def edit_message(self, update: Update, context, text: str, kb: KB):
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id,
                                      text=text,
                                      reply_markup=kb.get())

    def _abs_open_categories(self, categories: Iterable, offset: int, max_offset: int) -> KB:
        kb = KB(self._serializer)
        for category in categories:
            kb.button(category.name, self._open_category, (0, category.id, offset))

        kb.pager(self._open_categories, in_page, offset, max_offset)
        return kb

    def _abs_open_products(self, func: Callable, products: Iterable, offset: int, back_offset: int, max_offset: int, *args):
        kb = KB(self._serializer)

        for product in products:
            kb.button(product.name, self._open_product, (product.id, offset, back_offset))

        pager = kb.pager(func, in_page, offset, max_offset, back_offset, *args)
        if pager is not None:
            pager.back(self._open_categories, back_offset)

        return kb
