from datetime import datetime

from delegate.events.core.event import Event

class QueuedEvent:
    __slots__ = [ "__event", "__expires" ]

    def __init__(self, event: Event, expires: datetime) -> None:
        self.__event = event
        self.__expires = expires

    @property
    def event(self) -> Event:
        return self.__event

    @property
    def expired(self) -> bool:
        return self.__expires < datetime.now()