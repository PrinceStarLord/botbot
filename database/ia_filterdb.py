import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, USE_CAPTION_FILTER, MAX_B_TN, REMOVE_WORDS
from utils import get_settings, save_group_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME

def convert_to_bold(text):
    text = re.sub(r'<i>(.*?)</i>', r'\1', text)
    text = re.sub(r'<code>(.*?)</code>', r'\1', text)
    text = re.sub(r'<spoiler>(.*?)</spoiler>', r'\1', text)
    text = re.sub(r'<s>(.*?)</s>', r'\1', text)
    text = re.sub(r'<b>(.*?)</b>', r'\1', text)
    text = f'<b>{text}</b>'
    text = re.sub(r'\b[iImMbB]\b', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = ' '.join(text.split())
    return text

def remove_emoji(text):
    emoji_pattern = re.compile(
        '['
        '\U0001F600-\U0001F64F'  # emoticons
        '\U0001F300-\U0001F5FF'  # symbols & pictographs
        '\U0001F680-\U0001F6FF'  # transport & map symbols
        '\U0001F700-\U0001F77F'  # alchemical symbols
        '\U0001F780-\U0001F7FF'  # Geometric Shapes Extended
        '\U0001F800-\U0001F8FF'  # Supplemental Arrows-C
        '\U0001F900-\U0001F9FF'  # Supplemental Symbols and Pictographs
        '\U0001FA00-\U0001FA6F'  # Chess Symbols
        '\U0001FA70-\U0001FAFF'  # Symbols and Pictographs Extended-A
        '\U00002702-\U000027B0'  # Dingbats
        '\U000024C2-\U0001F251'  # Enclosed Characters
        ']+',
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)         

async def get_search_results(chat_id, query, file_type=None, max_results=8, offset=0, filter=False):
    if chat_id is not None:
        settings = await get_settings(int(chat_id))
        try:
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
        except KeyError:
            await save_group_settings(int(chat_id), 'max_btn', False)
            settings = await get_settings(int(chat_id))
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)
    next_offset = offset + max_results

    if next_offset > total_results:
        next_offset = ''

    cursor = Media.find(filter)
    cursor.sort('$natural', -1)
    cursor.skip(offset).limit(max_results)
    files = await cursor.to_list(length=max_results)

    return files, next_offset, total_results

async def get_bad_files(query, file_type=None, filter=False):
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)

    cursor = Media.find(filter)
    cursor.sort('$natural', -1)
    files = await cursor.to_list(length=total_results)

    return files, total_results

async def get_file_details(query):
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref

async def save_file(media):
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    try:
        caption = media.caption.html if media.caption else None
        if caption:
            # Convert text formatting to bold
            caption = convert_to_bold(caption)
            
            # Remove HTML tags and clean caption
            caption = re.sub(r'<b>(.*?)</b>', r'\1', caption)
            
            # Remove emojis
            caption = remove_emoji(caption)
            
            # Remove URLs
            caption = re.sub(r'http[s]?://\S+', '', caption)
            
            # Replace periods with blank spaces
            caption = caption.replace('.', ' ')
            caption = caption.replace('_', ' ')
            
            # Remove special characters except for spaces, underscores, and hyphens
            caption = re.sub(r'[^\w\s_-]', ' ', caption)
            
            # Check for ESub, MSub, .mkv, .mp4 or new line
            match = re.search(r'(ESub|MSub|\.mkv|\.mp4|\n)', caption, re.IGNORECASE)
            if match:
                if match.group() in ['ESub', 'MSub']:
                    # Keep ESub or MSub, but remove all text after it
                    caption = caption[:match.end()]
                else:
                    # Remove all text after .mkv, .mp4, or newline
                    caption = caption[:match.start()]
            
            # Remove '.mkv' and '.mp4' if they are still present in the caption
            caption = re.sub(r'\b(mkv|mp4)\b', '', caption, flags=re.IGNORECASE)
            
            # Clean up extra spaces and filter words
            caption = ' '.join(word for word in caption.split() if word.lower() not in REMOVE_WORDS)
            caption = caption.strip()
        
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=caption,
        )
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
        return False, 2
    else:
        try:
            await file.commit()
        except DuplicateKeyError:      
            logger.warning(
                f'{getattr(media, "file_name", "NO_FILE")} is already saved in database'
            )
            return False, 0
        else:
            logger.info(f'{getattr(media, "file_name", "NO_FILE")} is saved to database')
            return True, 1

async def update_existing_file_captions(progress_callback):
    cursor = Media.find({})
    processed_count = 0
    captions_updated = 0

    async for document in cursor:
        processed_count += 1

        if document.caption:
            # Convert text formatting to bold
            updated_caption = convert_to_bold(document.caption)
            
            # Remove emojis
            updated_caption = remove_emoji(updated_caption)
            
            # Remove URLs
            updated_caption = re.sub(r'http[s]?://\S+', '', updated_caption)
            
            # Replace periods with blank spaces
            updated_caption = updated_caption.replace('.', ' ')
            updated_caption = updated_caption.replace('_', ' ')
            
            # Remove special characters except for spaces, underscores, and hyphens
            updated_caption = re.sub(r'[^\w\s_-]', ' ', updated_caption)
            
            # Check for ESub, MSub, .mkv, .mp4, or new line
            match = re.search(r'(ESub|MSub|\.mkv|\.mp4|\n)', updated_caption, re.IGNORECASE)
            if match:
                if match.group() in ['ESub', 'MSub']:
                    # Keep ESub or MSub, but remove all text after it
                    updated_caption = updated_caption[:match.end()]
                else:
                    # Remove all text after .mkv, .mp4, or newline
                    updated_caption = updated_caption[:match.start()]
            
            # Remove '.mkv' and '.mp4' if they are still present in the caption
            updated_caption = re.sub(r'\b(mkv|mp4)\b', '', updated_caption, flags=re.IGNORECASE)
            
            # Clean up extra spaces and filter words
            updated_caption = ' '.join(word for word in updated_caption.split() if word.lower() not in REMOVE_WORDS)
            updated_caption = updated_caption.strip()
            
            if updated_caption != document.caption:
                document.caption = updated_caption
                await document.commit()
                captions_updated += 1

        if processed_count % 1000 == 0:
            await progress_callback(processed_count, captions_updated)

    # Final progress update after all documents are processed
    await progress_callback(processed_count, captions_updated)
    
    return captions_updated

