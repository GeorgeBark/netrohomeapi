from datetime import date, datetime
from typing import Any, Optional
from aiohttp import ClientSession
import logging

from .models import (
    Device,
    DeviceSetStatus,
    DeviceStatus,
    ErrorResponse,
    EventType,
    EventsEndpointResponse,
    EventsEndpointResponseRaw,
    InfoEndpointResponse,
    InfoEndpointResponseRaw,
    MoisturesEndpointResponse,
    MoisturesEndpointResponseRaw,
    Schedule,
    ScheduleEndpointResponseRaw,
    SchedulesEndpointResponse,
    SensorsEndpointResponse,
    SensorsEndpointResponseRaw,
    SuccessResponse,
    SuccessResponseRaw,
    WeatherConditions
)

_LOGGER = logging.getLogger(__name__)

class NetroException(Exception):
    """standard Netro exception for raising any NPA application error."""

    def __init__(self, result: ErrorResponse) -> None:
        """Make an exception from any result error code and message."""
        self.message = result.errors[0].message #["errors"][0]["message"]
        self.code = result.errors[0].code

    def __str__(self):
        """Return a literal error message related to the current exception."""
        return (
            f"a netro (NPA) error occurred -- error code #{self.code} -> {self.message}"
        )

class NetroHomeAPI:
    BASE_URL = 'http://api.netrohome.com/npa/v1'

    def __init__(self, api_key, session: Optional[ClientSession] = None):
        self.api_key = api_key
        self.session = ClientSession() if not session else session
        
    def _get_url(self, endpoint):
        return f"{self.BASE_URL}/{endpoint}.json"

    
    async def _get_async(self, endpoint, params={}) -> SuccessResponseRaw:
        if(self.session is None):
            raise Exception("No session provided")
        
        url = self._get_url(endpoint)
        headers = {
            "Content-Type": "application/json",
        }
        base_params = {
          "key": self.api_key
        }
        async with self.session.get(url, headers=headers, params={**base_params, **params}) as response:
            response.raise_for_status()
            data = await response.json()
            if "errors" in data:
                raise NetroException(ErrorResponse.parse_obj(data))
            return data
    
    async def _post_async(self, endpoint, data={}) -> SuccessResponseRaw:
        if self.session is None:
            raise Exception("No session provided")
        
        url = self._get_url(endpoint)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        base_data = {
          "key": self.api_key
        }
        async with self.session.post(url, headers=headers, json={**base_data, **data}) as response:
            response.raise_for_status()
            data = await response.json()
            if "errors" in data:
                raise NetroException(ErrorResponse.parse_obj(data))
            return data

    
    
    # Device
    async def get_info_raw(self) -> InfoEndpointResponseRaw:
        try:
            _LOGGER.debug("Fetching info")
            return await self._get_async('info')
        except Exception as e:
            _LOGGER.error("Failed to fetch info")
            raise e
        
    async def get_info(self) -> InfoEndpointResponse:
        res = await self.get_info_raw()
        return InfoEndpointResponse.parse_obj(res)

    async def set_device_status_raw(self, status:int) -> SuccessResponseRaw:
        try:
            _LOGGER.debug("Setting status")
            return await self._post_async('set_status', data={
                "status": status
            })
        except Exception as e:
            _LOGGER.error("Failed to set status")
            raise e
        
    async def set_device_status(self, status:DeviceSetStatus):
        data = await self.set_device_status_raw(status)
        return SuccessResponse.parse_obj(data)
        
    
    
    # Schedules
    async def get_schedules_raw(self, start_date:Optional[str]=None, end_date:Optional[str]=None, zones:Optional[list[int]]=None) -> ScheduleEndpointResponseRaw:
        params = {}
        if zones:
            params.update({"zones": str(zones)})
        if start_date:
            params.update({"start_date": start_date})
        if end_date:
            params.update({"end_date": end_date})
        try:
            _LOGGER.debug("Fetching schedules")
            return await self._get_async('schedules', params)
        except Exception as e:
            _LOGGER.error("Failed to fetch schedules")
            raise e
    
    async def get_schedules(self, start_date:Optional[date]=None, end_date:Optional[date]=None, zones:Optional[list[int]]=None) -> SchedulesEndpointResponse:
        res = await self.get_schedules_raw(
            start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
            end_date=end_date.strftime("%Y-%m-%d") if end_date else None, 
            zones=zones
        )
        return SchedulesEndpointResponse.parse_obj(res)
    
    async def set_schedule_raw(self, zones:Optional[list[int]]=None, duration:int=1, delay:Optional[int]=None, start_time:Optional[str]=None) -> ScheduleEndpointResponseRaw:
        params: dict[str,Any] = {
            "duration": duration
        }
        if zones:
            params.update({"zones": str(zones)})
        if delay:
            params.update({"delay": delay})
        if start_time:
            params.update({"start_time": start_time})
        try:
            _LOGGER.debug("Setting schedule")
            return await self._post_async('water', params)
        except Exception as e:
            _LOGGER.error("Failed to set schedule")
            raise e
        
    async def set_schedule(self, zones:Optional[list[int]]=None, duration:int=1, delay:Optional[int]=None, start_time:Optional[datetime]=None) -> SchedulesEndpointResponse:
        res = await self.set_schedule_raw(
            zones=zones, 
            duration=duration, 
            delay=delay if delay else None, 
            start_time=start_time.strftime("%Y-%m-%dT%H:%M:%S") if start_time else None
        )
        return SchedulesEndpointResponse.parse_obj(res)
    

    
    # Moistures
    async def get_moistures_raw(self, start_date:Optional[str]=None, end_date:Optional[str]=None, zones:Optional[list[int]]=None) -> MoisturesEndpointResponseRaw:
        params = {}
        if zones:
            params.update({"zones": str(zones)})
        if start_date:
            params.update({"start_date": start_date})
        if end_date:
            params.update({"end_date": end_date})
        try:
            _LOGGER.debug("Fetching moistures")
            return await self._get_async('moistures', params)
        except Exception as e:
            _LOGGER.error("Failed to fetch moistures")
            raise e
        
    async def get_moistures(self, start_date:Optional[date]=None, end_date:Optional[date]=None, zones:Optional[list[int]]=None) -> MoisturesEndpointResponse:
        res = await self.get_moistures_raw(
            start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
            end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
            zones=zones
        )
        return MoisturesEndpointResponse.parse_obj(res)
    
    async def set_moisture_raw(self, moisture:int, zones:Optional[list[int]]=None) -> MoisturesEndpointResponseRaw:
        params: dict[str,Any] = {
            "moisture": moisture
        }
        if zones:
            params.update({"zones": str(zones)})
        try:
            _LOGGER.debug("Setting moisture")
            return await self._post_async('water', params)
        except Exception as e:
            _LOGGER.error("Failed to set moisture")
            raise e
        
    async def set_moisture(self, moisture:int, zones:Optional[list[int]]=None) -> MoisturesEndpointResponse:
        res = await self.set_moisture_raw(
            moisture=moisture,
            zones=zones, 
        )
        return MoisturesEndpointResponse.parse_obj(res)
    
    
    
    # Events
    async def get_events_raw(self, start_date:Optional[str]=None, end_date:Optional[str]=None, event:Optional[int]=None) -> EventsEndpointResponseRaw:
        params = {}
        if event:
            params.update({"event": event})
        if start_date:
            params.update({"start_date": start_date})
        if end_date:
            params.update({"end_date": end_date})
        try:
            _LOGGER.debug("Fetching events")
            return await self._get_async('events', params)
        except Exception as e:
            _LOGGER.error("Failed to fetch events")
            raise e
    
    async def get_events(self, start_date:Optional[date]=None, end_date:Optional[date]=None, event:Optional[EventType]=None) -> EventsEndpointResponse:
        res = await self.get_events_raw(
                start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
                end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
                event=event.value if event else None
            )
        return EventsEndpointResponse.parse_obj(res)
    
    
    
    # Water
    async def water_raw(self, duration:int, zones:Optional[list[int]]=None, delay:Optional[int]=None, start_time:Optional[str]=None) -> ScheduleEndpointResponseRaw:
        params: dict[str,Any] = {
            "duration": duration
        }
        if zones:
            params.update({"zones": str(zones)})
        if delay:
            params.update({"delay": delay})
        if start_time:
            params.update({"start_time": start_time})
        try:
            _LOGGER.debug("Watering")
            return await self._post_async('water', params)
        except Exception as e:
            _LOGGER.error("Failed to water")
            raise e

    async def water(self, duration:int, zones:Optional[list[int]]=None, delay:Optional[int]=None, start_time:Optional[datetime]=None) -> SchedulesEndpointResponse:
        res = await self.water_raw(
            zones=zones, 
            duration=duration, 
            delay=delay if delay else None, 
            start_time=start_time.strftime("%Y-%m-%dT%H:%M:%S") if start_time else None
        )
        return SchedulesEndpointResponse.parse_obj(res)
    
    async def water_as_schedule_raw(self, zones:Optional[list[int]]=None, duration:int=1):
        return await self.set_schedule_raw(zones=zones, duration=duration)
        
    async def water_as_schedule(self, zones:Optional[list[int]]=None, duration:int=1):
        return await self.set_schedule(zones=zones, duration=duration)
    
        
    async def stop_water_raw(self):
        try:
            _LOGGER.debug("Stopping water")
            return await self._post_async('stop_water')
        except Exception as e:
            _LOGGER.error("Failed to stop water")
            raise e
        
    async def stop_water(self):
        data = await self.stop_water_raw()
        return SuccessResponse.parse_obj(data)
  
    
    async def no_water_raw(self, days:Optional[int]=None):
        try:
            _LOGGER.debug("Setting no water")
            return await self._post_async('no_water', data={
                "days": days
            })
        except Exception as e:
            _LOGGER.error("Failed to set no water")
            raise e
    
    async def no_water(self, days:Optional[int]=None):
        data = await self.no_water_raw(days=days)
        return SuccessResponse.parse_obj(data)
    
    # Weather
    async def report_weather_raw(self, 
        date: str, 
        condition: Optional[WeatherConditions],
        rain: Optional[float],
        rain_prob: Optional[float],
        temp: Optional[float],
        t_min: Optional[float],
        t_max: Optional[float],
        t_dew: Optional[float],
        wind_speed: Optional[float],
        humidity: Optional[float],
        pressure: Optional[float],
    ):
        params: dict[str, Any] = {
            "date": date
        }

        if condition:
            params.update({"condition": condition})
        if rain:
            params.update({"rain": rain})
        if rain_prob:
            params.update({"rain_prob": rain_prob})
        if temp:
            params.update({"temp": temp})
        if t_min:
            params.update({"t_min": t_min})
        if t_max:
            params.update({"t_max": t_max})
        if t_dew:
            params.update({"t_dew": t_dew})
        if wind_speed:
            params.update({"wind_speed": wind_speed})
        if humidity:
            params.update({"humidity": humidity})
        if pressure:
            params.update({"pressure": pressure})
            
        try:
            _LOGGER.debug("Reporting weather")
            return await self._post_async('report_weather', params)
        except Exception as e:
            _LOGGER.error("Failed to report weather")
            raise e

    async def report_weather(self, 
        date: date, 
        condition: Optional[WeatherConditions],
        rain: Optional[float],
        rain_prob: Optional[float],
        temp: Optional[float],
        t_min: Optional[float],
        t_max: Optional[float],
        t_dew: Optional[float],
        wind_speed: Optional[float],
        humidity: Optional[float],
        pressure: Optional[float],
    ):
        data = await self.report_weather_raw(
            date=date.strftime("%Y-%m-%d"),
            condition=condition,
            rain=rain,
            rain_prob=rain_prob,
            temp=temp,
            t_min=t_min,
            t_max=t_max,
            t_dew=t_dew,
            wind_speed=wind_speed,
            humidity=humidity,
            pressure=pressure,
        )
        return SuccessResponse.parse_obj(data)

    # Sensors
    async def get_sensor_data_raw(self, from_date: Optional[str], to_date: Optional[str]) -> SensorsEndpointResponseRaw:
        params: dict[str, Any] = {}
        if from_date:
            params.update({"from_date": from_date})
        if to_date:
            params.update({"to_date": to_date})
        try:
            _LOGGER.debug("Fetching sensor data")
            return await self._get_async('sensor_data', params)
        except Exception as e:
            _LOGGER.error("Failed to fetch sensor data")
            raise e

    async def get_sensor_data(self, from_date: Optional[date], to_date: Optional[date]) -> SensorsEndpointResponse:
        res = await self.get_sensor_data_raw(
            from_date=from_date.strftime("%Y-%m-%d") if from_date else None,
            to_date=to_date.strftime("%Y-%m-%d") if to_date else None,
        )
        return SensorsEndpointResponse.parse_obj(res)
        



    
