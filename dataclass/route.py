# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = route_from_dict(json.loads(json_string))

from dataclasses import dataclass, field
from typing import Optional, Any, List, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


@dataclass
class Details:
    tc: Optional[str] = ""
    en: Optional[str] = ""
    sc: Optional[str] = ""

    @staticmethod
    def from_dict(obj: Any) -> 'Details':
        assert isinstance(obj, dict)
        tc = from_union([from_str, from_none], obj.get("tc"))
        en = from_union([from_str, from_none], obj.get("en"))
        sc = from_union([from_str, from_none], obj.get("sc"))
        return Details(tc, en, sc)

    def to_dict(self) -> dict:
        result: dict = {}
        result["tc"] = from_union([from_str, from_none], self.tc)
        result["en"] = from_union([from_str, from_none], self.en)
        result["sc"] = from_union([from_str, from_none], self.sc)
        return result


@dataclass
class Info:
    bound_ids: Optional[List[str]] = field(default_factory=list)
    rdv: Optional[str] = ""
    bound: Optional[str] = ""
    start_seq: Optional[int] = None
    end_seq: Optional[int] = None
    stop_id: Optional[str] = ""
    fare_holiday: Optional[float] = None
    partial: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Info':
        assert isinstance(obj, dict)
        bound_ids = from_union([lambda x: from_list(from_str, x), from_none], obj.get("boundIds"))
        rdv = from_union([from_str, from_none], obj.get("rdv"))
        bound = from_union([from_str, from_none], obj.get("bound"))
        start_seq = from_union([from_int, from_none], obj.get("startSeq"))
        end_seq = from_union([from_int, from_none], obj.get("endSeq"))
        stop_id = from_union([from_str, from_none], obj.get("stopId"))
        fare_holiday = from_union([from_float, from_none], obj.get("fareHoliday"))
        partial = from_union([from_int, from_none], obj.get("partial"))
        return Info(bound_ids, rdv, bound, start_seq, end_seq, stop_id, fare_holiday, partial)

    def to_dict(self) -> dict:
        result: dict = {}
        result["boundIds"] = from_union([lambda x: from_list(from_str, x), from_none], self.bound_ids)
        result["rdv"] = from_union([from_str, from_none], self.rdv)
        result["bound"] = from_union([from_str, from_none], self.bound)
        result["startSeq"] = from_union([from_int, from_none], self.start_seq)
        result["endSeq"] = from_union([from_int, from_none], self.end_seq)
        result["stopId"] = from_union([from_str, from_none], self.stop_id)
        result["fareHoliday"] = from_union([to_float, from_none], self.fare_holiday)
        result["partial"] = from_union([from_int, from_none], self.partial)
        return result


@dataclass
class RouteKey:
    company: Optional[str] = None
    route_no: Optional[str] = None
    bound: Optional[int] = None
    variant: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'RouteKey':
        assert isinstance(obj, dict)
        company = from_union([from_str, from_none], obj.get("company"))
        route_no = from_union([from_str, from_none], obj.get("routeNo"))
        bound = from_union([from_int, from_none], obj.get("bound"))
        variant = from_union([from_int, from_none], obj.get("variant"))
        return RouteKey(company, route_no, bound, variant)

    def to_dict(self) -> dict:
        result: dict = {}
        result["company"] = from_union([from_str, from_none], self.company)
        result["routeNo"] = from_union([from_str, from_none], self.route_no)
        result["bound"] = from_union([from_int, from_none], self.bound)
        result["variant"] = from_union([from_int, from_none], self.variant)
        return result


@dataclass
class Route:
    route_key: Optional[RouteKey] = RouteKey()
    direction: Optional[int] = None
    special_code: Optional[int] = None
    company_details: Optional[List[str]] = field(default_factory=list)
    route_from: Optional[Details] = Details()
    to: Optional[Details] = Details()
    details: Optional[Details] = Details()
    path: Optional[str] = ""
    info: Optional[Info] = Info()
    eta: Optional[bool] = False
    display_seq: Optional[int] = -1
    type_seq: Optional[int] = -1

    @staticmethod
    def from_dict(obj: Any) -> 'Route':
        assert isinstance(obj, dict)
        route_key = from_union([RouteKey.from_dict, from_none], obj.get("routeKey"))
        direction = from_union([from_int, from_none], obj.get("direction"))
        special_code = from_union([from_int, from_none], obj.get("specialCode"))
        company_details = from_union([lambda x: from_list(from_str, x), from_none], obj.get("companyDetails"))
        route_from = from_union([Details.from_dict, from_none], obj.get("from"))
        to = from_union([Details.from_dict, from_none], obj.get("to"))
        details = from_union([Details.from_dict, from_none], obj.get("details"))
        path = from_union([from_str, from_none], obj.get("path"))
        info = from_union([Info.from_dict, from_none], obj.get("info"))
        eta = from_union([from_bool, from_none], obj.get("eta"))
        display_seq = from_union([from_int, from_none], obj.get("displaySeq"))
        type_seq = from_union([from_int, from_none], obj.get("typeSeq"))
        return Route(route_key, direction, special_code, company_details, route_from, to, details, path, info, eta, display_seq, type_seq)

    def to_dict(self) -> dict:
        result: dict = {}
        result["routeKey"] = from_union([lambda x: to_class(RouteKey, x), from_none], self.route_key)
        result["direction"] = from_union([from_int, from_none], self.direction)
        result["specialCode"] = from_union([from_int, from_none], self.special_code)
        result["companyDetails"] = from_union([lambda x: from_list(from_str, x), from_none], self.company_details)
        result["from"] = from_union([lambda x: to_class(Details, x), from_none], self.route_from)
        result["to"] = from_union([lambda x: to_class(Details, x), from_none], self.to)
        result["details"] = from_union([lambda x: to_class(Details, x), from_none], self.details)
        result["path"] = from_union([from_str, from_none], self.path)
        result["info"] = from_union([lambda x: to_class(Info, x), from_none], self.info)
        result["eta"] = from_union([from_bool, from_none], self.eta)
        result["displaySeq"] = from_union([from_int, from_none], self.display_seq)
        result["typeSeq"] = from_union([from_int, from_none], self.type_seq)
        return result


def route_from_dict(s: Any) -> Route:
    return Route.from_dict(s)


def route_to_dict(x: Route) -> Any:
    return to_class(Route, x)
