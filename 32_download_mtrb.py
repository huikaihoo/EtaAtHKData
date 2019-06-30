import configparser, os, time, urllib.request, zipfile
import xml.etree.cElementTree as ElementTree

COMPANY = "MTRB"

APP_VERSION = ""
DOWNLOAD_URL = ""
RESOURCE_XPATH = ""
DOWNLOAD_PATH = ""

def get_config() -> bool:
    # Get Config from config.ini
    config = configparser.ConfigParser()
    config.read("config.ini")

    global APP_VERSION
    APP_VERSION = config[COMPANY]["APP_VERSION"]
    if not APP_VERSION:
        print("Invalid APP_VERSION: {}".format(APP_VERSION))
        return False

    global DOWNLOAD_URL
    DOWNLOAD_URL = config[COMPANY]["DOWNLOAD_URL"]
    if not DOWNLOAD_URL:
        print("Invalid DOWNLOAD_URL: {}".format(DOWNLOAD_URL))
        return False

    global RESOURCE_XPATH
    RESOURCE_XPATH = config[COMPANY]["RESOURCE_XPATH"]
    if not RESOURCE_XPATH:
        print("Invalid RESOURCE_XPATH: {}".format(RESOURCE_XPATH))
        return False

    global DOWNLOAD_PATH
    DOWNLOAD_PATH = config[COMPANY]["DOWNLOAD_PATH"]
    if not DOWNLOAD_PATH:
        print("Invalid DOWNLOAD_PATH: {}".format(DOWNLOAD_PATH))
        return False

    return True


def main():
    t = str(int(time.time()))

    # Reset download
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
    
    # Get latest db in zip file
    print("Get SQL from url: {}".format(DOWNLOAD_URL.format(APP_VERSION)))

    opener = urllib.request.build_opener()
    response = opener.open(DOWNLOAD_URL.format(APP_VERSION))
    root = ElementTree.fromstring(response.read())

    dbUrl = root.find(RESOURCE_XPATH).attrib['url']
    dbFileName = (dbUrl.split("/")[-1]).split(".")[:-1][0]
    response = urllib.request.urlretrieve(dbUrl, "{}{}.zip".format(DOWNLOAD_PATH, dbFileName))

    # Unzip download/E_Bus_<version>.zip to download/E_Bus_<version>.db
    print("Get Database from zip: {}{}.zip".format(DOWNLOAD_PATH, dbFileName))

    archive = zipfile.ZipFile("{}{}.zip".format(DOWNLOAD_PATH, dbFileName))
    archive.extract("E_Bus.db", "/tmp/mtrb-{}".format(dbFileName))
    os.rename("/tmp/mtrb-{}/E_Bus.db".format(dbFileName), "{}{}.db".format(DOWNLOAD_PATH, dbFileName))

    # Store the latest db name
    with open("{}dbFileName.txt".format(DOWNLOAD_PATH), "w", encoding="utf8") as f:
        f.write(dbFileName)

    # Finish
    with open("{}t.txt".format(DOWNLOAD_PATH), "w", encoding="utf8") as f:
        f.write(t)

    print("Finish download mtrb: {}{}.db".format(DOWNLOAD_PATH, dbFileName))


if __name__ == "__main__":
    if get_config():
        main()
