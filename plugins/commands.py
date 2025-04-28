import os
import logging
import random
import asyncio
import binascii
import json
import base64
import re

from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Script import script
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db
from info import *
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp, verify_user, check_token, check_verification, get_token, send_all
from database.connections_mdb import active_connection

logger = logging.getLogger(__name__)
BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=UPDATES)]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(2)
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))
            await db.add_chat(message.chat.id, message.chat.title)
        return

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))

    if len(message.command) != 2:
        buttons = [[InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=UPDATES)]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Mᴀᴋᴇ sᴜʀᴇ Bᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ Fᴏʀᴄᴇsᴜʙ ᴄʜᴀɴɴᴇʟ")
            return

        btn = [[InlineKeyboardButton("❆ Jᴏɪɴ Oᴜʀ Bᴀᴄᴋ-Uᴘ Cʜᴀɴɴᴇʟ ❆", url=invite_link.invite_link)]]
        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub'
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])

        await client.send_message(
            chat_id=message.from_user.id,
            text="**Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ. Pʟᴇᴀsᴇ ᴊᴏɪɴ ғɪʀsᴛ!**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return

    data = message.command[1]

    if data.startswith("DS-"):
        # Handling DSTORE links
        sts = await message.reply("<b>Please wait...</b>")
        b_string = data.split("-", 1)[1]
        try:
            decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("utf-8")
            try:
                f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
            except:
                f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
                protect = "/pbatch"
        except (binascii.Error, UnicodeDecodeError, ValueError):
            await sts.delete()
            return await message.reply_text("<b>Invalid DSTORE Link ❌</b>")

        async for msg in client.iter_messages(
            int(f_chat_id),
            min_id=int(f_msg_id)-1, 
            max_id=int(l_msg_id)
        ):

            if msg.media:
                media = getattr(msg, msg.media.value)
                f_caption = getattr(msg, 'caption', '') or ''
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption = BATCH_FILE_CAPTION.format(
                            file_name=getattr(media, 'file_name', ''),
                            file_size=getattr(media, 'file_size', ''),
                            file_caption=f_caption
                        )
                    except Exception as e:
                        logger.exception(e)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
            await asyncio.sleep(1)
        try:
            await sts.delete()
        except MessageNotModified:
            pass
        return

    if data.startswith("BATCH-"):
        # Handling BATCH links
        sts = await message.reply("<b>Please wait...</b>")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try:
                with open(file) as file_data:
                    msgs = json.loads(file_data.read())
            except:
                await sts.edit("Fᴀɪʟᴇᴅ")
                return await client.send_message(LOG_CHANNEL, "Uɴᴀʙʟᴇ Tᴏ Oᴘᴇɴ Fɪʟᴇ.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs

        for msg in msgs:
            title = msg.get("title")
            size = get_size(int(msg.get("size", 0)))
            f_caption = msg.get("caption", "") or ''
            if BATCH_FILE_CAPTION:
                try:
                    f_caption = BATCH_FILE_CAPTION.format(
                        file_name=title or '',
                        file_size=size or '',
                        file_caption=f_caption
                    )
                except Exception as e:
                    logger.exception(e)

            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False)
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False)
                )
            except Exception as e:
                logger.exception(e)
                continue
            await asyncio.sleep(1)

        try:
            await sts.delete()
        except MessageNotModified:
            pass
        return

    # Normal Single File Handling
    try:
        pre, file_id = data.split("_", 1)
    except ValueError:
        file_id = data
        pre = ""

    files_ = await get_file_details(file_id)
    if not files_:
        try:
            decoded_data = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))
            decoded_string = decoded_data.decode("utf-8")
            pre, file_id = decoded_string.split("_", 1)
        except (binascii.Error, UnicodeDecodeError, ValueError):
            return await message.reply_text("<b>Invalid Link or File not found ❌</b>")

    files = await get_file_details(file_id)
    if not files:
        return await message.reply_text("<b>Invalid or Expired File ❌</b>")

    files = files[0]
    title = files.file_name
    size = get_size(files.file_size)
    f_caption = files.caption or f"<code>{title}</code>"

    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(
                file_name=title or '',
                file_size=size or '',
                file_caption=f_caption or ''
            )
        except Exception as e:
            logger.exception(e)

    if IS_VERIFY and not await check_verification(client, message.from_user.id):
        btn = [
            [InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
            InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)],
            [InlineKeyboardButton("⭐️ Bᴜʏ Pʀᴇᴍɪᴜᴍ ⭐️", url=UPDATES)]
        ]
        return await message.reply_text(
            text="<b>Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ!</b>",
            reply_markup=InlineKeyboardMarkup(btn),
            protect_content=True if PROTECT_CONTENT else False
        )

    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False
    )

@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('Logs.txt')
    except Exception as e:
        await message.reply(str(e))

@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer("Eᴠᴇʀʏᴛʜɪɴɢ's Gᴏɴᴇ")
    await message.message.edit('Sᴜᴄᴄᴇsғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ Aʟʟ Tʜᴇ Iɴᴅᴇxᴇᴅ Fɪʟᴇs.')

