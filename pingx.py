# meta developer: @SenkoSanModules
# meta name: PingX
# meta description: Проверка пинга и аптайма с настраиваемым текстом через конфиг

from .. import loader, utils
import time
import datetime

@loader.tds
class PingXMod(loader.Module):
    """Проверка пинга с кастомным текстом через конфиг"""
    strings = {"name": "PingX"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            "CUSTOM_TEXT", 
            (
                "{owner_block}\n"
                "<blockquote>🌩️ <b><i>𝚜𝚢𝚗𝚝𝚑𝚎𝚝𝚒𝚌 𝚛𝚎𝚏𝚕𝚎𝚌𝚝𝚒𝚘𝚗:</i></b> <code>{ping}</code> 𝚖𝚜</blockquote>\n"
                "<blockquote>🧿 <b><i>𝚘𝚙𝚎𝚗 𝚎𝚢𝚎 𝚊𝚌𝚝𝚒𝚟𝚎 𝚜𝚒𝚗𝚌𝚎:</i></b> <code>{uptime}</code></blockquote>\n"
                "<blockquote>🌌 <b><i>𝚕𝚒𝚗𝚔 𝚝𝚘 𝚖𝚊𝚝𝚛𝚒𝚡 𝚌𝚘𝚗𝚏𝚒𝚛𝚖𝚎𝚍.</i></b></blockquote>"
            ),
            "Шаблон текста для пинга (доступные переменные: {owner_block}, {ping}, {uptime})"
        )
        self._start_time = time.time()

    async def pinxcmd(self, message):
        """Проверить пинг (текст настраивается в .cfg PingX)"""
        start = time.time()
        m = await utils.answer(message, "⏳ Пинг...")
        ping = round((time.time() - start) * 1000)
        uptime = str(datetime.timedelta(seconds=int(time.time() - self._start_time)))

        me = await message.client.get_me()
        owner_block = f'<blockquote><a href="https://t.me/{me.username}">{me.first_name}</a></blockquote>'

        text = self.config["CUSTOM_TEXT"].format(
            owner_block=owner_block,
            ping=ping,
            uptime=uptime
        )

        await utils.answer(m, text)