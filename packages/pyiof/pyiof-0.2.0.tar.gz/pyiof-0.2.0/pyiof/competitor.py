import datetime
from typing import List, Literal, Optional

from .base import Id, Score
from .class_ import Class_
from .contact import Organisation, Person
from .fee import AssignedFee
from .misc import ServiceRequest
from .xml_base import BaseXmlModel, attr, element


class ControlCard(BaseXmlModel):
    """ControlCard

    Attributes:
        id (str): The unique identifier of the control card, i.e. card number.
        punchingsystem (str, optional): The manufacturer of the punching
                                        system, e.g. 'SI' or 'Emit'.
        modifytime (datetime, optional)
    """

    id: str
    punching_system: Optional[str] = attr(name="punchingSystem", default=None)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class Competitor(BaseXmlModel):
    """Represents information about a person in a competition context,
    i.e. including organisation and control card.

    Attributes:
        person: Person
        organisation (List[Organisation]): The organisations that the
            person is member of.
        controlcards (List[ControlCard]): The default control cards of the competitor.
        class_ (List[Claas_]): The default classes of the competitor.
        score (List[Score]): Any scores, e.g. ranking scores, for the person.
        modifytime (datetime.datetime, optional)
    """

    person: Person = element(tag="Person")
    organisation: List[Organisation] = element(tag="Organisation", default_factory=list)
    controlcards: List[ControlCard] = element(tag="ControlCard", default_factory=list)
    class_: List[Class_] = element(tag="Class", default_factory=list)
    score: List[Score] = element(tag="Score", default_factory=list)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class StartTimeAllocationRequest(BaseXmlModel):
    """Used to state start time allocation requests. It consists of a possible
    reference Organisation or Person and the allocation request, e.g. late start
    or grouped with the reference Organisation/Person. This way it is possible
    to state requests to the event organizer so that e.g. all members of an
    organisation has start times close to each other - or parents have start
    times far from each other. It is totally up to the event software and
    organizers whether they will support such requests.
    """

    organisation: Optional[Organisation] = element(tag="Organisation", default=None)
    person: Optional[Person] = element(tag="Person", default=None)
    type: Optional[Literal["Normal", "EarlyStart", "LateStart", "SeparatedFrom", "GroupedWith"]] = (
        attr(default="Normal")
    )


class PersonEntry(BaseXmlModel):
    """
    Defines an event entry for a person.
    """

    id: Optional[Id] = element(tag="Id", default=None)
    person: Person = element(tag="Person")
    organisation: Optional[Organisation] = element(tag="Organisation", default=None)
    controlcards: List[ControlCard] = element(tag="ControlCard", default_factory=list)
    scores: List[Score] = element(tag="Score", default_factory=list)
    classes: List[Class_] = element(tag="Class", default_factory=list)
    race_number: List[int] = element(tag="RaceNumber", default_factory=list)
    assigned_fee: List[AssignedFee] = element(tag="AssignedFee", default_factory=list)
    service_requests: List[ServiceRequest] = element(tag="ServiceRequest", default_factory=list)
    starttime_allocation_request: Optional[StartTimeAllocationRequest] = element(
        tag="StartTimeAllocationRequest", default=None
    )
    entry_time: Optional[datetime.datetime] = element(tag="EntryTime", default=None)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class TeamEntryPerson(BaseXmlModel):
    """Defines a person that is part of a team entry."""

    person: Optional[Person] = element(tag="Person", default=None)
    organisation: Optional[Organisation] = element(tag="Organisation", default=None)
    leg: Optional[int] = element(tag="Leg", default=None)
    leg_order: Optional[int] = element(tag="LegOrder", default=None)
    control_card: List[ControlCard] = element(tag="ControlCard", default_factory=list)
    score: List[Score] = element(tag="Score", default_factory=list)
    assigned_fees: List[AssignedFee] = element(tag="AssignedFee", default_factory=list)


class TeamEntry(BaseXmlModel):
    """Defines an event entry for a team."""

    id: Optional[Id] = element(tag="Id", default=None)
    name: str = element(tag="Name")
    organisations: List[Organisation] = element(tag="Organisation", default_factory=list)
    team_entry_persons: List[TeamEntryPerson] = element(tag="TeamEntryPerson", default_factory=list)
    class_: List[Class_] = element(tag="Class", default_factory=list)
    race: List[int] = element(tag="Race", default_factory=list)
    assigned_fees: List[AssignedFee] = element(tag="AssignedFee", default_factory=list)
    service_requests: List[ServiceRequest] = element(tag="ServiceRequest", default_factory=list)
    start_time_allocation_request: Optional[StartTimeAllocationRequest] = element(
        tag="StartTimeAllocationRequest", default=None
    )
    contact_information: Optional[str] = element(tag="ContactInformation", default=None)
    entry_time: Optional[datetime.datetime] = element(tag="EntryTime", default=None)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)
