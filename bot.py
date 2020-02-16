from telegram import Update

from catalog import Catalog
from service.keyboard_builder import KeyboardBuilder as KB, Serializer
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

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

    def _start_callback(self, update: Update, context):
        kb = KB(self._serializer).button("Open", self._open_categories, (0,))
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm catalog! Insert your request or open categories!",
                                 reply_markup=kb.get())

    def _query_callback(self, update: Update, context):
        callback, args = self._serializer.deserialize(update.callback_query.data)
        if callback:
            callback(update, context, *args)
        else:
            raise NotImplementedError(f"{update.callback_query.data}")

    def _message_callback(self, update: Update, context):
        pass

    def _open_product(self, update: Update, context, product_id: int, back_offset: int):
        product_id, back_offset = int(product_id), int(back_offset)
        raise NotImplementedError

    def _open_category(self, update: Update, context, offset: int, category_id: int, back_offset: int):
        offset, category_id, back_offset = int(offset), int(category_id), int(back_offset)

        kb = KB(self._serializer)

        for product in self._catalog.get(category_id, offset, in_page):
            kb.button(product.name, self._open_product, (product.id, offset, back_offset))

        kb.pager(self._open_category, in_page, offset).back(self._open_categories, back_offset)
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id,
                                      text="Catalog:",
                                      reply_markup=kb.get())

    def _open_categories(self, update: Update, context, offset: int):
        offset = int(offset)

        kb = KB(self._serializer)
        for category in self._catalog.get_categories(offset=offset, limit=in_page):
            kb.button(category.name, self._open_category, (0, category.id, offset))

        kb.pager(self._open_categories, in_page, offset)
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id,
                                      text="Catalog:",
                                      reply_markup=kb.get())

