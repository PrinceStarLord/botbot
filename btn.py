from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

class BUTTON(object):
    START_BUTTONS = InlineKeyboardMarkup(
       [[
        InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕', url=f"http://t.me/{U_NAME}?startgroup=true")
        ],[
        InlineKeyboardButton('ʙᴀᴄᴋᴜᴘ ᴄʜᴀɴɴᴇʟ', url=f'http://telegram.me/{UPDATES}'),
        InlineKeyboardButton('ʙᴏᴛꜱ ᴄʜᴀɴɴᴇʟ', url=BOTS)
        ],[
        InlineKeyboardButton('ᴍᴏᴠɪᴇꜱ ɢʀᴏᴜᴘ 1', url=GRP1),
        InlineKeyboardButton('ᴍᴏᴠɪᴇꜱ ɢʀᴏᴜᴘ 2', url=GRP2)
        ],[
        InlineKeyboardButton('ꜱʜᴀʀᴇ ᴍᴇ',url=SHARE)
        ]])
   
    FILES_BUTTONS = InlineKeyboardMarkup(
        [
        InlineKeyboardButton('Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ', url=UPDATES),
        InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=SPTGRP)
        ])


