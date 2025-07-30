import datetime
from typing import List, Literal, Optional

from .base import Id, Score
from .class_ import Class_
from .competitor import ControlCard, Organisation, Person
from .course import ControlAnswer, Route, SimpleCourse, SimpleRaceCourse
from .fee import AssignedFee
from .misc import ServiceRequest
from .xml_base import BaseXmlModel, attr, element

"""The result status of the person or team at the time of the result generation."""
ResultStatus = Literal[
    "OK",
    "Finished",
    "MissingPunch",
    "Disqualified",
    "DidNotFinish",
    "Active",
    "Inactive",
    "OverTime",
    "SportingWithdrawal",
    "NotCompeting",
    "Moved",
    "MovedUp",
    "DidNotStart",
    "DidNotEnter",
    "Cancelled",
]


class OverallResult(BaseXmlModel):
    time: Optional[float] = element(tag="Time", default=None)
    time_behind: Optional[float] = element(tag="TimeBehind", default=None)
    position: Optional[int] = element(tag="Position", default=None)
    status: ResultStatus = element(tag="Status")
    scores: List[Score] = element(tag="Score", default_factory=list)


class SplitTime(BaseXmlModel):
    """Defines a split time at a control."""

    control_card: str = element(tag="ControlCode")
    time: Optional[float] = element(tag="Time", default=None)
    status: Literal["OK", "Missing", "Additional"] = attr(default="OK")


class PersonRaceResult(BaseXmlModel):
    """Result information for a person in a race."""

    bib_number: Optional[str] = element(tag="BibNumber", default=None)
    start_time: Optional[datetime.datetime] = element(tag="StartTime", default=None)
    finish_time: Optional[datetime.datetime] = element(tag="FinishTime", default=None)
    time: Optional[float] = element(tag="Time", default=None)
    time_behind: Optional[float] = element(tag="TimeBehind", default=None)
    position: Optional[int] = element(tag="Position", default=None)
    status: ResultStatus = element(tag="Status")
    scores: List[Score] = element(tag="Score", default_factory=list)
    overall_result: Optional[OverallResult] = element(tag="OverallResult", default=None)
    course: Optional[SimpleCourse] = element(tag="Course", default=None)
    split_time: List[SplitTime] = element(tag="SplitTime", default_factory=list)
    control_answers: List[ControlAnswer] = element(tag="ControlAnswer", default_factory=list)
    route: Optional[Route] = element(tag="Route", default=None)
    control_card: List[ControlCard] = element(tag="ControlCard", default_factory=list)
    assigned_fees: List[AssignedFee] = element(tag="AssignedFee", default_factory=list)
    service_requests: List[ServiceRequest] = element(tag="ServiceRequest", default_factory=list)
    race_number: Optional[int] = attr(name="raceNumber", default=None)


class PersonResult(BaseXmlModel):
    """Result information for an individual competitor, including e.g. result status, place,
    finish time, and split times.
    """

    entry_id: Optional[Id] = element(tag="EntryId", default=None)
    person: Person = element(tag="Person")
    organisation: Optional[Organisation] = element(tag="Organisation", default=None)
    results: List[PersonRaceResult] = element(tag="Result", default_factory=list)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class TeamTimeBehind(BaseXmlModel):
    time_behind: float
    type: Literal["Leg", "Course"] = attr(name="type")


class TeamPosition(BaseXmlModel):
    position: int
    type: Literal["Leg", "Course"] = attr(name="type")


class TeamMemberRaceResults(BaseXmlModel):
    """Result information for a person in a race."""

    leg: Optional[int] = element(tag="Leg", default=None)
    leg_order: Optional[int] = element(tag="LegOrder", default=None)
    bib_number: Optional[str] = element(tag="BibNumber", default=None)
    start_time: Optional[datetime.datetime] = element(tag="StartTime", default=None)
    finish_time: Optional[datetime.datetime] = element(tag="FinishTime", default=None)
    time: Optional[float] = element(tag="Time", default=None)
    time_behind: List[TeamTimeBehind] = element(tag="TimeBehind")
    position: List[TeamPosition] = element(tag="Position", default_factory=list)
    status: ResultStatus = element(tag="Status")
    scores: List[Score] = element(tag="Score", default_factory=list)
    overall_result: Optional[OverallResult] = element(tag="OverallResult", default=None)
    course: Optional[SimpleCourse] = element(tag="Course", default=None)
    split_time: List[SplitTime] = element(tag="SplitTime", default_factory=list)
    control_answers: List[ControlAnswer] = element(tag="ControlAnswer", default_factory=list)
    route: Optional[Route] = element(tag="Route", default=None)
    control_card: List[ControlCard] = element(tag="ControlCard", default_factory=list)
    assigned_fees: List[AssignedFee] = element(tag="AssignedFee", default_factory=list)
    service_requests: List[ServiceRequest] = element(tag="ServiceRequest", default_factory=list)
    race_number: Optional[int] = attr(name="raceNumber", default=None)


class TeamMemberResult(BaseXmlModel):
    """Result information for a team member, including e.g. result status, place,
    finish time, and split times.
    """

    entry_id: Optional[Id] = element(tag="EntryId", default=None)
    person: Optional[Person] = element(tag="Person", default=None)
    organisation: Optional[Organisation] = element(tag="Organisation", default=None)
    results: List[TeamMemberRaceResults] = element(tag="Result", default_factory=list)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class TeamResult(BaseXmlModel):
    """Result information for a team, including e.g. result status, place, finish time and
    individual times for the team members.
    """

    entry_id: Optional[Id] = element(tag="EntryId", default=None)
    name: str = element(tag="Name")
    organisations: List[Organisation] = element(tag="Organisation", default_factory=list)
    bib_number: Optional[str] = element(tag="BibNumber", default=None)
    team_member_results: List[TeamMemberResult] = element(
        tag="TeamMemberResult", default_factory=list
    )
    assigned_fees: List[AssignedFee] = element(tag="AssignedFee", default_factory=list)
    service_requests: List[ServiceRequest] = element(tag="ServiceRequest", default_factory=list)


class ClassResult(BaseXmlModel):
    """The result list for a single class containing either individual
    results or team results.
    """

    class_: Class_ = element(tag="Class")
    courses: List[SimpleRaceCourse] = element(tag="Course", default_factory=list)
    person_results: List[PersonResult] = element(tag="PersonResult", default_factory=list)
    team_results: List[TeamResult] = element(tag="TeamResult", default_factory=list)
    time_resolution: float = attr(name="timeResolution", default=1)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)
