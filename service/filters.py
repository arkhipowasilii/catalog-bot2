from telegram.ext import BaseFilter


class MessageFilters(object):
    class _FindFilter(BaseFilter):
        name = 'MessageFilters.FindFilter'

        def filter(self, message):
            return bool(message.text
                        and not message.text.startswith('/')
                        and message.text != "cart"
                        and message.text != "home"
                        and message.text != "checkout"
                        and not message.text.startswith("+"))

    find_filter = _FindFilter()

    class _MenuFilter(BaseFilter):
        name = 'MessageFilters.MenuFilter'

        def filter(self, message):
            return bool(message.text
                        and (message.text == "cart" or message.text == "home" or message.text == "checkout")
                        and not message.text.startswith("+"))
    menu_filter = _MenuFilter()

    class _PhoneFilter(BaseFilter):
        name = 'MessageFilters.PhoneFilter'

        def filter(self, message):
            return bool(message.text and message.text.startswith("+"))

    phone_filter = _PhoneFilter()
