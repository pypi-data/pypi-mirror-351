"""Queue Framework

This module provides the `Queue` class, an implementation of the
standard libary's `heapq` module, for managing event queues in
the `microbial` event-handling framework.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ──
from __future__ import annotations
from abc import ABC
from collections.abc import Iterable
from datetime import datetime as dt
from datetime import timedelta as td
from heapq import (
    heapify, heappush, heappop, heapreplace, nsmallest, nlargest
)
from itertools import count
from time import sleep
from typing import Optional
from uuid import uuid4, UUID

# ─── constants ────────────────────────────────────────────────────────── ✦✦ ──

REMOVED = "<removed-event>"


# ─── interfaces ───────────────────────────────────────────────────────── ✦✦ ──

class Queue(Iterable):
    """Base class for all queues in the microbial framework."""

    def __init__(self, events: list = []) -> None:
        self._counter = count()
        self._id: UUID = uuid4()
        self._events = events
        self._entry_map = {}
        

    # : overrides
    
    def __iter__(self): 
        return iter(self._events)

    def __next__(self):
        return next(self._events)

    def __len__(self) -> int:
        return len(self._events)

    # def __contains__(self, item) -> bool:
    #     if item in self._events:
    #         return True
    #     else:
    #         return False

    def __getitem__(self, index: int) -> Optional[Event]:
        """Return an event at a specific index in the queue."""
        return (
            self._events[index] if 0 <= index < len(self._events)
            else IndexError(
                "Index out of range. Please provide a valid index."
            )
        )

    def __setitem__(self, index: int, value: Event) -> None:
        """Set an event at a specific index in the queue."""
        self._events[index] = (
            value if 0 <= index < len(self._events)
            else IndexError(
                "Index out of range. Please provide a valid index."
            )
        )

    def __delitem__(self, index: int) -> None:
        if 0 <= index < len(self._events):
            del self._events[index]
        else:
            raise IndexError(
                "Index out of range. Please provide a valid index."
            )

    def __repr__(self) -> str:
        return f"Queue(events={self._events})"

    def __str__(self) -> str:
        return f"Queue with {len(self._events)} events"

    def __eq__(self, other: object) -> bool:
        return True if self._id == other.id else False


    # : properties

    @property
    def id(self) -> UUID:
        return self._id

    @id.setter
    def id(self, value: UUID) -> None:
        """Set the queue's unique identifier."""
        if isinstance(value, UUID):
            self._id = value
        else:
            raise TypeError(
                "ID can only be set to another instance"
            )

    @id.deleter
    def id(self) -> UserWarning:
        return UserWarning("""\
⚠︎ Warning:

Queue IDs should not be deleted, as the `microbial` simulation framework's
event handling system depends on it for scheduling and managing events.
""")

    @property
    def events(self) -> [Event]:
        return self._events

    @events.setter
    def events(self, value: [Event | [Event]]) -> None:
        self._value = (
            value if isinstance(value, Event)
            else TypeError(
                "The event queue can only handle objects of type `Event`."
            )
        )

    @events.deleter
    def events(self) -> None:
        self._events = []

    @property
    def counter(self):
        return self._counter

    @counter.setter
    def counter(self, value) -> None:
        self._counter = (
            value if isinstance(value, count) else TypeError(
            "`.counter` must be an instance of `itertools.count`."
            )
        )

    @counter.deleter
    def counter(self) -> UserWarning:
        return UserWarning("""\
⚠︎ Warning:

The queue's counter should not be deleted.
""")


    # ─── instance methods ─────────────────────────────────────────────────────

    def add_event(
        self,
        event: Event,
    ) -> bool:
        """Add an event to the event queue.

        Args:
          priority (int):
            An integer representing the event's priority, where
            increasing magnitude corresponds to increasing priority.

        Returns:
            `True` if the event was successfully added to the event queue;
            otherwise raises `RuntimeError`.
        """
        seconds_from_now = (
            event.seconds_from_now if hasattr(event, 'seconds_from_now')
            else 10.0
        )

        deadline = dt.now() + td(seconds=seconds_from_now)

        self.defer_event(seconds_from_now)

        try:
            if event in self._entry_map:
                self.remove_event(event)

            count = next(self._counter)
            entry = [deadline, count, event]
            
            self._entry_map[event] = entry

            heappush(self._events, entry)

            return True
        except Exception as e:
            raise RuntimeError("Could not add event to queue.") from e


    @staticmethod
    def defer_event(duration: int | float = 10.0) -> None:
        """Sleep for a specified duration."""
        sleep(duration)


    def remove_event(self, event):
        """Mark an existing event as 'REMOVED'.

        Args:
          event (Event):
            The event to remove.

        Returns:
            `True` if the event was successfully removed from the queue;
            otherwise raises `KeyError`.
        """
        try:
            entry = self._entry_map.pop(event)
            entry[-1] = REMOVED
        except Exception as e:
            raise RuntimeError("Could not remove event from queue.") from e

    def pop_event(self) -> Optional[Event]:
        """Remove and return the lowest priority event.

        Raises `KeyError` if empty.
        """
        while self._events:
            deadline, count, event = heappop(self._events)
            if event is not REMOVED:
                del self._entry_map[event]
                return event
        raise KeyError("Attempted to pop from empty event queue.")
        

class Event(ABC):
    """Base class for all events in the simulation framework."""
    def __init__(self):
        self._id: UUID = uuid4()
        self._is_valid: bool = True
        self._timestamp: dt = dt.now()


    # : properties

    @property
    def id(self) -> UUID:
        return self._id

    @id.setter
    def id(self, value: UUID) -> None:
        self._id = (
            value if isinstance(value, UUID)
            else TypeError("`.id` must be an instance of `UUID`.")
        )

    @id.deleter
    def id(self) -> UserWarning:
        return("""\
⚠︎ Warning:

Event IDs should not be deleted. If you need to set the event's `.id`
attribute to a different unique identifier, set it to a new `UUID`
instance.
""")

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value: bool) -> None:
        self._is_valid = (
            value if isinstance(value, bool)
            else TypeError("`.is_valid` must be a boolean value.")
        )

    @is_valid.deleter
    def is_valid(self) -> None:
        self._is_valid = False


class ReplicationEvent(Event):
    """An event representing a replication action in the simulation."""
    def __init__(self, entity_id: UUID, seconds_from_now: int | float = 10.0):
        super().__init__()
        self._entity_id: UUID = entity_id
        self._seconds_from_now = seconds_from_now

    @property
    def entity_id(self) -> UUID:
        return self._entity_id

    @property
    def seconds_from_now(self) -> float:
        return self._seconds_from_now
