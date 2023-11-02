from enum import StrEnum, IntEnum
import datetime
from tkinter import W
from typing import Generic, Optional, TypeVar, TypedDict, NotRequired

from pydantic import BaseModel, validator

dataR = TypeVar("dataR", bound=TypedDict)
dataP = TypeVar("dataP", bound=BaseModel)

def make_tz_aware(v):
    tz_aware =  datetime.datetime.fromisoformat(v + "+00:00")
    return tz_aware

class ResponseStatus(StrEnum):
    OK = "OK"
    ERROR = "ERROR" 


class ErrorCode(IntEnum):
    INVALID_KEY = 1
    UNKNOWN = 2
    LIMIT_EXCEEDED = 3
    INVALID_DEVICE= 4
    INTERNAL_ERROR = 5
    PARAMETER_ERROR = 6

class DeviceStatus(StrEnum):
    STANDBY = "STANDBY"
    SETUP = "SETUP"
    ONLINE = "ONLINE"
    WATERING = "WATERING"
    OFFLINE = "OFFLINE"
    SLEEPING = "SLEEPING"
    POWEROFF = "POWEROFF"

class DeviceSetStatus(IntEnum):
    STANDBY = 0
    ONLINE = 1

class ZoneSmart(StrEnum):
    SMART = "SMART"
    ASSISTANT = "ASSISTANT"
    TIMER = "TIMER"

class ScheduleSource(StrEnum):
    MANUAL = "MANUAL"
    SMART = "SMART"

class ScheduleStatus(StrEnum):
    EXECUTED = "EXECUTED"
    EXECUTING = "EXECUTING"
    VALID = "VALID"
    
class EventType(IntEnum):
    DEVICE_OFFLINE = 1
    DEVICE_ONLINE = 2
    SCHEDULE_START =3
    SCHEDULE_END = 4

class WeatherConditions(IntEnum):
    CLEAR = 0 
    CLOUDY = 1 
    RAIN = 2 
    SNOW = 3 
    WIND = 4 


class MetaRaw(TypedDict):
    last_active: str
    tid: str
    time: str
    token_limit: int
    token_remaining: int
    token_reset: str
    version: str
    
class Meta(BaseModel):
    last_active: datetime.datetime
    tid: str
    time: datetime.datetime
    token_limit: int
    token_remaining: int
    token_reset: datetime.datetime
    version: str
    
    _make_tz_aware = validator("last_active", "time", "token_reset", pre=True, allow_reuse=True)(make_tz_aware)

class BaseResponseRaw(TypedDict):
    status: ResponseStatus
    meta: MetaRaw

class BaseResponse(BaseModel):
    status: ResponseStatus
    meta: Meta

class SuccessResponseRaw(BaseResponseRaw, Generic[dataR]):
    data: dataR    

class SuccessResponse(BaseResponse, Generic[dataP]):
    data: dataP

class ErrorDataRaw(TypedDict):
    code: ErrorCode
    message: str

class ErrorData(BaseModel):
    code: ErrorCode
    message: str

class ErrorResponseRaw(BaseResponseRaw):
    errors: list[ErrorDataRaw]
    
class ErrorResponse(BaseResponse):
    errors: list[ErrorData]

class ZoneRaw(TypedDict):
    enabled: bool
    ith: int
    name: str
    smart: ZoneSmart

class Zone(BaseModel):
    enabled: bool
    ith: int
    name: str
    smart: ZoneSmart

class DeviceRaw(TypedDict):
    last_active: str
    name: str
    serial: str
    status: DeviceStatus
    sw_version: str
    version: str
    zone_num: int
    zones: list[ZoneRaw]
    battery_level: NotRequired[float]

class Device(BaseModel):
    last_active: datetime.datetime
    name: str
    serial: str
    status: DeviceStatus
    sw_version: str
    version: str
    zone_num: int
    zones: list[Zone]
    batter_level: Optional[float]
    
    _make_tz_aware = validator("last_active", pre=True, allow_reuse=True)(make_tz_aware)
    
    def get_zones (self, only_active: bool = False):
        return [z for z in self.zones if z.enabled or not only_active]

class InfoDataRaw(TypedDict):
    device: DeviceRaw

class InfoData(BaseModel):
    device: Device

InfoEndpointResponseRaw = SuccessResponseRaw[InfoDataRaw]

InfoEndpointResponse = SuccessResponse[InfoData]

class ScheduleRaw(TypedDict):
    end_time: str
    id: int
    local_date: str
    local_end_time: str
    local_start_time: str
    source: ScheduleSource
    start_time: str
    status: ScheduleStatus
    zone: int    

class Schedule(BaseModel):
    end_time: datetime.datetime
    id: int
    local_date: datetime.date
    local_end_time: datetime.time
    local_start_time: datetime.time
    source: ScheduleSource
    start_time: datetime.datetime
    status: ScheduleStatus
    zone: int
    duration: Optional[datetime.timedelta]
    
    _make_tz_aware = validator("start_time", "end_time", pre=True, allow_reuse=True)(make_tz_aware)
    
    @validator("duration", always=True)
    def calc_duration(cls, v, values):
        return values["end_time"] - values["start_time"]

class ScheduleDataRaw(TypedDict):
    schedules: list[ScheduleRaw]

class ScheduleData(BaseModel):
    schedules: list[Schedule]
    
    def get_schedules_for_zone (self, zone: int):
        return [s for s in self.schedules if s.zone == zone]

ScheduleEndpointResponseRaw = SuccessResponseRaw[ScheduleDataRaw]

SchedulesEndpointResponse = SuccessResponse[ScheduleData]
    
class MoistureRaw(TypedDict):
    date: str
    id: int
    moisture: int
    zone: int

class Moisture(BaseModel):
    date: datetime.date
    id: int
    moisture: int
    zone: int
        
class MoistureDataRaw(TypedDict):
    moistures: list[MoistureRaw]

class MoistureData(BaseModel):
    moistures: list[Moisture]
        
    def get_moistures_for_zone (self, zone: int):
        return [m for m in self.moistures if m.zone == zone]

MoisturesEndpointResponseRaw = SuccessResponseRaw[MoistureDataRaw]

MoisturesEndpointResponse = SuccessResponse[MoistureData]
        
class EventRaw(TypedDict):
    event: EventType
    id: int
    message: str
    time: str

class Event(BaseModel):
    event: EventType
    id: int
    message: str
    time: datetime.datetime
    
    _make_tz_aware = validator("time", pre=True, allow_reuse=True)(make_tz_aware)

class EventDataRaw(TypedDict):
    events: list[EventRaw]

class EventData(BaseModel):
    events: list[Event]

EventsEndpointResponseRaw = SuccessResponseRaw[EventDataRaw]

EventsEndpointResponse = SuccessResponse[EventData]

class SensorRaw(TypedDict):
    id: int
    time: str
    local_date: str
    local_time: str
    moisture: int
    sunlight: float
    celsius: float
    fahrenheit: float
    battery_level: int

class Sensor(BaseModel):
    id: int
    time: datetime.datetime
    local_date: datetime.date
    local_time: datetime.time
    moisture: int
    sunlight: float
    celsius: float
    fahrenheit: float
    battery_level: int
    
    _make_tz_aware = validator("time", pre=True, allow_reuse=True)(make_tz_aware)

class SensorDataRaw(TypedDict):
    sensor_data: list[SensorRaw]

class SensorData(BaseModel):
    sensor_data: list[Sensor]

SensorsEndpointResponseRaw = SuccessResponseRaw[SensorDataRaw]

SensorsEndpointResponse = SuccessResponse[SensorData]