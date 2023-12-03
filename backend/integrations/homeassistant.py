import typing
import requests
import datetime

class HomeAssistant:
    def __init__(self, config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        
        self.config = config
        host = config["host"]
        port = config["port"]
        acccess_token = config["acccess_token"]
        self.headers = {"content-type": "application/json", "Authorization": f"Bearer {acccess_token}"}
        self.api = f"http://{host}:{port}/api"

    # GET ENDPOINTS

    def get_api(self):
        resp = requests.get(f"{self.api}/", headers=self.headers)
        resp.raise_for_status()
        return resp.json()
    
    def get_custom(self, endpoint: str):
        resp = requests.get(f"{self.api}/{endpoint}", headers=self.headers)
        resp.raise_for_status()
        return resp.json()
    
    def get_config(self):
        resp = requests.get(f"{self.api}/config", headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_events(self):
        resp = requests.get(f"{self.api}/events", headers=self.headers)
        resp.raise_for_status()
        return resp.json()
    
    def get_services(self):
        resp = requests.get(f"{self.api}/services", headers=self.headers)
        resp.raise_for_status()
        return resp.json()
    
    def get_history_period(self, 
                            filter_entity_ids: list[str], 
                            timestamp: datetime.datetime = None,
                            end_time: datetime.datetime = None, 
                            minimal_response: bool = False, 
                            no_attributes: bool = False, 
                            significant_changes_only: bool = False
    ):
        ts = timestamp.strftime("%Y-%m-%dT%H:%M:%S%z") if timestamp else ""
        et = end_time.strftime("%Y-%m-%dT%H:%M:%S%z") if timestamp else ""

        ext = f"/{ts}" if ts else ""

        params = f"?filter_entity_id={','.join(filter_entity_ids)}"
        params += f"&end_time={et}" if et else ""
        params += "&minimal_response" if minimal_response else ""
        params += "&no_attributes" if no_attributes else ""
        params += "&significant_changes_only" if significant_changes_only else ""

        resp = requests.get(f"{self.api}/history/period{ext}{params}", headers=self.headers)
        resp.raise_for_status()
        return resp.json()
    
    def get_logbook(self, 
                    timestamp: datetime.datetime = None,
                    entity_id: str = '',
                    end_time:  datetime.datetime = None
    ):
        ts = timestamp.strftime("%Y-%m-%dT%H:%M:%S%z") if timestamp else ""
        et = end_time.strftime("%Y-%m-%dT%H:%M:%S%z") if timestamp else ""

        ext = f"/{ts}" if ts else ""

        params = ""
        if end_time:
            params = f"?end_time={et}"
            if entity_id:
                params += f"&entity={entity_id}"
        elif entity_id:
            params = f"&entity={entity_id}"
            
        resp = requests.get(f"{self.api}/logbook{ext}{params}", headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_states(self, 
                   entity_id: str = ""
    ):
        ext = f"/{entity_id}" if entity_id else ""

        resp = requests.get(f"{self.api}/states{ext}", headers=self.headers)
        resp.raise_for_status()
        return resp.json()
    
    def get_error_log(self):
        resp = requests.get(f"{self.api}/error_log", headers=self.headers)
        resp.raise_for_status()
        return resp.content
    
    def get_camera_proxy(self, 
                         camera_entity_id: str
    ):
        resp = requests.get(f"{self.api}/camera_proxy/{camera_entity_id}", headers=self.headers)
        resp.raise_for_status()
        return resp.content
    
    def get_calendars(self, 
                      calendar_entity_id: str = ''
    ):
        ext = f"/{calendar_entity_id}" if calendar_entity_id else ""

        resp = requests.get(f"{self.api}/calendars{ext}", headers=self.headers)
        resp.raise_for_status()
        return resp.json()
    
    # POST ENDPOINTS

    def post_states(self, entity_id: str, state: typing.Dict):
        return requests.post(f"{self.api}/states/{entity_id}", headers=self.headers, json=state)

    def post_events(self, event_type: str, event_data: typing.Dict = None):
        if event_data:
            return requests.post(f"{self.api}/events/{event_type}", headers=self.headers, json=event_data)
        else:
            return requests.post(f"{self.api}/events/{event_type}", headers=self.headers)

    def post_services(self, domain: str, service: str, service_data: typing.Dict = None):
        if service_data:
            return requests.post(f"{self.api}/services/{domain}/{service}", headers=self.headers, json=service_data)
        else:
            return requests.post(f"{self.api}/events/{domain}/{service}", headers=self.headers)

    def post_template(self, template: typing.Dict):
        return requests.post(f"{self.api}/template", headers=self.headers, json=template)

    def post_config_core_check_config(self):
        return requests.post(f"{self.api}/config/core/check_config", headers=self.headers)

    def post_intent_handle(self, data: typing.Dict):
        return requests.post(f"{self.api}/intent/handle", headers=self.headers, json=data)

def build_integration(config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return HomeAssistant(config, ova)

def default_config():
    return {
        "host": "",
        "port": 8123,
        "acccess_token": ""
    }