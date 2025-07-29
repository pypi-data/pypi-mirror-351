'''Generic NeighborManager for any communicator and discoverer'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


import logging
import queue
from typing import List, Optional

from ..communicators.impl.communicator import Communicator
from ..discoverers.impl.discoverer import Discoverer
from ..wrangler.logger import Logger
from .neighbor_manager import Event, NeighborManager
from .node_id import NodeID

log = Logger(__file__, level=logging.DEBUG).logger()


class NeighborManagerImpl(NeighborManager):
    '''Generic neighbor manager with configurable discovery.'''
    name = 'neighbor_manager_impl'
    tags = {}
    _discoverer: Discoverer
    _communicator: Communicator

    def __init__(self, discoverer: Discoverer, **kwargs):
        super().__init__(discoverer=discoverer, **kwargs)
        self._discoverer = discoverer
        # Set up a socket to listen to.
        self._communicator = self._discoverer.communicator

    def synchronize(self):
        # TODO(Merritt/Piggy): write this
        return

    def _poll_for_events(self, timeout: Optional[float] = None) -> List[Event]:
        retval = []
        # We do not use self._default_timeout for polling. If you want
        # poll_for_events to block, you must specify a timeout.
        try:
            while not self._queue.empty():
                # There is a race here between callers to poll_for_events().
                # One of the racers will raise a queue.Empty, which is safely
                # caught below.
                event = self._queue.get(block=False)
                retval.append(event)
            if timeout is not None:
                # If we have a timeout, wait the full timeout for another event.
                event = self._queue.get(timeout=timeout)
                retval.append(event)
        except queue.Empty:
            pass
        if retval:
            # Only log if we got events.
            log.debug('poll_for_events got events: %s', retval)
        return retval

    def _send_all(self, payload: bytes) -> None:
        log.debug('_send_all(%s)', payload[:50])
        self._communicator.send_all(payload)

    def _send(self, nodes: List[NodeID], payload: bytes) -> None:
        log.debug('_send: %s to %s', payload[:50], nodes)
        self._communicator.send(nodes, payload)
