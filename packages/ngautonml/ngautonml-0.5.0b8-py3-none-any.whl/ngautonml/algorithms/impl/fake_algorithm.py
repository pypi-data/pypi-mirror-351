'''A fake algorithm used for tests.'''

from typing import Optional

from .algorithm import Algorithm
from .fittable_algorithm_instance import FittableAlgorithmInstance

from ...wrangler.dataset import Dataset


# TODO(Merritt/Piggy): possibly unify this with more uses of FakeAlgorithm in tests
class FakeAlgorithm(Algorithm):
    '''A fake algorithm used for tests.'''
    _name = 'fake_algorithm'

    def instantiate(self, **hyperparams) -> 'FakeInstance':
        return FakeInstance(parent=self, **hyperparams)


FAKE_SERIALIZED = b'fake serialized algorithm'


class FakeInstance(FittableAlgorithmInstance):
    '''An instance of FakeAlgorithm for tests.'''
    evidence_of_deserialize = None

    def __init__(self, parent, **kwargs):
        super().__init__(parent=parent, **kwargs)

    def deserialize(self, serialized_model: bytes) -> 'FakeInstance':
        self.evidence_of_deserialize = serialized_model
        return self

    def serialize(self) -> bytes:
        return FAKE_SERIALIZED

    def fit(self, dataset: Optional[Dataset]) -> None:
        _ = dataset
        self._trained = True

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        return dataset
