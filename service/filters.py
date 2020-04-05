from telegram.ext import BaseFilter


class MessageFilters(object):
    class _FindFilter(BaseFilter):
        name = 'MessageFilters.FindFilter'

        def filter(self, message):
            return bool(message.text
                        and not message.text.startswith('/')
                        and message.text != "cart"
                        and message.text != "home")

    find_filter = _FindFilter()

    class _MenuFilter(BaseFilter):
        name = 'MessageFilters.add'

        def filter(self, message):
            return bool(message.text and (message.text == "cart" or message.text == "home"))
    menu_filter = _MenuFilter()
