import random
import string
import sys

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import get_random_string

from apps.common.utils import eskiz_send_sms


class CacheTypes:
    forget_pass_sms_code = "forget_pass_sms_code"
    change_phone_sms_code = "change_phone_sms_code"
    auth_sms_code = "auth_sms_code"
    delete_user_sms_code = "delete_user_sms_code"


def generate_cache_key(type_, *args):
    return f"{type_}{''.join(args)}"


class MessageProvider:
    default_message = "Sizning tasdiqlash kodingiz: {}\n9kR#mN$pL2x"
    auth_code_message = (
        "Kelajak mediklari ilovasiga kirishni tasdiqlash uchun kod: {}\n9kR#mN$pL2x"
    )
    change_phone_message = "Kelajak mediklari ilovasida telefon raqamingizni o'zgartirishni tasdiqlash uchun kod: {}\n9kR#mN$pL2x"

    forget_pass_message = (
        "Kelajak mediklari ilovasida parolingizni tiklash uchun kod: {}\n9kR#mN$pL2x"
    )
    static_code = "7777"
    test_phone = "+998999999999"
    delete_user_message = "Kelajak mediklari ilovasidagi sahifangizni o'chirishni tasdiqlash uchun kod: {}\nShuni yodda tuting: Sahifangiz o'chirilsa uni tiklash imkoni mavjud emas!"  # noqa

    def __init__(self, _type):
        """
        :param _type: type of message
        code = static_code if development or test mode
        """
        self.type = _type
        self.session = get_random_string(length=16)
        self.production_mode = settings.STAGE == "production" and "test" not in sys.argv

    def generate_code(self):
        if self.production_mode:
            return "".join(random.choice(string.digits) for _ in range(4))
        return self.static_code

    def get_message(self, code):
        """
        Use this method after generate_code
        """
        if self.type == CacheTypes.auth_sms_code:
            message = self.auth_code_message
        elif self.type == CacheTypes.change_phone_sms_code:
            message = self.change_phone_message
        elif self.type == CacheTypes.forget_pass_sms_code:
            message = self.forget_pass_message
        else:
            message = self.default_message
        return message.format(code)

    async def send_sms(self, phone):
        if phone == self.test_phone:
            self.production_mode = False

        code = self.generate_code()
        message = self.get_message(code)
        if self.production_mode:
            # await send_sms(phone, message)
            await eskiz_send_sms(phone, message)

        await sync_to_async(cache.set)(
            generate_cache_key(self.type, phone, self.session), code, timeout=120
        )
