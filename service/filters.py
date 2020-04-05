from telegram.ext import BaseFilter


class MessageFilters(object):
    class _FindFilter(BaseFilter):
        name = 'MessageFilters.FindFilter'

        def filter(self, message):
            return bool(message.text and not message.text.startswith('/'))

    text = _FindFilter()

    class _MenuFilter(BaseFilter):
        name = 'MessageFilters.add'

        def filter(self, message):
            return bool(message.text and message.text.startswith('$add'))

    add = _MenuFilter()
