# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = stop_from_dict(json.loads(json_string))

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


def is_type(t: Type[T], x: Any) -> T:
    assert isinstance(x, t)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


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
class Stop:
    route_key: Optional[RouteKey] = RouteKey()
    seq: Optional[int] = None
    name: Optional[Details] = Details()
    to: Optional[Details] = Details()
    details: Optional[Details] = Details()
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fare: Optional[float] = None
    info: Optional[Info] = Info()

    @staticmethod
    def from_dict(obj: Any) -> 'Stop':
        assert isinstance(obj, dict)
        route_key = from_union([RouteKey.from_dict, from_none], obj.get("routeKey"))
        seq = from_union([from_int, from_none], obj.get("seq"))
        name = from_union([Details.from_dict, from_none], obj.get("name"))
        to = from_union([Details.from_dict, from_none], obj.get("to"))
        details = from_union([Details.from_dict, from_none], obj.get("details"))
        latitude = from_union([from_float, from_none], obj.get("latitude"))
        longitude = from_union([from_float, from_none], obj.get("longitude"))
        fare = from_union([from_float, from_none], obj.get("fare"))
        info = from_union([Info.from_dict, from_none], obj.get("info"))
        return Stop(route_key, seq, name, to, details, latitude, longitude, fare, info)

    def to_dict(self) -> dict:
        result: dict = {}
        result["routeKey"] = from_union([lambda x: to_class(RouteKey, x), from_none], self.route_key)
        result["seq"] = from_union([from_int, from_none], self.seq)
        result["name"] = from_union([lambda x: to_class(Details, x), from_none], self.name)
        result["to"] = from_union([lambda x: to_class(Details, x), from_none], self.to)
        result["details"] = from_union([lambda x: to_class(Details, x), from_none], self.details)
        result["latitude"] = from_union([to_float, from_none], self.latitude)
        result["longitude"] = from_union([to_float, from_none], self.longitude)
        result["fare"] = from_union([to_float, from_none], self.fare)
        result["info"] = from_union([lambda x: to_class(Info, x), from_none], self.info)
        return result


def stop_from_dict(s: Any) -> Stop:
    return Stop.from_dict(s)


def stop_to_dict(x: Stop) -> Any:
    return to_class(Stop, x)
