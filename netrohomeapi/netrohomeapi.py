from datetime import date, datetime
from typing import List
from aiohttp import ClientSession
import logging

from .models import (
    DeviceStatus,
    EventType,
    EventsEndpointResponse,
    InfoEndpointResponse,
    MoisturesEndpointResponse,
    SchedulesEndpointResponse,
    SuccessResponse
)

_LOGGER = logging.getLogger(__name__)

class NetroHomeAPI:
    BASE_URL = 'http://api.netrohome.com/npa/v1'

    def __init__(self, api_key, session: ClientSession = None):
        self.api_key = api_key
        self.session = ClientSession() if not session else session
        
    def _get_url(self, endpoint):
        return f"{self.BASE_URL}/{endpoint}.json"

    
    async def _get_async(self, endpoint, params={}):
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
            return await response.json()
    
    async def _post_async(self, endpoint, data={}):
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
            return await response.json()

    
    
    # Device
    async def get_info_raw(self):
        try:
            _LOGGER.debug("Fetching info")
            return await self._get_async('info')
        except Exception as e:
            _LOGGER.error("Failed to fetch info")
            raise e
        
    async def get_info(self) -> InfoEndpointResponse:
        res = await self.get_info_raw()
        return InfoEndpointResponse.parse_obj(res)

    async def set_device_status_raw(self, status:str):
        try:
            _LOGGER.debug("Setting status")
            return await self._post_async('set_status', data={
                "status": status
            })
        except Exception as e:
            _LOGGER.error("Failed to set status")
            raise e
        
    async def set_device_status(self, status:DeviceStatus):
        data = await self.set_device_status_raw(status.value)
        return SuccessResponse.parse_obj(data)
        
    
    
    # Schedules
    async def get_schedules_raw(self, start_date:str=None, end_date:str=None, zones:List[int]=None):
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
    
    async def get_schedules(self, start_date:date=None, end_date:date=None, zones:List[int]=None) -> SchedulesEndpointResponse:
        res = await self.get_schedules_raw(
            start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
            end_date=end_date.strftime("%Y-%m-%d") if end_date else None, 
            zones=zones
        )
        return SchedulesEndpointResponse.parse_obj(res)
    
    async def set_schedule_raw(self, zones:List[int]=None, duration:int=1, delay:int=None, start_time:str=None):
        params = {
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
        
    async def set_schedule(self, zones:List[int]=None, duration:int=1, delay:int=None, start_time:datetime=None):
        res = await self.set_schedule_raw(
            zones=zones, 
            duration=duration, 
            delay=delay if delay else None, 
            start_time=start_time.strftime("%Y-%m-%dT%H:%M:%S") if start_time else None
        )
        return SchedulesEndpointResponse.parse_obj(res)
    

    
    # Moistures
    async def get_moistures_raw(self, start_date:str=None, end_date:str=None, zones:List[int]=None):
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
        
    async def get_moistures(self, start_date:date=None, end_date:date=None, zones:List[int]=None) -> MoisturesEndpointResponse:
        res = await self.get_moistures_raw(
            start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
            end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
            zones=zones
        )
        return MoisturesEndpointResponse.parse_obj(res)
    
    async def set_moisture_raw(self, moisture:int, zones:List[int]=None):
        params = {
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
        
    async def set_moisture(self, zones:List[int]=None, duration:int=1, delay:int=None, start_time:datetime=None):
        res = await self.set_moisture_raw(
            zones=zones, 
            duration=duration, 
            delay=delay if delay else None, 
            start_time=start_time.strftime("%Y-%m-%dT%H:%M:%S") if start_time else None
        )
        return MoisturesEndpointResponse.parse_obj(res)
    
    
    
    # Events
    async def get_events_raw(self, start_date:str=None, end_date:str=None, event:int=None):
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
    
    async def get_events(self, start_date:date=None, end_date:date=None, event:EventType=None):
        res = await self.get_events_raw(
                start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
                end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
                event=event.value if event else None
            )
        return EventsEndpointResponse.parse_obj(res)
    
    
    
    # Water
    async def water_raw(self, zones:List[int]=None, duration:int=1):
        await self.set_schedule_raw(zones=zones, duration=duration)
        
    async def water(self, zones:List[int]=None, duration:int=1):
        await self.set_schedule(zones=zones, duration=duration)
    
        
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
  
    
    async def no_water_raw(self, days:int=None):
        try:
            _LOGGER.debug("Setting no water")
            return await self._post_async('no_water', data={
                "days": days
            })
        except Exception as e:
            _LOGGER.error("Failed to set no water")
            raise e
    
    async def no_water(self, days:int=None):
        data = await self.no_water_raw(days=days)
        return SuccessResponse.parse_obj(data)
    




    

    





    
