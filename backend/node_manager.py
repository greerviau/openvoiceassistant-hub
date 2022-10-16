import requests

from backend.config import Configuration

class NodeManager:
    def __init__(self, config: Configuration):
        self.config = config
        self.nodes = config.get('managers', 'node_manager', 'nodes')

    def update_node_config(self, node_id: str, config: dict):   # TODO use TypedDict
        self.nodes[node_id] = config
        self.config.setkey('managers', 'node_manager', 'nodes', node_id, value=config)
    
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
            config = self.nodes[node_id]
        except:
            raise RuntimeError('Node does not exist')
        address = config['address']
        try:
            resp = requests.get(address+'/status', timeout=2)
            if resp.status_code == 200:
                return 'online'
            else:
                raise
        except:
            return 'offline'