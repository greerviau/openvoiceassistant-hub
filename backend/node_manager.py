import requests
from typing import Dict

from backend import config

class NodeManager:
    def __init__(self):
        self.nodes = config.get('managers', 'node_manager', 'nodes')

    def update_node_config(self, node_id: str, node_config: Dict):
        if self.node_exists(node_id):
            self.nodes[node_id] = node_config
            config.set('managers', 'node_manager', 'nodes', node_id, value=node_config)
        else:
            raise RuntimeError("Node does not exist")
        
    def add_node_config(self, node_id: str, node_config: Dict):
        if not self.node_exists(node_id):
            self.nodes[node_id] = node_config
            config.set('managers', 'node_manager', 'nodes', node_id, value=node_config)
        else:
            raise RuntimeError("Node already exists")
        
    def sync_down_config(self, node_config: Dict, hub_config: Dict):
        node_api_url = node_config['node_api_url']
        resp = requests.put(f'{node_api_url}/config', json=node_config)
        if resp.status_code != 200:
            raise RuntimeError('Faied to update node config')

    def node_exists(self, node_id: str):
        return node_id in self.nodes
    
    def get_node_ids(self):
        return self.nodes.keys()

    def get_node_configs(self):
        return self.nodes.values()

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
            resp = requests.get(address+'/status', timeout=2)
            if resp.status_code == 200:
                return 'online'
            else:
                raise
        except:
            return 'offline'