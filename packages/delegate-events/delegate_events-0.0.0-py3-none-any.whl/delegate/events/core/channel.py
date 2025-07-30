from __future__ import annotations
from typing import Generic, TypeVar, MutableSequence, Callable, cast, overload
from datetime import datetime, timedelta
from threading import RLock
from weakref import ref

from delegate.events.core.channel_closed_error import ChannelClosedError
from delegate.events.core.event import Event
from delegate.events.core.queued_event import QueuedEvent
from delegate.events.core.handler_already_subscribed_error import HandlerAlreadySubscribedError
from delegate.events.core.handler_not_subscribed_error import HandlerNotSubscribedError

T = TypeVar("T", bound=Event, contravariant=True)
class Channel(Generic[T]):
    __slots__ = [ "__publisher", "__subscribers", "__queue", "__queue_lock", "__weakref__", "__closed" ]

    @overload
    def __init__(self) -> None:
        """
        Creates a channel without a publisher. This is meant for testing purposes.
        """
        ...
    @overload
    def __init__(self, delegator: object) -> None:
        """
        Creates a delegate channel for specific publisher (delegator).
        """
        ...
    def __init__(self, delegator: object | None = None):
        self.__publisher = ref(delegator) if delegator is not None else None
        self.__subscribers: MutableSequence[Callable[[object, T], None]] = []
        self.__queue: MutableSequence[QueuedEvent] = []
        self.__queue_lock = RLock()
        self.__closed = False

    def subscribe(self, handler: Callable[[object, T], None]) -> None:
        """
        Subscribes to the event channel.

        Args:
            handler (Callable[[object, T], None]): The event handler
        """
        if self.__closed:
            raise ChannelClosedError

        if handler in self.__subscribers:
            raise HandlerAlreadySubscribedError

        self.__subscribers.append(handler)

        with self.__queue_lock:
            for event in self.__queue:
                if not event.expired:
                    self.fire(cast(T, event.event))
            self.__queue.clear()


    def unsubscribe(self, handler: Callable[[object, T], None]) -> None:
        """
        Unsubscribes handler from event channel.

        Args:
            handler (Callable[[object, T], None]): The event handler
        """
        if self.__closed:
            raise ChannelClosedError

        if handler not in self.__subscribers:
            raise HandlerNotSubscribedError

        self.__subscribers.remove(handler)

    def fire(self, event: T, *, ttl: float | None = 0) -> bool:
        """
        Fires the event, invoking all subscribed handlers

        Args:
            event (Event): The event
            ttl (float, optional): The time (seconds) the event may live in the queue while awaiting subcriptions
        Returns:
            bool: Returns True when event was successfully sent to one or more subscribers.
        """
        if self.__closed:
            raise ChannelClosedError

        if not self.__subscribers:
            if ttl:
                with self.__queue_lock:
                    self.__queue.append(QueuedEvent(event, datetime.now() + timedelta(seconds = ttl)))

            return False

        for subscriber in self.__subscribers:
            subscriber(self.__publisher() if self.__publisher else None, event)

        return True

    def close(self) -> None:
        """
        Closes the channel.

        Raises:
            ChannelClosedError: _description_
        """
        if self.__closed:
            raise ChannelClosedError

        self.__closed = True
        self.__subscribers.clear()
        self.__queue.clear()

    def __iadd__(self, handler: Callable[[object, T], None]) -> Channel[T]:
        self.subscribe(handler)
        return self

    def __isub__(self, handler: Callable[[object, T], None]) -> Channel[T]:
        self.unsubscribe(handler)
        return self