import os
import sys
import webbrowser
from pathlib import Path

from truffle.common import get_logger

logger = get_logger()

APP_FILES = ["manifest.json", "requirements.txt", "main.py", "icon.png"]
BANNED_REQS = ["truffle", "grpcio", "protobuf"]

def get_client_userdata_dir() -> Path:
    if sys.platform == "win32": base = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    elif sys.platform == "darwin": base = os.path.expanduser("~/Library/Application Support")
    else: base = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

    CLIENT_DIR_NAME = "TruffleOS-Development" if os.getenv("TRUFFLE_DEV") else "TruffleOS"
    userdata = Path(os.path.join(base, CLIENT_DIR_NAME))
    if not userdata.exists():
        logger.error(f"User data directory {userdata} does not exist")
        logger.error("Please make sure you have Truffle OS installed")
        logger.info("Opening download link... (https://itsalltruffles.com/)")
        webbrowser.open("https://itsalltruffles.com/", new=0, autoraise=True)
        exit(1)
    if not userdata.is_dir(): raise ValueError(f"User data directory {userdata} is not a directory")
    return userdata


def get_user_id() -> str:
    if os.getenv("TRUFFLE_CLIENT_ID"):
        return os.getenv("TRUFFLE_CLIENT_ID")
    try:
        userdata = get_client_userdata_dir()
        user_id_path = userdata / "magic-number.txt"
        if not user_id_path.exists():
            raise ValueError(f"Magic Number file @{user_id_path} does not exist")
        with open(user_id_path, 'r') as f:
            user_id = f.read().strip()
        if not user_id or len(user_id) < 6:
            raise ValueError(f"Magic Number file @{user_id_path} is empty/too short {len(user_id)}")
        
        if not user_id.isdigit():
            raise ValueError(f"Magic Number file @{user_id_path} is not a number")
        if user_id == "1234567891":
            raise ValueError(f"Magic Number file @{user_id_path} is the placeholder number")
        return user_id
    except Exception as e:
        logger.error(f"Error getting user ID: {e}")
        raise


def get_base_url() -> str:
    if os.getenv("TRUFFLE_DEV"): return "https://forecast.itsalltruffles.com:2087" 
    url = "https://overcast.itsalltruffles.com:2087"
    try:
       path = get_client_userdata_dir()
       url_file = path / "current-url"
       if url_file.exists():
            with open(url_file, "r") as f:
                url_file_contents = f.read().strip()
                if url_file_contents:
                    url = url_file_contents
                    logger.debug(f"Using URL from file: {url}")
    except Exception as e:
        logger.error(f"Error getting base URL fron client: {str(e)}")
    logger.debug(f"Using URL-  {url}")
    return url