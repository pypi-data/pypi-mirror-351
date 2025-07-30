from uuid import UUID
from mumle.state.base import State
from mumle.services.bottom.V0 import Bottom


class Bytes:
    def __init__(self, model: UUID, state: State):
        self.model = model
        self.bottom = Bottom(state)
        type_model_id_node, = self.bottom.read_outgoing_elements(state.read_root(), "Bytes")
        self.type_model = UUID(self.bottom.read_value(type_model_id_node))

    def create(self, value: bool):
        if "bytes" in self.bottom.read_keys(self.model):
            instance, = self.bottom.read_outgoing_elements(self.model, "bytes")
            self.bottom.delete_element(instance)
        _instance = self.bottom.create_node(value)
        self.bottom.create_edge(self.model, _instance, "bytes")
        _type, = self.bottom.read_outgoing_elements(self.type_model, "Bytes")
        self.bottom.create_edge(_instance, _type, "Morphism")

    def read(self):
        instance, = self.bottom.read_outgoing_elements(self.model, "bytes")
        return self.bottom.read_value(instance)
