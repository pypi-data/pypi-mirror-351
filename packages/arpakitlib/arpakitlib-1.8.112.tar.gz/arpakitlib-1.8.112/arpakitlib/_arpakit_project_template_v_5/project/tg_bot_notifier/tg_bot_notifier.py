import aiogram
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from project.core.settings import get_cached_settings


def create_tg_bot_notifier() -> aiogram.Bot | None:
    if get_cached_settings().tg_bot_notifier_token is None:
        return None
    session: AiohttpSession | None = None
    if get_cached_settings().tg_bot_notifier_proxy_url:
        session = AiohttpSession(proxy=get_cached_settings().tg_bot_notifier_proxy_url)
    tg_bot = aiogram.Bot(
        token=get_cached_settings().tg_bot_notifier_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            disable_notification=False,
            link_preview_is_disabled=True
        ),
        session=session
    )
    return tg_bot
