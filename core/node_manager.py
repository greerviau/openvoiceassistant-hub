import requests
import typing

from core import config

class NodeManager:
    def __init__(self, ova):
        self.ova = ova
        self.nodes = config.get('nodes')

    def update_node_config(self, node_id: str, node_config: typing.Dict):
        self.__save_config(node_id, node_config)
        return node_config
        
    def node_exists(self, node_id: str):
        return node_id in self.nodes
    
    def get_node_in_area(self, area: str):
        for node_id, conf in self.nodes.items():
            if area in conf['area']:
                return self.nodes[node_id]
        return {}
    
    def get_node_ids(self):
        return list(self.nodes.keys())

    def get_node_configs(self):
        return list(self.nodes.values())

    def get_node_config(self, node_id: str):
        if self.node_exists(node_id):
            return self.nodes[node_id]
        raise RuntimeError(f"Node {node_id} does not exist")

    def check_for_config_discrepancy(self, node_id: str, node_config: typing.Dict):
        existing_node_config = self.nodes[node_id]
        if list(existing_node_config.keys()) == list(node_config.keys()):
            return existing_node_config
        update_needed = False
        for key, value in node_config.items():
            if key not in existing_node_config:
                existing_node_config[key] = value
                update_needed = True
        if update_needed:
            self.__save_config(node_id, existing_node_config)
        return existing_node_config
        
    def get_all_node_status(self):
        node_status = []
        for node_id in self.get_node_ids():
            node_status.append(self.get_node_status(node_id))

        return node_status
    
    def get_node_hardware(self, node_id: str):
        hardware = {}
        resp = self.call_node_api("GET", node_id, "/microphones")
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to get microphones from node {node_id}")
        hardware["microphones"] = resp.json()
        resp = self.call_node_api("GET", node_id, "/speakers")
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to get speakers from node {node_id}")
        hardware["speakers"] = resp.json()
        return hardware

    def get_node_wake_words(self, node_id: str):
        resp = self.call_node_api("GET", node_id, "/wake_word_models")
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to get wake words from node {node_id}")
        return resp.json()

    def get_node_status(self, node_id: str):
        try:
            node_config = self.nodes[node_id]
        except:
            raise RuntimeError(f"Node {node_id} does not exist")
        try:
            resp = self.call_node_api("GET", node_id, "")
            if resp.status_code == 200 and resp.json()["id"] == node_id:
                status = 'online'
            else:
                raise
        except Exception as e:
            #print(e)
            status = 'offline'
        
        return {
            'id': node_id,
            'name': node_config['name'],
            'status': status,
            'restart_required': node_config['restart_required']
        }
    
    def remove_node(self, node_id: str):
        if self.node_exists(node_id):
            node_config = self.nodes.pop(node_id)
            config.set('nodes', self.nodes)
            return node_config
        raise RuntimeError("Node does not exist")

    def restart_node(self, node_id: str):
        if self.node_exists(node_id):
            node_config = self.nodes[node_id]
            resp = self.call_node_api('POST', node_id, '/restart')
            if resp.status_code != 200:
                raise RuntimeError(f"Failed to restart node {node_id}")
            node_config["restart_required"] = False
            self.__save_config(node_id, node_config)
    
    def call_node_api(self, 
                        verb: str, 
                        node_id: str, 
                        endpoint: str, 
                        files: typing.Dict = None, 
                        json: typing.Dict = None, 
                        data: typing.Dict = None
    ):
        verb = verb.upper()
        if verb not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise RuntimeError('Invalid api verb')
        try:
            node_config = self.nodes[node_id]
        except:
            raise RuntimeError(f"Node {node_id} does not exist")
        address = node_config['api_url']
        url = address + endpoint
        try:
            resp = requests.request(verb, url, timeout=5, files=files, json=json, data=data)
        except:
            raise RuntimeError(f"Failed to make request to {endpoint} on node {node_id} | Timed out")
        return resp

    def __save_config(self, node_id: str, node_config: typing.Dict):
        self.nodes[node_id] = node_config
        config.set('nodes', node_id, node_config)