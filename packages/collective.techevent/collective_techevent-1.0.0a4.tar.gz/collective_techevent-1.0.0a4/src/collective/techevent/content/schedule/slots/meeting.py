from collective.techevent.content.schedule.slot import ISlot
from collective.techevent.content.schedule.slot import Slot
from zope.interface import implementer


class IMeeting(ISlot):
    """A Meeting in the event."""


@implementer(IMeeting)
class Meeting(Slot):
    """Convenience subclass for ``Meeting`` portal type."""
