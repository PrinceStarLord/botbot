import re
from os import environ
from Script import script 
from time import time

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
PORT = environ.get("PORT", "8081")
SESSION = environ.get('SESSION', 'FileStoreBot')
API_ID = environ.get('API_ID',)
API_HASH = environ.get('API_HASH',)
BOT_TOKEN = environ.get('BOT_TOKEN',"")
U_NAME = "ksBot" #Bot Username Without @ Symbol
SEARCH_G = "https://t.me/+FZL0kd8e0aFjNzRl"
UPDATES = environ.get('UPDATES',"")
GRP2 = "https://t.me/+FZL0kd8jNzRl"
SPTGRP = "https://t.me/m2ity" 
GRP1 = "https://t.me/+FZL0kd8NzRl"
HOW_TO_VERIFY = environ.get('HOW_TO_VERIFY', "https://t.me/FICIAL/48")
REQST_A = "https://t.me/ommunity" #Request to admin 
UDLT = 300 #User Message Auto Delete Time In Seconds
DLT = 300 #Bot Messages Auto delete time in seconds
VDLT = 600 #Verification link delete time in Seconds
BOT_FILES_DIRECTORY = environ.get('BOT_FILES_DIRECTORY', '/home/pavan/hso-main')
BOT_START_TIME = time()
VLINK = "" #Verification link
BOTS = "https://t.me/BotFusion/15"
SHARE = "http://t.me/share/url?url=%2A%2AHey%20👋,%2A%2A%0A%2A%2ACheckout%20%2A%2A%40MovieSearch2bot%2A%2A%20for%20searching%20latest%20movies%20and%20series%20in%20multiple%20languages,%20it's%20just%20a%20awesome%20bot%20😍%2A%2A"

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = is_enabled((environ.get('USE_CAPTION_FILTER', 'True')), True)

PICS = (environ.get('PICS', 'https://envs.sh/0Ga.jpg')).split()

#VERIFY LOGS
VERIFY_COMPLETE_LOG = int(environ.get('VERIFY_COMPLETE_LOG', '-1002440494636'))
VERIFY_LOG = int(environ.get('VERIFY_LOG', '-1002440494636'))

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '6167872503').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '0').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = int(environ.get('AUTH_USERS', '6167872503'))
auth_channel = environ.get('AUTH_CHANNEL')
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = 0
AUTH_CHANNEL_2 = 0
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
support_chat_id = environ.get('SUPPORT_CHAT_ID')
reqst_channel = 0
REQST_CHANNEL = 0
SUPPORT_CHAT_ID = 0
LOG_CHANNEL = -1002440494636
NO_RESULTS_MSG = is_enabled((environ.get("NO_RESULTS_MSG", 'False')), False)

DATABASE_URI = environ.get('DATABASE_URI', "")
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Filestoresaxxii') 

# Others
IS_VERIFY = is_enabled((environ.get('IS_VERIFY', 'False')), True)
VERIFY2_URL = environ.get('VERIFY2_URL', "shortner.in")
VERIFY2_API = environ.get('VERIFY2_API', "76a41243931b44946d6b2df3")
SHORTLINK_URL = environ.get('SHORTLINK_URL', VERIFY2_URL)
SHORTLINK_API = environ.get('SHORTLINK_API', VERIFY2_API)
IS_SHORTLINK = is_enabled((environ.get('IS_SHORTLINK', 'False')), False)
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '0').split()]
MAX_B_TN = environ.get("MAX_B_TN", "5")
MAX_BTN = is_enabled((environ.get('MAX_BTN', "True")), True)
MSG_ALRT = environ.get('MSG_ALRT', 'Wʜᴀᴛ Aʀᴇ Yᴏᴜ Lᴏᴏᴋɪɴɢ Aᴛ ?')
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'm2linkscommunity')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "True")), True)
IMDB = is_enabled((environ.get('IMDB', "False")), False)
AUTO_FFILTER = is_enabled((environ.get('AUTO_FFILTER', "False")), True)
AUTO_DELETE = is_enabled((environ.get('AUTO_DELETE', "False")), False)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "False")), True)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
PATCH_FILE_CAPTION = environ.get("PATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "False"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '-1002440494636')).split()]
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), False)
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "False")), False)

LOG_STR = "Current Cusomized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as different buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"

SPELL_WORDS = ["baahubali", "Dilpreet Dhillon Feat. Gurlej Akhtar", "(", ")", "457", "Review", "spoilers", "Special", "BFH", "Bonus 5", "Part 1", "Part 2", "Movies and Specials to Stream", "Season 1", "Horror Movie", "IT and the Upside Down of Nostalgia", "?", "None", ":", "'", ",", "episode", "Episode", "Movie Review", "Ms. Marvel Trailer, X Horror Movie Review - Episode 93"]
REMOVE_WORDS = ['R∆G∆ ','join', 'us', 'https', 'http', 't', 'me', 'from', 'telegram', 'm2links', 'm',"m2links", "join us", "Join Us","t.me", "http","https", "mkvcinemas","movies","moviesmod","moviesflix","Desiremovies","mkvc", "join", "cinevood", "@m2links", "skymovieshd"]
