import configparser, json, os, shutil, sqlite3, sys, time, urllib.request, zipfile
import xml.etree.cElementTree as ElementTree

COMPANY = "KMB"

APP_VERSION = ""
LAST_UPDATE = ""
DOWNLOAD_URL = ""
DOWNLOAD_PATH = ""
DATA_PATH = ""

def get_config() -> bool:
    # Get Config from config.ini
    config = configparser.ConfigParser()
    config.read("config.ini")

    global APP_VERSION
    APP_VERSION = config[COMPANY]["APP_VERSION"]
    if not APP_VERSION:
        print("Invalid APP_VERSION: {}".format(APP_VERSION))
        return False

    global LAST_UPDATE
    LAST_UPDATE = config[COMPANY]["LAST_UPDATE"]
    if not LAST_UPDATE:
        print("Empty LAST_UPDATE")

    global DOWNLOAD_URL
    DOWNLOAD_URL = config[COMPANY]["DOWNLOAD_URL"]
    if not DOWNLOAD_URL:
        print("Invalid DOWNLOAD_URL: {}".format(DOWNLOAD_URL))
        return False

    global DOWNLOAD_PATH
    DOWNLOAD_PATH = config[COMPANY]["DOWNLOAD_PATH"]
    if not DOWNLOAD_PATH:
        print("Invalid DOWNLOAD_PATH: {}".format(DOWNLOAD_PATH))
        return False

    global DATA_PATH
    DATA_PATH = config[COMPANY]["DATA_PATH"]
    if not DATA_PATH:
        print("Invalid DATA_PATH: {}".format(DATA_PATH))
        return False

    return True


def main():
    t = str(int(time.time()))

    # Check if download/kmb-<version>.apk exist
    if not os.path.isfile("{}kmb-{}.apk".format(DOWNLOAD_PATH, APP_VERSION)):
        print("Missing file: {}kmb-{}.apk".format(DOWNLOAD_PATH, APP_VERSION))
        return

    # Unzip kmb.mp3 to download/kmb-<version>.db
    print("Get Database from apk: {}kmb-{}.apk".format(DOWNLOAD_PATH, APP_VERSION))

    archive = zipfile.ZipFile("{}kmb-{}.apk".format(DOWNLOAD_PATH, APP_VERSION))
    archive.extract("res/raw/kmb.mp3", "/tmp/kmb-{}".format(APP_VERSION))
    os.rename("/tmp/kmb-{}/res/raw/kmb.mp3".format(APP_VERSION), "{}kmb-{}.db".format(DOWNLOAD_PATH, APP_VERSION))

    print("Database extracted to: {}kmb-{}.db".format(DOWNLOAD_PATH, APP_VERSION))

    # Download DB update sql to kmb-<version>.sql
    print("Get SQL from url: {}".format(DOWNLOAD_URL.format(APP_VERSION, LAST_UPDATE)))

    opener = urllib.request.build_opener()
    response = opener.open(DOWNLOAD_URL.format(APP_VERSION, LAST_UPDATE))

    dataUrl = str(json.loads(response.read())["deltadataurl"])
    response = opener.open(dataUrl)
    root = ElementTree.fromstring(response.read())
    with open("{}kmb-{}.sql".format(DOWNLOAD_PATH, APP_VERSION), "w") as f:
        for log in root.iter("string"):
            f.write(log.text + ";\n")

    print("SQL extracted to: {}kmb-{}.sql".format(DOWNLOAD_PATH, APP_VERSION))

    # Reset data
    if os.path.exists(DATA_PATH):
        shutil.rmtree(DATA_PATH)
    os.makedirs(DATA_PATH)

    # Build latest db/kmb-<version>.db
    print("Prepare latest database in {}kmb-{}.db".format(DATA_PATH, APP_VERSION))

    shutil.copy2("{}kmb-{}.db".format(DOWNLOAD_PATH, APP_VERSION), "{}kmb-{}.db".format(DATA_PATH, APP_VERSION))
    with open("{}kmb-{}.sql".format(DOWNLOAD_PATH, APP_VERSION), "r") as f, sqlite3.connect("{}kmb-{}.db".format(DATA_PATH, APP_VERSION)) as conn:
        db = conn.cursor()
        cnt = 0
        sql_statement = ""

        for line in f:
            try:
                cnt = cnt + 1
                sql_statement = sql_statement + line
                if (line.endswith(";\n")):
                    # TODO: Replace special char
                    db.executescript(sql_statement)
                    sql_statement = ""

            except:
                print("Error on line {}: {}".format(cnt, sql_statement))
                sql_statement = ""

            if (cnt % 10000 == 0):
                print("Running on line {}".format(cnt))

        print("Finish running {} lines of sql".format(cnt))
        conn.commit()

    # Finish
    with open("{}t.txt".format(DATA_PATH), "w", encoding="utf8") as f:
        f.write(t)

    print("Finish download kmb: {}kmb-{}.db".format(DATA_PATH, APP_VERSION))


if __name__ == "__main__":
    if get_config():
        main()
