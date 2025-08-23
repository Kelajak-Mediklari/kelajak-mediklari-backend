import httpx
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext as _
from httpx import ConnectTimeout
from rest_framework.exceptions import ValidationError


async def send_sms(phone, message):
    sn = "8687"
    if phone[4:6] in ["99", "77", "95", "20", "90", "91", "50", "93", "94", "88", "97"]:
        sn = "8687"
    elif phone[4:6] in ["98", "33"]:
        sn = "6500"

    async with httpx.AsyncClient() as client:
        try:
            await client.get(
                settings.SMS_URL,
                params={"sn": sn, "msisdn": phone[1:], "message": message},
                timeout=5,
            )
        except ConnectTimeout:
            raise ValidationError(
                detail={"sms_provider": _("Can not connect to sms provider.")},
                code="connection_error",
            )
        except Exception as e:  # noqa
            raise ValidationError(
                detail={"sms_provider": _("Something went wrong with sms provider.")},
                code="error",
            )


async def get_eskiz_token():
    if cache.get("eskiz_auth_token"):
        return cache.get("eskiz_auth_token")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.ESKIZ_SMS_LOGIN_URL,
                data={
                    "email": settings.ESKIZ_SMS_LOGIN,
                    "password": settings.ESKIZ_SMS_SECRET_KEY,
                },
                timeout=5,
            )
        except ConnectTimeout:
            raise ValidationError(
                detail={
                    "sms_provider": _(
                        "Can not connect to sms provider while getting token"
                    )
                },
                code="connection_error",
            )
        except Exception as e:  # noqa
            raise ValidationError(
                detail={
                    "sms_provider": _(
                        "Something went wrong with sms provider while getting token"
                    )
                },
                code="error",
            )
    if response.status_code == 200:
        token = response.json()["data"]["token"]
        cache.set("eskiz_auth_token", token, timeout=3600)
        return token
    else:
        raise ValidationError(
            detail={
                "sms_provider": _("Bad response from sms provider while getting token")
            },
            code="error",
        )


async def eskiz_send_sms(phone, message):
    nickname = "4546"
    token = await get_eskiz_token()
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                settings.ESKIZ_SMS_SEND_URL,
                data={"from": nickname, "mobile_phone": phone[1:], "message": message},
                headers=headers,
                timeout=5,
            )
        except ConnectTimeout:
            raise ValidationError(
                detail={"sms_provider": _("Can not connect to sms provider.")},
                code="connection_error",
            )
        except Exception as e:  # noqa
            raise ValidationError(
                detail={"sms_provider": _("Something went wrong with sms provider.")},
                code="error",
            )
