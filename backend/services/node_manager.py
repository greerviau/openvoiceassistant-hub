class NodeManager:
    def __init__(self, config: dict):
        self.nodes = config['nodes']

    def add_node(self, node_id, config):
        self.nodes[node_id] = config
    
    def get_node_ids(self):
        return self.nodes.keys()

    def get_node_configs(self):
        return self.nodes.values()

    def get_node_config(self, id):
        return self.nodes[id]