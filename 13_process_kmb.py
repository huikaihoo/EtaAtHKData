import configparser, json, os, shutil, sqlite3
import xml.etree.cElementTree as ElementTree

from dataclass.route import *
from dataclass.stop import *

COMPANY = "KMB"

SELECT_DISTINCT_ROUTE_NO = """
    SELECT DISTINCT route_no,
    CASE WHEN destination LIKE '%CIRCULAR%' THEN 0 ELSE MAX(bound_no) END direction
    FROM kmb_routeboundmaster_ST
    WHERE route_no NOT IN ( {} )
    GROUP BY route_no
    ORDER BY route_no
"""

SELECT_ROUTES = """
    SELECT * FROM kmb_routeboundmaster_ST
    WHERE route_no = '{}'
    ORDER BY bound_no, service_type
"""

SELECT_STOPS = """
    SELECT * FROM kmb_routestopfile_ST
    WHERE route_no = '{}'
    ORDER BY bound, service_type, stop_seq
"""

APP_VERSION = ""
EXCLUDE_ROUTES = ""
KMB_ROUTES_PREFIX = ""
LWB_ROUTES_PREFIX = ""
DATA_PATH = ""
RESULT_PATH = ""
UPLOAD_PATH = ""

def route_no_to_company(route_no: str) -> str:
    for prefix in KMB_ROUTES_PREFIX:
        if route_no.startswith(prefix.strip()):
            return "KMB"
    for prefix in LWB_ROUTES_PREFIX:
        if route_no.startswith(prefix.strip()):
            return "LWB"
    return "KMB"

def to_parent_route(rec: Any, direction: int) -> Any:
    company = route_no_to_company(rec["route_no"])

    route = Route()
    route.route_key.company = company
    route.route_key.route_no = rec["route_no"]
    route.route_key.bound = 0
    route.route_key.variant = 0
    route.direction = direction
    route.special_code = 0
    route.company_details = [company]
    route.route_from.tc = rec["origin_chi"]
    route.route_from.en = rec["origin"]
    route.route_from.sc = rec["origin_cn"]
    route.to.tc = rec["destination_chi"]
    route.to.en = rec["destination"]
    route.to.sc = rec["destination_cn"]
    route.details.tc = ""
    route.details.en = ""
    route.details.sc = ""

    return route_to_dict(route)

def to_child_route(rec: Any, direction: int) -> Any:
    company = route_no_to_company(rec["route_no"])

    route = Route()
    route.route_key.company = company
    route.route_key.route_no = rec["route_no"]
    route.route_key.bound = rec["bound_no"]
    route.route_key.variant = int(rec["service_type"])
    route.direction = 1 if direction > 1 else direction     # TODO: Check if "Circular" appear in destination
    route.special_code = 0
    route.company_details = [company]
    route.route_from.tc = rec["origin_chi"]
    route.route_from.en = rec["origin"]
    route.route_from.sc = rec["origin_cn"]
    route.to.tc = rec["destination_chi"]
    route.to.en = rec["destination"]
    route.to.sc = rec["destination_cn"]
    route.details.tc = rec["service_type_desc_chi"]
    route.details.en = rec["service_type_desc_eng"]
    route.details.sc = rec["service_type_desc_cn"]

    return route_to_dict(route)

def to_stop(rec: Any, routeRec: Any) -> Any:
    company = route_no_to_company(rec["route_no"])

    stop = Stop()
    stop.route_key.company = company
    stop.route_key.route_no = rec["route_no"]
    stop.route_key.bound = int(rec["bound"])
    stop.route_key.variant = int(rec["service_type"])
    stop.seq = int(rec["stop_seq"])
    stop.name.tc = rec["stop_name_chi"]
    stop.name.en = rec["stop_name"]
    stop.name.sc = rec["stop_name_chi"]
    stop.to.tc = routeRec["destination_chi"]
    stop.to.en = routeRec["destination"]
    stop.to.sc = routeRec["destination_cn"]
    stop.details.tc = rec["stop_loc_chi1"] + rec["stop_loc_chi2"] + rec["stop_loc_chi3"]
    stop.details.en = (rec["stop_loc1"] + ' ' + rec["stop_loc2"] + ' ' + rec["stop_loc3"]).strip()
    stop.details.sc = rec["stop_loc_cn1"] + rec["stop_loc_cn2"] + rec["stop_loc_cn3"]
    stop.latitude = float(rec["lat"])
    stop.longitude = float(rec["lng"])
    stop.fare = float(rec["air_cond_fare"])
    stop.info.stop_id = rec["subarea"]

    return stop_to_dict(stop)


def get_config() -> bool:
    # Get Config from config.ini
    config = configparser.ConfigParser()
    config.read("config.ini")

    global APP_VERSION
    APP_VERSION = config[COMPANY]["APP_VERSION"]
    if not APP_VERSION:
        print("Invalid APP_VERSION: {}".format(APP_VERSION))
        return False

    global EXCLUDE_ROUTES
    EXCLUDE_ROUTES = config[COMPANY]["EXCLUDE_ROUTES"]
    if not EXCLUDE_ROUTES:
        print("Invalid EXCLUDE_ROUTES: {}".format(EXCLUDE_ROUTES))
        return False

    global KMB_ROUTES_PREFIX
    KMB_ROUTES_PREFIX = config[COMPANY]["KMB_ROUTES_PREFIX"].split(",")
    if not KMB_ROUTES_PREFIX:
        print("Invalid KMB_ROUTES_PREFIX: {}".format(KMB_ROUTES_PREFIX))
        return False

    global LWB_ROUTES_PREFIX
    LWB_ROUTES_PREFIX = config[COMPANY]["LWB_ROUTES_PREFIX"].split(",")
    if not LWB_ROUTES_PREFIX:
        print("Invalid LWB_ROUTES_PREFIX: {}".format(LWB_ROUTES_PREFIX))
        return False

    global DATA_PATH
    DATA_PATH = config[COMPANY]["DATA_PATH"]
    if not DATA_PATH:
        print("Invalid DATA_PATH: {}".format(DATA_PATH))
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


def main():
    t = ""
    with open("{}t.txt".format(DATA_PATH), "r") as f:
        t = f.read()

    # Reset Result
    if os.path.exists(RESULT_PATH):
        shutil.rmtree(RESULT_PATH)
    os.makedirs(RESULT_PATH)

    routes = []
    parent_routes = []
    child_routes = []
    stops = []

    with sqlite3.connect("{}kmb-{}.db".format(DATA_PATH, APP_VERSION)) as conn:
        route_direction = {}
        db = conn.cursor()

        # Get list of routes no
        cursor = db.execute(SELECT_DISTINCT_ROUTE_NO.format(EXCLUDE_ROUTES))
        columns = [column[0] for column in cursor.description]

        for row in cursor.fetchall():
            rec = dict(zip(columns, row))
            routes.append(rec["route_no"])
            route_direction[rec["route_no"]] = rec["direction"]

        for route in routes:
            route_map = {}
            route_cnt = 0
            stop_cnt = 0

            # Get parent and child routes
            cursor = db.execute(SELECT_ROUTES.format(route))
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                rec = dict(zip(columns, row))
                route_map[str(rec["bound_no"]) + "_" + rec["service_type"]] = rec
                if route_cnt == 0:
                    parent_routes.append(to_parent_route(rec, route_direction[route]))
                child_routes.append(to_child_route(rec, route_direction[route]))
                route_cnt = route_cnt + 1

            # Get stops
            cursor = db.execute(SELECT_STOPS.format(route))
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                rec = dict(zip(columns, row))
                stops.append(to_stop(rec, route_map[rec["bound"] + "_" + rec["service_type"]]))
                stop_cnt = stop_cnt + 1

            print("[{}]: company = {}, direction = {}, route_cnt = {}, stop_cnt = {}".format(route, route_no_to_company(route), route_direction[route], route_cnt, stop_cnt))

    # Export the result
    metadata = { "parent_cnt": len(parent_routes), "child_cnt": len(child_routes), "stops_cnt": len(stops), "routes": routes, "timestamp": t }

    with open("{}metadata.json".format(RESULT_PATH), "w", encoding="utf8") as f:
        f.write(json.dumps(metadata, ensure_ascii=False))

    with open("{}parent.json".format(RESULT_PATH), "w", encoding="utf8") as f:
        f.write(json.dumps(parent_routes, ensure_ascii=False))

    with open("{}child.json".format(RESULT_PATH), "w", encoding="utf8") as f:
        f.write(json.dumps(child_routes, ensure_ascii=False))

    with open("{}stops.json".format(RESULT_PATH), "w", encoding="utf8") as f:
        f.write(json.dumps(stops, ensure_ascii=False))

    # Zip the result
    shutil.make_archive(RESULT_PATH[:-1], 'zip', RESULT_PATH)
    os.rename("{}.zip".format(RESULT_PATH[:-1]), "{}kmb.zip".format(UPLOAD_PATH))

    print("-------------------")
    print("Convert Result:")
    print("len(routes) = ", len(routes))
    print("len(parent_routes) = ", len(parent_routes))
    print("len(child_routes) = ", len(child_routes))
    print("len(stops) = ", len(stops))
    print("timestamp = ", t)
    print("-------------------")


if __name__ == "__main__":
    if get_config():
        main()
