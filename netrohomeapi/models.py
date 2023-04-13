from enum import Enum
import datetime
from typing import List, Optional

from pydantic import BaseModel, validator

def make_tz_aware(v):
    tz_aware =  datetime.datetime.fromisoformat(v + "+00:00")
    return tz_aware

class ResponseStatus(Enum):
    OK = "OK"
    ERROR = "ERROR" 

class ErrorCode(Enum):
    INVALID_KEY = 1
    UNKNOWN = 2
    LIMIT_EXCEEDED = 3
    INVALID_DEVICE= 4
    INTERNAL_ERROR = 5
    PARAMETER_ERROR = 6

class DeviceStatus(Enum):
    STANDBY = "STANDBY"
    SETUP = "SETUP"
    ONLINE = "ONLINE"
    WATERING = "WATERING"
    OFFLINE = "OFFLINE"
    SLEEPING = "SLEEPING"
    POWEROFF = "POWEROFF"

class DeviceSetStatus(Enum):
    STANDBY = 0
    ONLINE = 1

class ZoneSmart(Enum):
    SMART = "SMART"
    ASSISTANT = "ASSISTANT"
    TIMER = "TIMER"


class ScheduleSource(Enum):
    MANUAL = "MANUAL"
    SMART = "SMART"


class ScheduleStatus(Enum):
    EXECUTED = "EXECUTED"
    EXECUTING = "EXECUTING"
    VALID = "VALID"
    
class EventType(Enum):
    DEVICE_OFFLINE = 1
    DEVICE_ONLINE = 2
    SCHEDULE_START =3
    SCHEDULE_END = 4

    
class Meta(BaseModel):
    last_active: datetime.datetime
    tid: str
    time: datetime.datetime
    token_limit: int
    token_remaining: int
    token_reset: datetime.datetime
    version: str
    
    _make_tz_aware = validator("last_active", "time", "token_reset", pre=True, allow_reuse=True)(make_tz_aware)


class BaseResponse(BaseModel):
    status: ResponseStatus
    meta: Meta
    
class SuccessResponse(BaseResponse):
    data: Optional[dict]

class ErrorData(BaseModel):
    code: ErrorCode
    message: str
    
class ErrorResponse(BaseResponse):
    errors: List[ErrorData]
    
class Zone(BaseModel):
    enabled: bool
    ith: int
    name: str
    smart: ZoneSmart


class Device(BaseModel):
    last_active: datetime.datetime
    name: str
    serial: str
    status: DeviceStatus
    sw_version: str
    version: str
    zone_num: int
    zones: List[Zone]
    
    _make_tz_aware = validator("last_active", pre=True, allow_reuse=True)(make_tz_aware)
    
    def get_zones (self, only_active: bool = False):
        return [z for z in self.zones if z.enabled or not only_active]



class InfoData(BaseModel):
    device: Device


class InfoEndpointResponse(SuccessResponse):
    data: InfoData
    
    

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



class ScheduleData(BaseModel):
    schedules: List[Schedule]
    
    def get_schedules_for_zone (self, zone: int):
        return [s for s in self.schedules if s.zone == zone]


class SchedulesEndpointResponse(SuccessResponse):
    data: ScheduleData
    

class Moisture(BaseModel):
    date: datetime.date
    id: int
    moisture: int
    zone: int
        

class MoistureData(BaseModel):
    moistures: List[Moisture]
        
    def get_moistures_for_zone (self, zone: int):
        return [m for m in self.moistures if m.zone == zone]


class MoisturesEndpointResponse(SuccessResponse):
    data: MoistureData
        

class Event(BaseModel):
    event: EventType
    id: int
    message: str
    time: datetime.datetime
    
    _make_tz_aware = validator("time", pre=True, allow_reuse=True)(make_tz_aware)



class EventData(BaseModel):
    events: List[Event]


class EventsEndpointResponse(SuccessResponse):
    data: EventData
    

