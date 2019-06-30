import configparser, json, os, shutil, sqlite3
import xml.etree.cElementTree as ElementTree

COMPANY = "NWFB"

APP_VERSION = ""
DOWNLOAD_PATH = ""
RESULT_PATH = ""
UPLOAD_PATH = ""

def get_config() -> bool:
    # Get Config from config.ini
    config = configparser.ConfigParser()
    config.read("config.ini")

    global APP_VERSION
    APP_VERSION = config[COMPANY]["APP_VERSION"]
    if not APP_VERSION:
        print("Invalid APP_VERSION: {}".format(APP_VERSION))
        return False

    global DOWNLOAD_PATH
    DOWNLOAD_PATH = config[COMPANY]["DOWNLOAD_PATH"]
    if not DOWNLOAD_PATH:
        print("Invalid DOWNLOAD_PATH: {}".format(DOWNLOAD_PATH))
        return False

    global RESULT_PATH
    RESULT_PATH = config[COMPANY]["RESULT_PATH"]
    if not RESULT_PATH:
        print("Invalid RESULT_PATH: {}".format(RESULT_PATH))
        return False

    global UPLOAD_PATH
    UPLOAD_PATH = config[COMPANY]["UPLOAD_PATH"]
    if not UPLOAD_PATH:
        print("Invalid UPLOAD_PATH: {}".format(UPLOAD_PATH))
        return False

    return True


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def main():
    t = ""
    with open("{}t.txt".format(DOWNLOAD_PATH), "r") as f:
        t = f.read()

    # Reset result
    if os.path.exists(RESULT_PATH):
        shutil.rmtree(RESULT_PATH)
    os.makedirs(RESULT_PATH)

    # Export the result
    metadata = { "timestamp": t }

    with open("{}metadata.json".format(RESULT_PATH), "w", encoding="utf8") as f:
        f.write(json.dumps(metadata, ensure_ascii=False))

    copytree(DOWNLOAD_PATH, RESULT_PATH)
    os.remove("{}t.txt".format(RESULT_PATH))

    # Zip the result
    shutil.make_archive(RESULT_PATH[:-1], 'zip', RESULT_PATH)
    os.rename("{}.zip".format(RESULT_PATH[:-1]), "{}nwfb.zip".format(UPLOAD_PATH))

    print("-------------------")
    print("Convert Result:")
    print("timestamp = ", t)
    print("-------------------")


if __name__ == "__main__":
    if get_config():
        main()
