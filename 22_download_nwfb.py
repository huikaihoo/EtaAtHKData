import configparser, hashlib, json, os, random, re, time, shutil, urllib.parse, urllib.request

COMPANY = "NWFB"

NWFB_ROUTE_RECORD_SIZE = 11
NWFB_ROUTE_RECORD_COMPANY = 0
NWFB_ROUTE_RECORD_INFO_BOUND_ID = 7

NWFB_VARIANT_RECORD_SIZE = 10
NWFB_VARIANT_RECORD_RDV = 2
NWFB_VARIANT_RECORD_START_SEQ = 6
NWFB_VARIANT_RECORD_END_SEQ = 7

APP_VERSION = ""
APP_PLATFORM = ""
ROUTE_URL = ""
VARIANT_URL = ""
STOP_URL = ""
USER_AGENT = ""
ROUTE_LIMIT = ""
SLEEP_TIME = ""
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

    global APP_PLATFORM
    APP_PLATFORM = config[COMPANY]["APP_PLATFORM"]
    if not APP_PLATFORM:
        print("Invalid APP_PLATFORM: {}".format(APP_PLATFORM))
        return False

    global ROUTE_URL
    ROUTE_URL = config[COMPANY]["ROUTE_URL"]
    if not ROUTE_URL:
        print("Invalid ROUTE_URL: {}".format(ROUTE_URL))
        return False

    global VARIANT_URL
    VARIANT_URL = config[COMPANY]["VARIANT_URL"]
    if not VARIANT_URL:
        print("Invalid VARIANT_URL: {}".format(VARIANT_URL))
        return False

    global STOP_URL
    STOP_URL = config[COMPANY]["STOP_URL"]
    if not STOP_URL:
        print("Invalid STOP_URL: {}".format(STOP_URL))
        return False

    global USER_AGENT
    USER_AGENT = config[COMPANY]["USER_AGENT"]
    if not USER_AGENT:
        print("Invalid USER_AGENT: {}".format(USER_AGENT))
        return False

    global ROUTE_LIMIT
    ROUTE_LIMIT = config[COMPANY]["ROUTE_LIMIT"]
    if not ROUTE_LIMIT:
        print("Invalid ROUTE_LIMIT: {}".format(ROUTE_LIMIT))
        return False

    global SLEEP_TIME
    SLEEP_TIME = config[COMPANY]["SLEEP_TIME"]
    if not SLEEP_TIME:
        print("Invalid SLEEP_TIME: {}".format(SLEEP_TIME))
        return False

    global DOWNLOAD_PATH
    DOWNLOAD_PATH = config[COMPANY]["DOWNLOAD_PATH"]
    if not DOWNLOAD_PATH:
        print("Invalid DOWNLOAD_PATH: {}".format(DOWNLOAD_PATH))
        return False

    return True


def get_system_code() -> str:
    randomNum = str(random.randrange(1000))
    randomNum += "0" * (4-len(randomNum))
    timestamp = str(int(time.time()))[-6:]

    return timestamp + randomNum + hashlib.md5((timestamp + randomNum + "firstbusmwymwy").encode(encoding='UTF-8')).hexdigest().upper()


def main():
    t = str(int(time.time()))
    parent_cnt = 0
    child_cnt = 0

    # Reset download
    if os.path.exists(DOWNLOAD_PATH):
        shutil.rmtree(DOWNLOAD_PATH)
    os.makedirs("{}child/".format(DOWNLOAD_PATH))
    os.makedirs("{}stops/".format(DOWNLOAD_PATH))

    params = urllib.parse.urlencode({
        "rno": "",
        "m": "0",
        "l": "0",
        "syscode": get_system_code(),
        "p": APP_PLATFORM,
        "appversion": APP_VERSION
    })

    # Download parent routes to nwfb/routes.txt
    print("Get Parent Routes from url: {}".format(ROUTE_URL + params))

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', USER_AGENT)]
    response = opener.open(ROUTE_URL + params)

    with open("{}parent.txt".format(DOWNLOAD_PATH), "w", encoding="utf8") as f:
        f.write(response.read().decode('utf-8'))

    print("Parent Routes downloaded to: {}parent.txt".format(DOWNLOAD_PATH))

    # Download child routes to nwfb/child/<id>.txt
    parents = []
    with open("{}parent.txt".format(DOWNLOAD_PATH), "r") as f:
        parents = f.read().split("|*|<br>")

    for cnt, parent in enumerate(parents):
        p_records = parent.split('||')

        if (len(p_records) == NWFB_ROUTE_RECORD_SIZE and cnt < int(ROUTE_LIMIT)):
            id = p_records[NWFB_ROUTE_RECORD_INFO_BOUND_ID]
            params = urllib.parse.urlencode({
                "id": id,
                "l": "0",
                "syscode": get_system_code(),
                "p": APP_PLATFORM,
                "appversion": APP_VERSION
            })

            response = opener.open(VARIANT_URL + params)

            with open("{}child/{}.txt".format(DOWNLOAD_PATH, id), "w", encoding="utf8") as f:
                f.write(response.read().decode('utf-8'))

            parent_cnt += 1

            # Download stops to nwfb/stop/<id>.txt
            childs = []
            with open("{}child/{}.txt".format(DOWNLOAD_PATH, id), "r") as f:
                childs = f.read().split("<br>")

            for child in childs:
                c_records = re.split('\\|\\||\\*\\*\\*', child)

                if (len(c_records) == NWFB_VARIANT_RECORD_SIZE):
                    info = "1|*|{}||{}||{}||{}".format(
                        p_records[NWFB_ROUTE_RECORD_COMPANY],
                        c_records[NWFB_VARIANT_RECORD_RDV],
                        c_records[NWFB_VARIANT_RECORD_START_SEQ],
                        c_records[NWFB_VARIANT_RECORD_END_SEQ]
                    )
                    params = urllib.parse.urlencode({
                        "info": info,
                        "l": "0",
                        "syscode": get_system_code(),
                        "p": APP_PLATFORM,
                        "appversion": APP_VERSION
                    })

                    response = opener.open(STOP_URL + params)

                    with open("{}stops/{}.txt".format(DOWNLOAD_PATH, info), "w",  encoding="utf8") as f:
                        f.write(response.read().decode('utf-8'))

                    child_cnt += 1

            print("Finish [{}/{}][{}]".format(cnt + 1, len(parents) - 1, id))
            time.sleep(float(SLEEP_TIME))

    # Finish
    with open("{}t.txt".format(DOWNLOAD_PATH), "w", encoding="utf8") as f:
        f.write(t)

    print("-------------------")
    print("Download Result:")
    print("timestamp  =", t)
    print("parent_cnt =", parent_cnt)
    print("child_cnt  =", child_cnt)
    print("-------------------")


if __name__ == "__main__":
    if get_config():
        main()
