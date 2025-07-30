import datetime
from typing import List, Literal, Optional

from .base import DateAndOptionalTime, GeoPosition, Id
from .class_ import Class_
from .contact import EntryReceiver, Organisation, Role
from .fee import Account
from .misc import EventURL, InformationItem, Schedule, Service
from .xml_base import BaseXmlModel, attr, element

EventStatus = Literal["Planned", "Applied", "Proposed", "Sanctioned", "Canceled", "Rescheduled"]

EventClassification = Literal["International", "National", "Regional", "Local", "Club"]

EventForm = Literal["Individual", "Team", "Relay"]

RaceDiscipline = Literal["Sprint", "Middle", "Long", "Ultralong", "Other"]


class Race(BaseXmlModel):
    """An event consists of a number of races. The number is equal to the number of
    times a competitor should start.
    """

    race_number: int = element(tag="RaceNumber")
    name: str = element(tag="Name")
    start_time: Optional[DateAndOptionalTime] = element(tag="StartTime", default=None)
    end_time: Optional[DateAndOptionalTime] = element(tag="EndTime", default=None)
    status: Optional[EventStatus] = element(tag="Status", default=None)
    classification: Optional[EventClassification] = element(tag="Classification", default=None)
    position: Optional[GeoPosition] = element(tag="Position", default=None)
    discipline: List[RaceDiscipline] = element(tag="Discipline", default_factory=list)
    organisers: List[Organisation] = element(tag="Organiser", default_factory=list)
    officials: List[Role] = element(tag="Official", default_factory=list)
    services: List[Service] = element(tag="Service", default_factory=list)
    url: List[EventURL] = element(tag="URL", default_factory=list)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class Event(BaseXmlModel):
    id: Optional[Id] = element(tag="Id", default=None)
    name: str = element(tag="Name")
    start_time: Optional[DateAndOptionalTime] = element(tag="StartTime", default=None)
    end_time: Optional[DateAndOptionalTime] = element(tag="EndTime", default=None)
    event_status: Optional[EventStatus] = element(tag="Status", default=None)
    classification: Optional[EventClassification] = element(tag="Classification", default=None)
    forms: List[EventForm] = element(tag="Form", default_factory=list)
    organisers: List[Organisation] = element(tag="Organiser", default_factory=list)
    officials: List[Role] = element(tag="Official", default_factory=list)
    classes: List[Class_] = element(tag="Class", default_factory=list)
    races: List[Race] = element(tag="Race", default_factory=list)
    entry_receiver: Optional[EntryReceiver] = element(tag="EntryReceiver", default=None)
    services: List[Service] = element(tag="Service", default_factory=list)
    accounts: List[Account] = element(tag="Account", default_factory=list)
    urls: List[EventURL] = element(tag="URL", default_factory=list)
    information: List[InformationItem] = element(tag="Information", default_factory=list)
    schedules: List[Schedule] = element(tag="Schedule", default_factory=list)
    news: List[InformationItem] = element(tag="News", default_factory=list)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)
