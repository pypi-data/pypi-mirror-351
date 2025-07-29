# flake8: noqa
# type: ignore
# pylint: skip-file

# ngautonml's distributed AI implementation is adapted from this code made by Kyle Miller
# We are keeping it here for now to compare and make sure we adapted it right.
# There is a test that compares the ngautonml implementation.

from typing import Any

class DistAIModel:
    def __init__(self):
        self.fit_time = None
        self.ID = None

    def serialize(self): # returns serialized model
        # care should be taken to make message size as small as possible. self.ID is required.
        # the deserialized model must be able to run norm2, inner_product, and metrics. It need not run fit.
        pass

    @staticmethod
    def deserialize(serialized_model): # returns model instance
        # care should be taken to make message size as small as possible. self.ID is required.
        # the deserialized model must be able to run norm2, inner_product, and metrics. It need not run fit.
        pass

    def fit(self, data, neighbor_models): # returns nothing, fits model to data and other models
        pass

    def norm2(self): # returns scalar
        pass

    def inner_product(self,other): # returns scalar
        pass

    def metrics(self,data): # returns a dictionary with string keys recording any sort of metrics Dict[str, Any]
        pass

def register(catalog: Any, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
