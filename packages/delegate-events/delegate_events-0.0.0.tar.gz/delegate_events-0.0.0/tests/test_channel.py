# pyright: basic
from typing import Any
from time import sleep
import gc
from weakref import ref
from pytest import raises as assert_raises, fixture

from delegate.pattern import delegate
from delegate.events import Event, Channel, HandlerNotSubscribedError, HandlerAlreadySubscribedError, ChannelClosedError

class Event1(Event):
    def __init__(self, arg1: str, arg2: int):
        self.arg1 = arg1
        self.arg2 = arg2

class Event2(Event):
    def __init__(self, arg1: str, arg2: int):
        self.arg1 = arg1
        self.arg2 = arg2

class OnSomethingEvent(Event):
    def __init__(self, what: str, why: str):
        self.what = what
        self.why = why

    def __str__(self):
        return f"{self.what} happened because of {self.why}"


def test_channel_basics():
    class Class1:
        event1 = delegate(Channel[Event1])

    inst = Class1()
    msg_queue: list[tuple[object, Event]] = []

    def fn(publisher, event: Event1):
        msg_queue.append((publisher, event))

    inst.event1.subscribe(fn)
    inst.event1.fire(Event1("msg",1))

    assert len(msg_queue) == 1
    assert msg_queue[0][0] is inst


def test_channel_closing():
    class Class1:
        event1 = delegate(Channel[Event1])

    inst = Class1()

    def fn(publisher, event: Event1):
        pass

    inst.event1.close()

    with assert_raises(ChannelClosedError):
        inst.event1.close()

    with assert_raises(ChannelClosedError):
        inst.event1.subscribe(fn)

    with assert_raises(ChannelClosedError):
        inst.event1.unsubscribe(fn)

    with assert_raises(ChannelClosedError):
        inst.event1.fire(Event1("msg",2))


def test_garbage_collection():
    class Event3(Event):
        def __init__(self, arg1: str, arg2: int):
            self.arg1 = arg1
            self.arg2 = arg2

    class Class1:
        event3 = delegate(Channel[Event3])



    inst = Class1()
    channel = ref(inst.event3)
    refs_before_gc = len(gc.get_referrers(channel()))

    inst = None
    del Class1
    del Event3

    gc.collect()
    gc.collect()
    gc.collect()

    assert refs_before_gc > 0
    assert channel() is None


def test_multiple_channels():

    class Class1:
        event1 = delegate(Channel[Event1])
        event2 = delegate(Channel[Event2])

    inst = Class1()
    msg_queue: list[tuple[object, Event]] = []

    def fn(publisher, event: Event):
        msg_queue.append((publisher, event))

    inst.event1.subscribe(fn)
    inst.event2.subscribe(fn)

    inst.event1.fire(Event1("msg",1))
    inst.event2.fire(Event2("msg",2))

    assert len(msg_queue) == 2
    assert msg_queue[0][0] is inst
    assert isinstance(msg_queue[0][1], Event1)
    assert msg_queue[1][0] is inst
    assert isinstance(msg_queue[1][1], Event2)
    x=0



def test_subscriptions():

    class Class1:
        event1 = delegate(Channel[Event1])

    inst = Class1()
    msg_queue: list[tuple[object, Event1]] = []

    def fn1(publisher, event: Event1):
        msg_queue.append((publisher, event))

    def fn2(publisher, event: Event1):
        msg_queue.append((publisher, event))

    inst.event1.subscribe(fn1)

    with assert_raises(HandlerAlreadySubscribedError):
        inst.event1.subscribe(fn1)

    inst.event1.unsubscribe(fn1)

    with assert_raises(HandlerNotSubscribedError):
        inst.event1.unsubscribe(fn1)

    inst.event1 += fn1
    inst.event1 += fn2

    inst.event1.fire(Event1("msg",1))

    assert len(msg_queue) == 2
    assert msg_queue[0][0] is inst
    assert msg_queue[1][0] is inst
    assert msg_queue[0][1] is msg_queue[1][1] # events should be same instance

    inst.event1 -= fn2
    inst.event1.fire(Event1("msg",2))

    assert len(msg_queue) == 3
    assert msg_queue[2][1].arg2 ==2


def test_event_queue():

    class Class1:
        event1 = delegate(Channel[Event1])

    inst = Class1()
    msg_queue: list[tuple[object, Event1]] = []

    def fn(publisher, event: Event1):
        msg_queue.append((publisher, event))

    inst.event1.fire(Event1("msg",1)) # this msg will not be received because it has no ttl
    inst.event1.fire(Event1("msg",2), ttl=60)
    inst.event1.subscribe(fn)

    assert len(msg_queue) == 1
    assert msg_queue[0][0] is inst

    inst = Class1()
    msg_queue.clear()

    inst.event1.fire(Event1("msg",1), ttl=0.001) # this msg will not be received because it has no ttl
    sleep(0.01)
    inst.event1.subscribe(fn)

    assert len(msg_queue) == 0

def test_multiple_instances_of_same_class():

    class Class1:
        event1 = delegate(Channel[Event1])

    inst1 = Class1()
    inst2 = Class1()

    msg_queue: list[tuple[object, Event1]] = []

    def fn(publisher, event: Event1):
        msg_queue.append((publisher, event))

    inst1.event1.subscribe(fn)
    inst2.event1.subscribe(fn)

    inst1.event1.fire(Event1("msg",1))
    inst2.event1.fire(Event1("msg",2))

    assert len(msg_queue) == 2
    assert msg_queue[0][0] is inst1
    assert msg_queue[0][1].arg2 == 1
    assert msg_queue[1][0] is inst2
    assert msg_queue[1][1].arg2 == 2



def test_instances_of_different_classes():

    class Class1:
        event1 = delegate(Channel[Event1])

    class Class2:
        event1 = delegate(Channel[Event1])

    inst1 = Class1()
    inst2 = Class2()

    msg_queue: list[tuple[object, Event1]] = []

    def fn(publisher, event: Event1):
        msg_queue.append((publisher, event))

    inst1.event1.subscribe(fn)
    inst2.event1.subscribe(fn)

    inst1.event1.fire(Event1("msg",1))
    inst2.event1.fire(Event1("msg",2))

    assert len(msg_queue) == 2
    assert msg_queue[0][0] is inst1
    assert msg_queue[0][1].arg2 == 1
    assert msg_queue[1][0] is inst2
    assert msg_queue[1][1].arg2 == 2

def test_readme_example1():
    from delegate.pattern import delegate
    from delegate.events import Channel, Event

    class OnSomethingEvent(Event):
        def __init__(self, what: str, why: str):
            self.what = what
            self.why = why

        def __str__(self):
            return f"{self.what} happened because of {self.why}"

    class Class1:
        on_something = delegate(Channel[OnSomethingEvent])

    inst = Class1()
    msg_queue: list[Event] = []

    def fn(publisher, event: OnSomethingEvent):
        msg_queue.append(event)

    inst.on_something.subscribe(fn)
    inst.on_something.fire(OnSomethingEvent("Something", "some other thing"))

    event_msg = str(msg_queue[0]) # => "Something happened because of some other thing"
    assert str(event_msg) == "Something happened because of some other thing"


def test_readme_example2():
    from delegate.events import Channel

    channel = Channel[OnSomethingEvent]()

    def handler(sender: object, event: OnSomethingEvent) -> None:
        pass

    channel.subscribe(handler)
    assert True == channel.fire(OnSomethingEvent("Something", "some other thing"))


def test_readme_example3():
    from delegate.events import Channel

    channel = Channel[OnSomethingEvent]()

    msg_queue: list[Event] = []

    def handler(sender: object, event: OnSomethingEvent) -> None:
        msg_queue.append(event)

    assert False == channel.fire(OnSomethingEvent("Something", "some other thing")) # -> False
    assert False == channel.fire(OnSomethingEvent("Something", "some other thing"), ttl=10) # -> False - event stays in queue for 10 seconds though

    channel.subscribe(handler)

    assert True == channel.fire(OnSomethingEvent("Something", "some other thing")) # -> True
    assert len(msg_queue) == 2