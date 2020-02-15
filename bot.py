from telegram import Update
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackQueryHandler


class Bot:
    def __init__(self, token):
        self._updater = Updater(token=token, use_context=True)

    def start(self):
        self._updater.start_polling()

    @property
    def _dispatcher(self) -> Dispatcher:
        return self._updater.dispatcher

    def _connect(self):
        self._dispatcher.add_handler(CommandHandler('start', self._start_callback))
        self._dispatcher.add_handler(CallbackQueryHandler(self._query_callback))

    def _start_callback(self, update: Update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm a bot, please talk to me!")

    def _query_callback(self, update: Update, context):
        pass