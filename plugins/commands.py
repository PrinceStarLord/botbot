
import os
import logging
import random
import asyncio
import pytz
import tempfile
from Script import script
from datetime import date, datetime, timedelta
import re, asyncio, time, shutil, psutil, os, sys
from pyrogram import Client, filters, enums
from pyrogram.types import *
from datetime import datetime
from utils import humanbytes
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files, update_existing_file_captions
from database.users_chats_db import db
from btn import BUTTON
from info import CHANNELS, BOT_START_TIME, IS_VERIFY, BOT_FILES_DIRECTORY, ADMINS, AUTH_CHANNEL, AUTH_CHANNEL_2, BATCH_FILE_CAPTION, PATCH_FILE_CAPTION, VLINK, LOG_CHANNEL, VDLT, SPTGRP, VERIFY_COMPLETE_LOG, VERIFY_LOG, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, REQST_CHANNEL, SUPPORT_CHAT_ID, MAX_B_TN, IS_VERIFY, HOW_TO_VERIFY, UPDATES, GRP1, GRP2, SHARE, BOTS
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp, ansh_token, verify_user, check_token, check_verification, get_token, send_all
from database.connections_mdb import active_connection
import re
import json
import base64
import time
from .pm_filter import auto_filter
logger = logging.getLogger(__name__)

BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if "search_" in message.text:
        text = " ".join(message.text.split("_")[1:]) if "search" in message.text else message.text
        okda = await message.reply_text(f"**🔍 Searching For {text}...**")
        await asyncio.sleep(0.99)
        await okda.delete()
        print("Start text :-", message.text)
        await auto_filter(client, message)
        return
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        
        buttons = buttons = [[
                          InlineKeyboardButton('ʙᴀᴄᴋᴜᴘ ᴄʜᴀɴɴᴇʟ', url=UPDATES),
                          InlineKeyboardButton('ʙᴏᴛꜱ ᴄʜᴀɴɴᴇʟ', url=BOTS)
                       ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(2) 
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
                    InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=UPDATES)
                  ]]
        reply_markup=InlineKeyboardMarkup(buttons) #Start Buttons Here
        await message.reply_text(
            # photo=random.choice(PICS),
            text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if (AUTH_CHANNEL and not await is_subscribed(client, message)):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
            # invite_link_2 = await client.create_chat_invite_link(int(AUTH_CHANNEL_2))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return

        btn = [[
                InlineKeyboardButton("❆ Jᴏɪɴ Cʜᴀɴɴᴇʟ ❆", url=invite_link.invite_link)
            ],
            # [
            #     InlineKeyboardButton("❆ Jᴏɪɴ Cʜᴀɴɴᴇʟ 2 ❆", url=invite_link_2.invite_link)
            # ],
            [
                InlineKeyboardButton("❆ Follow On Instagram ❆", url="https://www.instagram.com/m2linksofficial")
            ]
        ]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ.\n\nIғ ʏᴏᴜ ᴡᴀɴᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ '❆ Jᴏɪɴ Oᴜʀ Bᴀᴄᴋ-Uᴘ Cʜᴀɴɴᴇʟ ❆' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀɴᴅ ᴊᴏɪɴ ᴏᴜʀ ʙᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ, ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ '↻ Tʀʏ Aɢᴀɪɴ' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ...**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
                    InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=f'http://telegram.me/{UPDATES}')
                  ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await message.reply_text(
            # photo=random.choice(PICS),
            text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "BH":
        sts = await message.reply("<b>Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("Fᴀɪʟᴇᴅ")
                return await client.send_message(LOG_CHANNEL, "Uɴᴀʙʟᴇ Tᴏ Oᴘᴇɴ Fɪʟᴇ.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                if IS_VERIFY and not await check_verification(client, message.from_user.id):
                    m = await message.reply_text("Please Wait . .")                  
                    btn = [[
                        InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                        InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
                    ]]
                    k = await message.reply_text(
                            text="<b>Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ!\nKɪɴᴅʟʏ ᴠᴇʀɪғʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ Sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴀᴄᴄᴇss ᴛᴏ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs ᴜɴᴛɪʟ 16 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ !\n\nआप verified नहीं हैं ! \nकृपया जारी रखने के लिए verify करें ताकि आप अब से 16 घंटे तक unlimited फिल्मों  प्राप्त कर सकें</b>",
                            protect_content=True if PROTECT_CONTENT else False,
                            reply_markup=InlineKeyboardMarkup(btn)
                    )
                    await sts.delete()
                    await m.delete()
                    await asyncio.sleep(VDLT)
                    await k.delete()
                    ist_timezone = pytz.timezone('Asia/Kolkata')
                    current_time = datetime.now(tz=ist_timezone)
                    VERIFY_TXT = f"""<b>User ID : `{message.from_user.id}`
Username : {message.from_user.mention}
Time : {datetime.now(tz=ist_timezone).strftime('%d-%m-%Y  ⏰: %I:%M:%S %p')}

#New_Verify_User</b>"""
                    await client.send_message(VERIFY_LOG, text=VERIFY_TXT)
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False)
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False)
                )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        return
    elif data.split("-", 1)[0] == "DS":
        sts = await message.reply("<b>Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        if IS_VERIFY and not await check_verification(client, message.from_user.id):
            m = await message.reply_text("Please Wait . .")
            
            btn = [[
                       InlineKeyboardButton("Vᴇʀɪғʏ", url=await ansh_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=")),
                       InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
            ]]
            k = await message.reply_text(
                    text="<b>Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ!\nKɪɴᴅʟʏ ᴠᴇʀɪғʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ Sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴀᴄᴄᴇss ᴛᴏ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs ᴜɴᴛɪʟ 16 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ !\n\nआप verified नहीं हैं ! \nकृपया जारी रखने के लिए verify करें ताकि आप अब से 16 घंटे तक unlimited फिल्मों  प्राप्त कर सकें</b>",
                    protect_content=True if PROTECT_CONTENT else False,              
                    reply_markup=InlineKeyboardMarkup(btn)
            )
            await sts.delete()
            await m.delete()
            await asyncio.sleep(VDLT)
            await k.delete()
            ist_timezone = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(tz=ist_timezone)
            VERIFY_TXT = f"""<b>User ID : `{message.from_user.id}`
            Username : {message.from_user.mention}
            Time : {datetime.now(tz=ist_timezone).strftime('%d-%m-%Y  ⏰: %I:%M:%S %p')}

            #New_Verify_User</b>"""
            await client.send_message(VERIFY_LOG, text=VERIFY_TXT)
            return
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:                    
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:                    
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()

    elif data.split("-", 1)[0] == "ansh":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            btn = [[
                InlineKeyboardButton('Generate Again Verify Link ✨', url=VLINK)]]            
            return await message.reply_text(
                text="<b>Invalid link or Expired link !!\n\nEnter \verify to generate verification link.</b>",
                
                protect_content=True
            )
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            await verify_user(client, userid, token)
            await message.reply_photo(
                photo='https://telegra.ph/file/dc39d7672ebb31efb8e0b.jpg',
                caption=f"<b>Hey {message.from_user.mention},</b>\n\n<b>You have completed verification ✅</b>\n\n<b>Now you have unlimited access for all movies without any ads till 16 hours \n\nEnjoy..❤️‍🔥❤️‍🔥</b>",     
            )
            ist_timezone = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(tz=ist_timezone)
            VERIFY_TXT = f"""<b>User ID : `{message.from_user.id}`
Username : {message.from_user.mention}
Time : {datetime.now(tz=ist_timezone).strftime('%d-%m-%Y  ⏰: %I:%M:%S %p')}

#New_Verifed_User_complete✨</b>"""
            await client.send_message(VERIFY_COMPLETE_LOG, text=VERIFY_TXT)
            return
            
        else:
            btn = [[
                InlineKeyboardButton('Generate Again Verify Link ✨', url=VLINK)]]            
            return await message.reply_text(
                text="<b>Invalid link or Expired link !!\n\nEnter \verify to generate verification link.</b>",
                
                protect_content=True
            )
            
    elif data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        fileid = data.split("-", 3)[3]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>Iɴᴠᴀʟɪᴅ ʟɪɴᴋ ᴏʀ Exᴘɪʀᴇᴅ ʟɪɴᴋ !</b>",
                protect_content=True if PROTECT_CONTENT else False
            )
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            if fileid == "send_all":
                btn = [[
                    InlineKeyboardButton("Gᴇᴛ Fɪʟᴇ", callback_data=f"checksub#send_all")
                ]]
                await verify_user(client, userid, token)
                await message.reply_text(
                    text=f"<b>Hᴇʏ {message.from_user.mention}, Yᴏᴜ ᴀʀᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ !\nNᴏᴡ ʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss ғᴏʀ ᴀʟʟ ᴍᴏᴠɪᴇs ᴛɪʟʟ ᴛʜᴇ ɴᴇxᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴡʜɪᴄʜ ɪs ᴀғᴛᴇʀ 16 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ.</b>",
                    protect_content=True if PROTECT_CONTENT else False,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            btn = [[
                InlineKeyboardButton("Gᴇᴛ Fɪʟᴇ", url=f"https://telegram.me/{temp.U_NAME}?start=files_{fileid}")
            ]]
            await message.reply_text(
                text=f"<b>Hᴇʏ {message.from_user.mention}, Yᴏᴜ ᴀʀᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ !\nNᴏᴡ ʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss ғᴏʀ ᴀʟʟ ᴍᴏᴠɪᴇs ᴛɪʟʟ ᴛʜᴇ ɴᴇxᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴡʜɪᴄʜ ɪs ᴀғᴛᴇʀ 16 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ.\n\n Get link - https://telegram.me/{temp.U_NAME}?start=files_{fileid}</b>",
                protect_content=True if PROTECT_CONTENT else False                
            )
            ist_timezone = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(tz=ist_timezone)
            VERIFY_TXT = f"""<b>User ID : `{message.from_user.id}`
Username : {message.from_user.mention}
Time : {datetime.now(tz=ist_timezone).strftime('%d-%m-%Y  ⏰: %I:%M:%S %p')}

#New_Verifed_User_complete</b>"""
            await client.send_message(VERIFY_COMPLETE_LOG, text=VERIFY_TXT)                         
            await verify_user(client, userid, token)
            return
        else:
            return await message.reply_text(
                text="<b>Iɴᴠᴀʟɪᴅ ʟɪɴᴋ ᴏʀ Exᴘɪʀᴇᴅ ʟɪɴᴋ !\n\nUse /verify to Create Verification Link Again !!</b>",
                protect_content=True if PROTECT_CONTENT else False
            )

    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            if IS_VERIFY and not await check_verification(client, message.from_user.id):
                m = await message.reply_text("Please Wait . .")
                
                await m.delete()
                btn = [[
                    InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                    InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
                ]]
                k = await message.reply_text(
                        text="<b>Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ!\nKɪɴᴅʟʏ ᴠᴇʀɪғʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ Sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴀᴄᴄᴇss ᴛᴏ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs ᴜɴᴛɪʟ 16 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ !\n\nआप verified नहीं हैं ! \nकृपया जारी रखने के लिए verify करें ताकि आप अब से 16 घंटे तक unlimited फिल्मों  प्राप्त कर सकें</b>",
                        protect_content=True if PROTECT_CONTENT else False,
                        reply_markup=InlineKeyboardMarkup(btn)
                )
                await m.delete()
                await asyncio.sleep(VDLT)
                await k.delete()
                ist_timezone = pytz.timezone('Asia/Kolkata')
                current_time = datetime.now(tz=ist_timezone)
                VERIFY_TXT = f"""<b>User ID : `{message.from_user.id}`
Username : {message.from_user.mention}
Time : {datetime.now(tz=ist_timezone).strftime('%d-%m-%Y  ⏰: %I:%M:%S %p')}

#New_Verify_User</b>"""
                await client.send_message(VERIFY_LOG, text=VERIFY_TXT)
                return
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False
            )
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = file.file_name
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    if IS_VERIFY and not await check_verification(client, message.from_user.id):
        m = await message.reply_text("Please Wait . .")
        
        
        btn = [[
            InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
            InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
        ]]
        k = await message.reply_text(
                text="<b>Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ!\nKɪɴᴅʟʏ ᴠᴇʀɪғʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ Sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴀᴄᴄᴇss ᴛᴏ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs ᴜɴᴛɪʟ 16 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ !\n\nआप verified नहीं हैं ! \nकृपया जारी रखने के लिए verify करें ताकि आप अब से 16 घंटे तक unlimited फिल्मों  प्राप्त कर सकें</b>",
                protect_content=True if PROTECT_CONTENT else False,
                reply_markup=InlineKeyboardMarkup(btn)
        )
        await m.delete()
        await asyncio.sleep(VDLT)
        await k.delete()
        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(tz=ist_timezone)
        VERIFY_TXT = f"""<b>User ID : `{message.from_user.id}`
Username : {message.from_user.mention}
Time : {datetime.now(tz=ist_timezone).strftime('%d-%m-%Y  ⏰: %I:%M:%S %p')}

#New_Verify_User</b>"""
        await client.send_message(VERIFY_LOG, text=VERIFY_TXT)
        return
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False
    )
                    

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Uɴᴇxᴘᴇᴄᴛᴇᴅ ᴛʏᴘᴇ ᴏғ CHANNELS")

    text = '📑 **Iɴᴅᴇxᴇᴅ ᴄʜᴀɴɴᴇʟs/ɢʀᴏᴜᴘs**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('Logs.txt')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command(['delete', 'd']) & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Pʀᴏᴄᴇssɪɴɢ...⏳", quote=True)
    else:
        await message.reply('Rᴇᴘʟʏ ᴛᴏ ғɪʟᴇ ᴡɪᴛʜ /delete ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('Tʜɪs ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟᴇ ғᴏʀᴍᴀᴛ')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
            else:
                await msg.edit('Fɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'Tʜɪs ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ɪɴᴅᴇxᴇᴅ ғɪʟᴇs.\nDᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ?',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Yᴇs", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cᴀɴᴄᴇʟ", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer("Eᴠᴇʀʏᴛʜɪɴɢ's Gᴏɴᴇ")
    await message.message.edit('Sᴜᴄᴄᴇsғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ Aʟʟ Tʜᴇ Iɴᴅᴇxᴇᴅ Fɪʟᴇs.')
        
@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "Usᴇʀs Sᴀᴠᴇᴅ Iɴ DB Aʀᴇ:\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"<b>Yᴏᴜʀ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ sᴇɴᴅ ᴛᴏ {user.mention}.</b>")
            else:
                await message.reply_text("<b>Tʜɪs ᴜsᴇʀ ᴅɪᴅɴ'ᴛ sᴛᴀʀᴛᴇᴅ ᴛʜɪs ʙᴏᴛ ʏᴇᴛ!</b>")
        except Exception as e:
            await message.reply_text(f"<b>Eʀʀᴏʀ: {e}</b>")
    else:
        await message.reply_text("<b>Usᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴜsɪɴɢ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴄʜᴀᴛ ɪᴅ. Fᴏʀ ᴇɢ: /send ᴜsᴇʀɪᴅ</b>")

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏɴ'ᴛ ᴡᴏʀᴋ ɪɴ ɢʀᴏᴜᴘs. Iᴛ ᴏɴʟʏ ᴡᴏʀᴋs ᴏɴ ᴍʏ PM!</b>")
    else:
        pass
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, Gɪᴠᴇ ᴍᴇ ᴀ ᴋᴇʏᴡᴏʀᴅ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ғɪʟᴇs.</b>")
    btn = [[
       InlineKeyboardButton("Yᴇs, Cᴏɴᴛɪɴᴜᴇ !", callback_data=f"killfilesdq#{keyword}")
       ],[
       InlineKeyboardButton("Nᴏ, Aʙᴏʀᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ !", callback_data="close_data")
    ]]
    await message.reply_text(
        text="<b>Aʀᴇ ʏᴏᴜ sᴜʀᴇ? Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ?\n\nNᴏᴛᴇ:- Tʜɪs ᴄᴏᴜʟᴅ ʙᴇ ᴀ ᴅᴇsᴛʀᴜᴄᴛɪᴠᴇ ᴀᴄᴛɪᴏɴ!</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )
    
@Client.on_message(filters.private & filters.command("verify"))
async def verify(client, message):
    anjaliansh = await message.reply_text("**Checking . .**")
    user_id = message.from_user.id
    btn = [[
        InlineKeyboardButton("Vᴇʀɪғʏ", url=await ansh_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=")),
        InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
    ]]
    ist_timezone = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz=ist_timezone) 
    VERIFY_TXT = f"""<b>User ID : `{message.from_user.id}`
Username : {message.from_user.mention}
Time : {datetime.now(tz=ist_timezone).strftime('%d-%m-%Y  ⏰: %I:%M:%S %p')}

#New_Verify_User✨</b>"""
    try:
        if not await check_verification(client, user_id) and IS_VERIFY:
            anjali = await message.reply_text(text="<b>You don't complete Verification, Please Wait...</b>")   
            await anjaliansh.delete()        
            await asyncio.sleep(3)
            sa = await client.send_message(chat_id=message.from_user.id, text="**Generating Verification Link..**")               
            await anjali.delete()                             
            await asyncio.create_task(asyncio.sleep(3))            
            await sa.delete()            
            ab = await client.send_message(chat_id=message.from_user.id,text="<b>Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ!\nKɪɴᴅʟʏ ᴠᴇʀɪғʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ Sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴀᴄᴄᴇss ᴛᴏ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs ᴜɴᴛɪʟ 16 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ !\n\nआप verified नहीं हैं ! \nकृपया जारी रखने के लिए verify करें ताकि आप अब से 16 घंटे तक unlimited फिल्मों  प्राप्त कर सकें</b>",reply_markup=InlineKeyboardMarkup(btn))
            await client.send_message(VERIFY_LOG, text=VERIFY_TXT)              
            await anjali.delete()
            await asyncio.sleep(VDLT)
            await ab.delete()
        elif await check_verification(client, user_id) and IS_VERIFY:
            await message.reply_text(text="<b>You Have Completed Verification Already ✅\n\nEnjoy Unlimited Movies/Series Until Next Verification.</b>")
            await anjaliansh.delete()
            
    except Exception as e:
        print(f"An error occurred: {e}")

@Client.on_message(filters.private & filters.command("status") & filters.user(ADMINS))          
async def stats(bot, update):
    currentTime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - BOT_START_TIME))
    total, used, free = shutil.disk_usage(".")
    total = humanbytes(total)
    used = humanbytes(used)
    free = humanbytes(free)
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    ms_g = f"""<b><u>Bot Status</b></u>

Uptime: <code>{currentTime}</code>
CPU Usage: <code>{cpu_usage}%</code>
RAM Usage: <code>{ram_usage}%</code>
Total Disk Space: <code>{total}</code>
Used Space: <code>{used} ({disk_usage}%)</code>
Free Space: <code>{free}</code> """

    msg = await bot.send_message(chat_id=update.chat.id, text="__Processing...__", parse_mode=enums.ParseMode.MARKDOWN)         
    await msg.edit_text(text=ms_g, parse_mode=enums.ParseMode.HTML)
    
@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="**🔄 Bot is Restarting ...**", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("**✅️ 𝙱ot Restarted Succesfully**")
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.command("verification") & filters.user(ADMINS))
async def verification_command_handler(client, message):
    global IS_VERIFY  # Assuming IS_VERIFY is a global variable
    IS_VERIFY = not IS_VERIFY  # Toggle IS_VERIFY (True -> False or False -> True)
    # Save the updated value to the info.py file
    with open("info.py", "a") as file:
        file.write(f"\nIS_VERIFY = {IS_VERIFY}\n")
    if IS_VERIFY:
        await message.reply("Verification turned on successfully.")
    else:
        await message.reply("Verification turned off successfully.")

@Client.on_message(filters.command("get") & filters.user(ADMINS))
async def get_file(client, message):
    if len(message.text.split()) > 1:
        file_path = message.text.split(maxsplit=1)[1].strip()
        full_file_path = os.path.join(BOT_FILES_DIRECTORY, file_path)
        
        # Check if the file exists
        if os.path.isfile(full_file_path):
            with open(full_file_path, "rb") as file:
                await client.send_document(message.chat.id, file)
        else:
            await message.reply_text("File not found.")
    else:
        await message.reply_text("Please provide the file path.")

@Client.on_message(filters.command("replace") & filters.user(ADMINS))
async def replace_file(client, message):
    if message.reply_to_message.document:
        document_id = message.reply_to_message.document.file_id
        
        download_path = await client.download_media(message.reply_to_message)
        _, file_path = message.text.split(maxsplit=1)
        file_path = file_path.strip()
        full_file_path = os.path.join(BOT_FILES_DIRECTORY, file_path)
        
        try:
            if os.path.isfile(full_file_path):
                os.replace(download_path, full_file_path)
                await message.reply_text("File replaced successfully.")
            else:
                await message.reply_text("File does not exist.")
        except Exception as e:
            await message.reply_text(f"Error replacing file: {e}")
    else:
        await message.reply_text("Please reply to a document to replace its content.")

@Client.on_message(filters.command("list") & filters.user(ADMINS))
async def list_files(client, message):
    try:
        files_list = []
        for root, dirs, files in os.walk(BOT_FILES_DIRECTORY):
            # Exclude hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                relative_file_path = os.path.relpath(os.path.join(root, file), BOT_FILES_DIRECTORY)
                # Exclude hidden files
                if not file.startswith('.'):
                    files_list.append(relative_file_path)
        
        if files_list:
            files_list.sort()
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                for file_name in files_list:
                    temp_file.write(file_name + '\n')
            
            await client.send_document(message.chat.id, temp_file.name, caption="List of files:")
            os.unlink(temp_file.name)
            
        else:
            await message.reply_text("No files found.")
    except Exception as e:
        await message.reply_text("An error occurred while processing your request.")

@Client.on_message(filters.command("uc") & filters.private)
async def update_captions_command(_, message):
    # Check if the user is authorized to use this command
    if message.from_user.id in ADMINS:
        total_files = await Media.count_documents({})  # Get the total number of files
        
        # Initialize progress message
        progress_message = await message.reply(f"Updating captions...\nProgress: 0% (0/{total_files} files processed)\nCaptions Updated: 0")

        async def progress_callback(processed_count, captions_updated):
            progress_percentage = (processed_count / total_files) * 100
            await progress_message.edit_text(
                f"Updating captions...\nProgress: {progress_percentage:.2f}% ({processed_count}/{total_files} files processed)\nCaptions Updated: {captions_updated}"
            )
        
        # Call the update_existing_file_captions function with the progress callback
        captions_updated = await update_existing_file_captions(progress_callback)
        
        # Final message after completion
        await progress_message.edit_text(
            f"File captions updated successfully!\nTotal Files Processed: {total_files}\nCaptions Updated: {captions_updated}"
        )
    else:
        await message.reply("You are not authorized to use this command.")
