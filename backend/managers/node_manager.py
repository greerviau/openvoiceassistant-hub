class NodeManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.nodes = config_manager.get('nodes')

    def set_node(self, node_id, config):
        self.nodes[node_id] = config
        self.config_manager.set('nodes', node_id, value=config)
    
    def node_exists(self, node_id):
        return node_id in self.nodes
    
    def get_node_ids(self):
        return self.nodes.keys()

    def get_node_configs(self):
        return self.nodes.values()

    def get_node_config(self, id):
        return self.nodes[id]