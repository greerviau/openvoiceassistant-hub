import requests
import urllib
import typing

from backend import config

class NodeManager:
    def __init__(self, ova):
        self.ova = ova
        self.nodes = config.get('nodes')

    def update_node_config(self, node_id: str, node_config: typing.Dict):
        return config.set('nodes', node_id, node_config)
        
    def node_exists(self, node_id: str):
        return node_id in self.nodes
    
    def get_node_in_area(self, area: str):
        for id, conf in self.nodes.items():
            if area in conf['area']:
                return self.nodes[id]
        return {}
    
    def get_node_ids(self):
        return list(self.nodes.keys())

    def get_node_configs(self):
        return list(self.nodes.values())

    def get_node_config(self, node_id: str):
        if self.node_exists(node_id):
            return self.nodes[node_id]
        raise RuntimeError(f"Node {node_id} does not exist")
        
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

    def get_node_status(self, node_id: str):
        try:
            node_config = self.nodes[node_id]
        except:
            raise RuntimeError(f"Node {node_id} does not exist")
        address = node_config['api_url']
        try:
            resp = requests.get(address, timeout=2)
            if resp.status_code == 200 and resp.json()["id"] == node_id:
                status = 'online'
            else:
                raise
        except:
            status = 'offline'
        
        return {
            'id': node_id,
            'name': node_config['name'],
            'status': status,
            'restart_required': node_config['restart_required']
        }
    
    def delete_node(self, node_id: str):
        if self.node_exists(node_id):
            del self.nodes[node_id]
            config.set('nodes', self.nodes)

    def restart_node(self, node_id: str):
        if self.node_exists(node_id):
            resp = self.call_node_api('POST', node_id, '/restart')
            if resp.status_code != 200:
                raise RuntimeError(f"Failed to restart node {node_id}")
            self.nodes[node_id]["restart_required"] = False
    
    def call_node_api(self, verb: str, node_id: str, endpoint: str, data: typing.Dict = {}):
        verb = verb.upper()
        if verb not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise RuntimeError('Invalid api verb')
        try:
            node_config = self.nodes[node_id]
        except:
            raise RuntimeError(f"Node {node_id} does not exist")
        address = node_config['api_url']
        url = address + endpoint
        print(url)
        resp = requests.request(verb, url, timeout=10, json=data)
        return resp