import configparser, json, os, shutil, sqlite3
import xml.etree.cElementTree as ElementTree

from dataclass.route import *
from dataclass.stop import *

COMPANY = "MTRB"

SELECT_DISTINCT_ROUTE_NO = """
    SELECT DISTINCT route_number
    FROM busRoute
    ORDER BY route_number
"""

SELECT_PARENT_ROUTES = """
    SELECT route_number,
    CASE shape
        WHEN 'U' THEN 0
        WHEN 'I' THEN 1
        WHEN 'H' THEN 2
    END AS direction,
    CASE INSTR(description_zh, ' ←→ ')
        WHEN 0
            THEN SUBSTR(description_zh, 0, INSTR(description_zh, '至'))
            ELSE SUBSTR(description_zh, 0, INSTR(description_zh, ' ←→ '))
    END AS from_tc,
    CASE INSTR(description_zh, ' ←→ ')
        WHEN 0
            THEN SUBSTR(description_zh, INSTR(description_zh, '至') + 1)
            ELSE SUBSTR(description_zh, INSTR(description_zh, ' ←→ ') + 4)
    END AS to_tc,
    CASE INSTR(description_en, ' ←→ ')
        WHEN 0
            THEN SUBSTR(description_en, 0, INSTR(description_en, ' to '))
            ELSE SUBSTR(description_en, 0, INSTR(description_en, ' ←→ '))
    END AS from_en,
    CASE INSTR(description_en, ' ←→ ')
        WHEN 0
            THEN SUBSTR(description_en, INSTR(description_en, ' to ') + 4)
            ELSE SUBSTR(description_en, INSTR(description_en, ' ←→ ') + 4)
    END AS to_en,
    octopus_adult
    FROM busRoute,
    ( SELECT DISTINCT route_ID, shape FROM busRouteLine ) AS busRouteLine,
   	busFare
    WHERE route_number = '{}'
    AND busRoute.route_ID = busRouteLine.route_ID
    AND busRoute.route_ID = busFare.route_ID
    ORDER BY route_number
"""

SELECT_CHILD_ROUTES = """
    SELECT route_number, routeLine_ID, from_stop
    FROM busRoute, busRouteLine
    WHERE route_number = '{}'
    AND busRoute.route_ID = busRouteLine.route_ID
    ORDER BY route_number, routeLine_ID
"""

SELECT_STOPS = """
    SELECT busStop.*
    FROM busRouteLine, busStop
    WHERE busRouteLine.routeLine_ID = '{}'
    AND busRouteLine.routeLine_ID = busStop.routeLine_ID
    ORDER BY sort_order
"""

APP_VERSION = ""
DOWNLOAD_PATH = ""
RESULT_PATH = ""
UPLOAD_PATH = ""

def to_parent_route(rec: Any) -> Any:
    route = Route()
    route.route_key.company = COMPANY
    route.route_key.route_no = rec["route_number"]
    route.route_key.bound = 0
    route.route_key.variant = 0
    route.direction = int(rec["direction"])
    route.special_code = 0
    route.company_details = [COMPANY]
    route.route_from.tc = rec["from_tc"]
    route.route_from.en = rec["from_en"]
    route.route_from.sc = ""
    route.to.tc = rec["to_tc"]
    route.to.en = rec["to_en"]
    route.to.sc = ""

    return route_to_dict(route)

def to_child_route(rec: Any, bound: int, parentRoute: Any) -> Any:
    route = Route()
    route.route_key.company = COMPANY
    route.route_key.route_no = rec["route_number"]
    route.route_key.bound = bound
    route.route_key.variant = 1
    route.direction = 1 if parentRoute["direction"] > 1 else parentRoute["direction"]
    route.special_code = 0
    route.company_details = [COMPANY]
    route.route_from.tc = parentRoute["from"]["tc"] if bound == 1 else parentRoute["to"]["tc"]
    route.route_from.en = parentRoute["from"]["en"] if bound == 1 else parentRoute["to"]["en"]
    route.route_from.sc = parentRoute["from"]["sc"] if bound == 1 else parentRoute["to"]["sc"]
    route.to.tc = parentRoute["to"]["tc"] if bound == 1 else parentRoute["from"]["tc"]
    route.to.en = parentRoute["to"]["en"] if bound == 1 else parentRoute["from"]["en"]
    route.to.sc = parentRoute["to"]["sc"] if bound == 1 else parentRoute["from"]["sc"]

    return route_to_dict(route)

def to_stop(rec: Any, fare: float, childRoute: Any) -> Any:
    stop = Stop()
    stop.route_key.company = COMPANY
    stop.route_key.route_no = childRoute["routeKey"]["routeNo"]
    stop.route_key.bound = childRoute["routeKey"]["bound"]
    stop.route_key.variant = childRoute["routeKey"]["variant"]
    stop.seq = int(rec["sort_order"])
    stop.name.tc = rec["name_ch"]
    stop.name.en = rec["name_en"]
    stop.name.sc = ""
    stop.to.tc = childRoute["to"]["tc"]
    stop.to.en = childRoute["to"]["en"]
    stop.to.sc = childRoute["to"]["sc"]
    stop.details.tc = rec["remark_ch"]
    stop.details.en = rec["remark_en"]
    stop.details.sc = ""
    stop.latitude = float(rec["latitude"])
    stop.longitude = float(rec["longitude"])
    stop.fare = fare
    stop.info.stop_id = rec["ref_ID"]

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


def main():
    t = ""
    with open("{}t.txt".format(DOWNLOAD_PATH), "r") as f:
        t = f.read()

    dbFileName = ""
    with open("{}dbFileName.txt".format(DOWNLOAD_PATH), "r") as f:
        dbFileName = f.read()

    # Reset Result
    if os.path.exists(RESULT_PATH):
        shutil.rmtree(RESULT_PATH)
    os.makedirs(RESULT_PATH)

    routes = []
    parent_routes = []
    child_routes = []
    stops = []

    with sqlite3.connect("{}{}.db".format(DOWNLOAD_PATH, dbFileName)) as conn:
        db = conn.cursor()

        # Get list of routes no
        cursor = db.execute(SELECT_DISTINCT_ROUTE_NO)
        columns = [column[0] for column in cursor.description]

        for row in cursor.fetchall():
            rec = dict(zip(columns, row))
            routes.append(rec["route_number"])

        for route in routes:
            parent = None
            route_map = {}
            route_cnt = 0
            stop_cnt = 0

            # Get parent routes
            cursor = db.execute(SELECT_PARENT_ROUTES.format(route))
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                rec = dict(zip(columns, row))
                if parent is None:
                    fare = float(rec["octopus_adult"])
                    parent = to_parent_route(rec)
                    parent_routes.append(parent)

            # Get child routes
            cursor = db.execute(SELECT_CHILD_ROUTES.format(route))
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                rec = dict(zip(columns, row))
                child = to_child_route(rec, route_cnt + 1, parent)
                route_map[rec["routeLine_ID"]] = child
                child_routes.append(child)
                route_cnt = route_cnt + 1

            # Get stops
            for key, value in route_map.items():
                cursor = db.execute(SELECT_STOPS.format(key))
                columns = [column[0] for column in cursor.description]

                for row in cursor.fetchall():
                    rec = dict(zip(columns, row))
                    stops.append(to_stop(rec, fare, value))
                    stop_cnt = stop_cnt + 1

            print("[{}]: direction = {} route_cnt = {}, stop_cnt = {}".format(route, parent["direction"], route_cnt, stop_cnt))

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
    os.rename("{}.zip".format(RESULT_PATH[:-1]), "{}mtrb.zip".format(UPLOAD_PATH))

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
