import gettext
import json
import locale
import os
import re
import shutil
import sys
import tempfile

import pinyin
import polib
import zhon.cedict as chinese_characters


# All resources in development mode are relative to `src` folder
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        full_path = os.path.join(sys._MEIPASS, relative_path)
    else:
        full_path = os.path.join(os.path.dirname(__file__), '..', relative_path)

    if not os.path.exists(full_path):
        resource_name = os.path.basename(relative_path)
        formatted_message = tr("Couldn't find {missing_resource}. Please try reinstalling the application.").format(missing_resource=resource_name)
        raise FileNotFoundError(formatted_message)

    return full_path


def apply_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)


def load_settings():
    locale.setlocale(locale.LC_ALL, '')
    system_locale = locale.getlocale()[0]
    locale_mapping = {
        "English_United States": "English",
        "Chinese (Simplified)_China": "简体中文",
        "Chinese (Simplified)_Hong Kong SAR": "简体中文",
        "Chinese (Simplified)_Macao SAR": "简体中文",
        "Chinese (Simplified)_Singapore": "简体中文",
        "Chinese (Traditional)_Hong Kong SAR": "繁体中文",
        "Chinese (Traditional)_Macao SAR": "繁体中文",
        "Chinese (Traditional)_Taiwan": "繁体中文"
    }
    app_locale = locale_mapping.get(system_locale, 'English')

    default_settings = {
        "downloadPath": os.path.join(os.environ["APPDATA"], "GCM Trainers"),
        "language": app_locale,
        "theme": "black",
        "enSearchResults": False,
        "checkAppUpdate": True,
        "launchAppOnStartup": False,
        "showWarning": True,
        "autoUpdateTranslations": True,

        # Trainer management configs
        "flingDownloadServer": "intl",
        "removeFlingBgMusic": True,
        "autoUpdateFlingData": True,
        "autoUpdateFlingTrainers": True,
        "enableXiaoXing": True,
        "autoUpdateXiaoXingData": True,
        "weModPath": wemod_install_path,
        "cePath": ce_install_path
    }

    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
    except Exception as e:
        print("Error loading settings json" + str(e))
        settings = default_settings

    for key, value in default_settings.items():
        settings.setdefault(key, value)

    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

    return settings


def get_translator():
    """获取翻译器"""
    lang = settings["language"]
    if lang == "简体中文":
        lang = "zh_CN"
    elif lang == "繁体中文":
        lang = "zh_TW"
    else:
        lang = "en_US"

    try:
        # 尝试加载翻译文件
        lang_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale")
        if not os.path.exists(lang_path):
            # 如果翻译目录不存在，创建它
            os.makedirs(lang_path)
            return lambda x: x  # 返回一个简单的函数，直接返回输入的字符串
            
        lang = gettext.translation(
            "Game Cheats Manager", 
            lang_path,
            languages=[lang],
            fallback=True  # 如果找不到翻译文件，使用原始字符串
        )
        return lang.gettext
    except Exception as e:
        print(f"加载翻译文件时出错: {str(e)}")
        return lambda x: x  # 出错时返回一个简单的函数，直接返回输入的字符串


def is_chinese(text):
    for char in text:
        if char in chinese_characters.all:
            return True
    return False


def sort_trainers_key(name):
    if is_chinese(name):
        return pinyin.get(name, format="strip", delimiter=" ")
    return name


def ensure_trainer_details_exist():
    dst = os.path.join(DATABASE_PATH, "xgqdetail.json")
    if not os.path.exists(dst):
        shutil.copyfile(resource_path("dependency/xgqdetail.json"), dst)


def ensure_trainer_download_path_is_valid():
    try:
        os.makedirs(settings["downloadPath"], exist_ok=True)
    except Exception:
        settings["downloadPath"] = os.path.join(os.environ["APPDATA"], "GCM Trainers")
        apply_settings(settings)
        os.makedirs(settings["downloadPath"], exist_ok=True)


def findCEInstallPath():
    base_path = r'C:\Program Files'
    latest_version = []
    latest_path = ""

    if os.path.exists(base_path):
        for folder in os.listdir(base_path):
            if folder.startswith("Cheat Engine"):
                match = re.search(r"Cheat Engine (\d+(?:\.\d+)*)", folder)
                if match:
                    # Parse version into a list of integers (e.g., '7.5.1' -> [7, 5, 1])
                    version = list(map(int, match.group(1).split('.')))
                    while len(version) < 3:
                        version.append(0)
                    if version > latest_version:
                        latest_version = version
                        latest_path = os.path.join(base_path, folder)

    return latest_path


setting_path = os.path.join(os.environ["APPDATA"], "GCM Settings")
os.makedirs(setting_path, exist_ok=True)

SETTINGS_FILE = os.path.join(setting_path, "settings.json")
DATABASE_PATH = os.path.join(setting_path, "db")
os.makedirs(DATABASE_PATH, exist_ok=True)
DOWNLOAD_TEMP_DIR = os.path.join(tempfile.gettempdir(), "GameCheatsManagerTemp", "download")
VERSION_TEMP_DIR = os.path.join(tempfile.gettempdir(), "GameCheatsManagerTemp", "version")
WEMOD_TEMP_DIR = os.path.join(tempfile.gettempdir(), "GameCheatsManagerTemp", "wemod")

wemod_install_path = os.path.join(os.environ["LOCALAPPDATA"], "WeMod")
ce_install_path = findCEInstallPath()

settings = load_settings()
tr = get_translator()

ensure_trainer_details_exist()
ensure_trainer_download_path_is_valid()

if settings["theme"] == "black":
    dropDownArrow_path = resource_path("assets/dropdown-white.png").replace("\\", "/")
elif settings["theme"] == "white":
    dropDownArrow_path = resource_path("assets/dropdown-black.png").replace("\\", "/")
checkMark_path = resource_path("assets/check-mark.png").replace("\\", "/")
upArrow_path = resource_path("assets/up.png").replace("\\", "/")
downArrow_path = resource_path("assets/down.png").replace("\\", "/")
leftArrow_path = resource_path("assets/left.png").replace("\\", "/")
rightArrow_path = resource_path("assets/right.png").replace("\\", "/")
resourceHacker_path = resource_path("dependency/ResourceHacker.exe")
unzip_path = resource_path("dependency/7z/7z.exe")
binmay_path = resource_path("dependency/binmay.exe")
emptyMidi_path = resource_path("dependency/TrainerBGM.mid")
elevator_path = resource_path("dependency/Elevate.exe")
search_path = resource_path("assets/search.png")

language_options = {
    "English": "English",
    "简体中文": "简体中文",
    "繁体中文": "繁体中文"
}

theme_options = {
    tr("黑色"): "black",
    tr("白色"): "white"
}

server_options = {
    tr("国际"): "intl",
    tr("中国") + tr(" (部分修改器无法下载)"): "china"
}

font_config = {
    "English": resource_path("assets/NotoSans-Regular.ttf"),
    "简体中文": resource_path("assets/NotoSansSC-Regular.ttf"),
    "繁体中文": resource_path("assets/NotoSansTC-Regular.ttf")
}
