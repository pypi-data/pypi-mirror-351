import sys
import types
import cloudpickle
from semiauto_classification.custom_transformers import TRANSFORMER_REGISTRY

class CustomUnpickler(cloudpickle.CloudPickler):
    def find_class(self, module, name):
        if name in TRANSFORMER_REGISTRY:
            return TRANSFORMER_REGISTRY[name]
        return super().find_class(module, name)

def load_pipeline(filepath):
    """Load a pipeline with custom class resolution"""
    with open(filepath, 'rb') as f:
        unpickler = CustomUnpickler(f)
        return unpickler.load()