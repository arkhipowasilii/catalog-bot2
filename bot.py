from telegram import Update
from service.keyboard_builder import KeyboardBuilder as KB, Serializer
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler

class Bot:
    def __init__(self, token):
        self._updater = Updater(token=token, use_context=True)
        self._serializer = Serializer(self)
        self._connect()

    def start(self):
        self._updater.start_polling()

    @property
    def _dispatcher(self) -> Dispatcher:
        return self._updater.dispatcher

    def _connect(self):
        self._dispatcher.add_handler(CommandHandler('start', self._start_callback))
        self._dispatcher.add_handler(CallbackQueryHandler(self._query_callback))
        self._dispatcher.add_handler(MessageHandler(self._message_callback()))

    def _start_callback(self, update: Update, context):
        kb = KB(self._serializer).button("Open", self._open_cl)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm catalog! Insert your request or open categories!",
                                 reply_markup=kb.get())

    def _query_callback(self, update: Update, context):
        pass

    def _message_callback(self, update: Update, context):
        pass

    def _open_cl(self, update, context):
        pass
