import requests
import urllib
import typing

from backend import config

class NodeManager:
    def __init__(self, ova):
        self.ova = ova

        self.nodes = config.get('nodes')

    def update_node_config(self, node_id: str, node_config: typing.Dict):
        if self.node_exists(node_id):
            self.nodes[node_id] = node_config
            config.set('nodes', node_id, node_config)
        else:
            raise RuntimeError("Node does not exist")
        
    def add_node_config(self, node_id: str, node_config: typing.Dict):
        if not self.node_exists(node_id):
            self.nodes[node_id] = node_config
            config.set('nodes', node_id, node_config)
        else:
            raise RuntimeError("Node already exists")
        
    def sync_down_config(self, node_config: typing.Dict, hub_config: typing.Dict):
        node_api_url = node_config['node_api_url']
        resp = requests.put(f'{node_api_url}/config', data=node_config)
        if resp.status_code != 200:
            raise RuntimeError('Faied to update node config')

    def node_exists(self, node_id: str):
        return node_id in self.nodes
    
    def get_node_in_area(self, area: str):
        for id, conf in self.nodes.items():
            if area in conf['node_area']:
                return self.nodes[id]
        return {}
    
    def get_node_ids(self):
        return list(self.nodes.keys())

    def get_node_configs(self):
        return list(self.nodes.values())

    def get_node_config(self, node_id: str):
        if self.node_exists(node_id):
            return self.nodes[node_id]
        raise RuntimeError('Node does not exist')
        
    def get_all_node_status(self):
        node_status = {}
        for node_id in self.get_node_ids():
            node_status[node_id] = self.get_node_status(node_id)

        return node_status

    def get_node_status(self, node_id: str):
        try:
            node_config = self.nodes[node_id]
        except:
            raise RuntimeError('Node does not exist')
        address = node_config['node_api_url']
        try:
            resp = requests.get(address, timeout=2)
            if resp.status_code == 200:
                status = 'online'
            else:
                raise
        except:
            status = 'offline'
        
        return {
            'name': node_config['node_name'],
            'status': status
        }
    
    def call_node_api(self, verb: str, node_id: str, endpoint: str, data: typing.Dict = {}):
        if verb not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise RuntimeError('Invalid api verb')
        try:
            node_config = self.nodes[node_id]
        except:
            raise RuntimeError('Node does not exist')
        address = node_config['node_api_url']
        url = address + endpoint
        print(url)
        resp = requests.request(verb, url, timeout=2, json=data)
        return resp