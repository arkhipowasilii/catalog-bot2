from telegram import Update
from typing import List, Tuple, Dict, Iterable, Callable, Union, Any
from catalog import Catalog, Product
from service.keyboard_builder import KeyboardBuilder as KB, Serializer, MenuBuilder
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineQueryResultCachedPhoto
from telegram.files.inputmedia import InputMediaPhoto
from PIL import Image
from pathlib import Path
from time import sleep

IN_PAGE = 2
main_image_path = Path(r"/Users/arkhipowasilii/PycharmProjects/catalog-bot2/resources/png/-1.png")


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
        menu = MenuBuilder(self._serializer)
        menu.button(text="cart", callback=self.get_basket_start)
        #self.send_message_photo(update, context, "hi", menu)
        self.send_message(update, context, "I'm catalog! Insert your request or open categories!:", kb)

    def _query_callback(self, update: Update, context):
        callback, args = self._serializer.deserialize(update.callback_query.data)
        if callback:
            callback(update, context, *args)
        else:
            raise NotImplementedError(f"{update.callback_query.data}")

    #ToDO
    def _message_callback(self, update: Update, context):
        request = update.message.text
        all_products_count, result = self._catalog.find(update.message.text, 0, IN_PAGE)
        all_products = []
        for products in result.values():
            all_products += products

        kb = self._get_products_keyboard(self.open_particular_products,
                                         all_products,
                                         0, 0, all_products_count, False, request)
        self.send_message(update, context, "Products", kb)

    def open_particular_products(self, update: Update, context,
                                 offset: int, request: str):
        offset = int(offset)
        all_products_count, result = self._catalog.find(request, offset, IN_PAGE)

        all_products = []
        for products in result.values():
            all_products += products

        kb = self._get_products_keyboard(self.open_particular_products,
                                         all_products,
                                         offset,
                                         0,
                                         all_products_count,
                                         False,
                                         request)

        self.edit_message(update, context, "Products:", kb)

    def open_product(self, update: Update, context, product_id: int, back_offset: int):
        product_id, back_offset = int(product_id), int(back_offset)
        image_path = self._catalog.get_png_path(product_id)
        desciption = self._catalog.get_description(product_id)

        kb = KB(self._serializer)
        kb.button("add to basket", self.add_to_basket, [product_id])
        if isinstance(image_path, Path):
            photo = image_path.open('rb')

            msg = self.send_message_photo(update=update, context=context, photo=photo, kb=kb, caption=desciption)
            photo_id = msg.photo[-1].file_id
            self._catalog.update_photo_id(photo_id, product_id)

            photo.close()

        elif isinstance(image_path, str):
            self.send_message_photo(update=update, context=context, caption=desciption, kb=kb, photo=image_path)

    def add_to_basket(self, update, context, product_id: int):
        product_id = int(product_id)
        self._catalog.insert_into_basket(update._effective_user.id, product_id, 1)
        if len(update._effective_message.reply_markup['inline_keyboard']) == 1:
            kb = KB(self._serializer)
            kb.button("add to cart", self.add_to_basket, [product_id]).line().button("go to cart", self.get_basket_start)
            self.edit_message_reply_markup(update, context, kb)

    def get_basket_start(self, update: Update, context, *args):
        max_offset, product_data = self._catalog.get_basket(update._effective_user.id, 0, 1)
        kb = KB(self._serializer)
        kb.button("delete", self.delete_products_from_cart, (0,)).\
            pager(callback=self.get_basket, in_page=1, current_offset=0, max_offset=max_offset)
        self.send_message_photo(update=update,
                                context=context,
                                photo=product_data[2],
                                caption=f"Product: {product_data[1]}, quantity: {product_data[0]}",
                                kb=kb)

    def get_basket(self, update, context, offset: int):
        offset = int(offset)
        max_offset, product_data = self._catalog.get_basket(update._effective_user.id, offset, 1)
        kb = KB(self._serializer)
        kb.button("delete", self.delete_products_from_cart, (offset,)). \
            pager(callback=self.get_basket, in_page=1, current_offset=offset, max_offset=max_offset)
        input_media_photo = InputMediaPhoto(media=product_data[2],
                                            caption=f"Product: {product_data[1]}, quantity: {product_data[0]}")
        self.edit_message_photo(update=update, context=context, photo=input_media_photo)
        self.edit_message_reply_markup(update=update, context=context, kb=kb)

    def delete_products_from_cart(self, update, context, offset: int,  product_id):
        self._catalog.delete_product_from_basket(update._effective_user.id, product_id)
        self.get_basket(update, context, offset - 1)

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
        context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                      message_id=update.effective_message.message_id,
                                      text=text,
                                      reply_markup=kb.get())

    def send_message(self, update: Update, context, text: str, kb: KB = None):
        return context.bot.send_message(chat_id=update.effective_chat.id,
                                        text=text,
                                        reply_markup=kb.get())

    def send_message_photo(self, update: Update, context, caption: str, kb: KB = None, photo: Union[Path, str] = None):
        return context.bot.send_photo(chat_id=update.effective_chat.id,
                                      photo=photo,
                                      caption=caption,
                                      reply_markup=kb.get())

    def edit_message_photo(self, update: Update, context, photo: InputMediaPhoto):
        context.bot.edit_message_media(chat_id=update.effective_chat.id,
                                       media=photo,
                                       message_id=update.effective_message.message_id)

    def edit_message_reply_markup(self, update: Update, context, kb: KB):
        return context.bot.edit_message_reply_markup(chat_id=update.effective_chat.id,
                                                     message_id=update.effective_message.message_id,
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
            kb.button(product.name, self.open_product, (product.id, back_offset))

        if is_need_back:
            pager = kb.pager(func, IN_PAGE, offset, max_offset, back_offset, *args)
        else:
            pager = kb.pager(func, IN_PAGE, offset, max_offset, *args)

        if pager is not None and is_need_back:
            pager.back(self.open_categories, back_offset)

        return kb

    @staticmethod
    def open_main_photo() -> Union[str, Any]:
        if isinstance(main_image_path, Path):
            return main_image_path.open('rb')
        elif isinstance(main_image_path, str):
            return main_image_path
