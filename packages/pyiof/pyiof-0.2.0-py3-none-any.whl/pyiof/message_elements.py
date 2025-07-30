import datetime
from typing import List, Literal, Optional

from pydantic import conlist

from .class_ import Class_
from .competitor import Competitor, ControlCard, Organisation, PersonEntry, TeamEntry
from .course import RaceCourseData
from .event import Event
from .misc import OrganisationServiceRequest, PersonServiceRequest
from .result import ClassResult
from .start import ClassStart
from .xml_base import BaseXmlModel, attr, element


class BaseMessageElement(BaseXmlModel):
    iof_version: Literal["3.0"] = attr(name="iofVersion", default="3.0")
    create_time: Optional[datetime.datetime] = attr(name="createTime", default=None)
    creator: Optional[str] = attr(default=None)


class CompetitorList(BaseMessageElement):
    """A list of competitors. This is used to exchange a "brutto" list of
    possible competitors. This should not be used to exchange entries;
    use EntryList instead.
    """

    competitors: List[Competitor] = element(tag="Competitor", default_factory=list)


class OrganisationList(BaseMessageElement):
    """A list of organisations, including address and contact information."""

    organisations: List[Organisation] = element(tag="Organisation", default_factory=list)


class EventList(BaseMessageElement):
    """A list of events. This can be used to exchange fixtures."""

    events: List[Event] = element(tag="Event", default_factory=list)


class ClassList(BaseMessageElement):
    """A list of classes"""

    classes: List[Class_] = element(tag="Class", default_factory=list)


class EntryList(BaseMessageElement):
    """A list of persons and/or teams which are registered for a particular event."""

    event: Event = element(tag="Event")
    team_entries: List[TeamEntry] = element(tag="TeamEntry", default_factory=list)
    person_entries: List[PersonEntry] = element(tag="PersonEntry", default_factory=list)


class CourseData(BaseMessageElement):
    """This element defines all the control and course information for an event or race.
    Used when transferring courses from course-setting software to event administration software.
    """

    event: Event = element(tag="Event")
    race_course_data: conlist(item_type=RaceCourseData, min_length=1) = element(  # type: ignore
        tag="RaceCourseData"
    )


class StartList(BaseMessageElement):
    """Contains information about the start lists for the classes in an event."""

    event: Event = element(tag="Event")
    class_starts: List[ClassStart] = element(tag="ClassStart", default_factory=list)


class ResultList(BaseMessageElement):
    """Contains information about the result lists for the classes in an event."""

    event: Event = element(tag="Event")
    class_results: List[ClassResult] = element(tag="ClassResult", default_factory=list)
    status: Literal["Complete", "Delta", "Snapshot"] = attr(default="Complete")


class ServiceRequestList(BaseMessageElement):
    """A list of service requests."""

    event: Event = element(tag="Event")
    organisation_service_requests: List[OrganisationServiceRequest] = element(
        tag="OrganisationServiceRequest", default_factory=list
    )
    person_service_requests: List[PersonServiceRequest] = element(
        tag="PersonServiceRequest", dafault_factory=list
    )


class ControlCardList(BaseMessageElement):
    """Defines control card ownership, e.g. for rental control card handling purposes."""

    owner: Optional[str] = element(tag="Owner", default=None)
    control_cards: List[ControlCard] = element(tag="ControlCard", default_factory=list)
