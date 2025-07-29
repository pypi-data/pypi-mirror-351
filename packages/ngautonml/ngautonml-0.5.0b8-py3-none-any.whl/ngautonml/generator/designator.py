'''A designator identifying a specific step or pipeline.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


class Designator(str):
    '''A unique designator identifying a specific pipeline.

    It is also used in the filename when saving that pipeline to disk.
    '''
    def __str__(self) -> str:
        return self.lower()


class StepDesignator(str):
    '''A unique designator identifying a specific step in a specific pipeline.

    It is also used in the filename when saving the model in that step to disk.'''
    def __str__(self) -> str:
        return self.lower()
