from __future__ import annotations

import datetime
from typing import List, Literal, Optional

from .base import Id
from .contact import Sex
from .course import Control, Leg, SimpleCourse
from .fee import Fee
from .xml_base import BaseXmlModel, attr, element

"""
The status of a certain race in the class.

Valid values:
    start_times_not_allocated: The start list draw has not been made for
        this class in this race
    start_times_allocated: The start list draw has been made for this class
        in this race.
    not_used: The class is not organised in this race, e.g. for classes that
        are organised in only some of the races in a multi-race event.
    completed: The result list is complete for this class in this race.
    invalidated: The results are considered invalid due to technical issues
        such as misplaced controls. Entry fees are not refunded.
    invalidated_no_fee: The results are considered invalid due to technical
        issues such as misplaced controls. Entry fees are refunded.
"""
RaceClassStatus = Literal[
    "StartTimesNotAllocated",
    "StartTimesAllocated",
    "NotUsed",
    "Completed",
    "Invalidated",
    "InvalidatedNoFee",
]


class RaceClass(BaseXmlModel):
    """Information about a class with respect to a race.

    Attributes:
        punching_system (list[str]): The punching system used for the class at
            the race. Multiple punching systems can be specified, e.g. one for
                punch checking and another for timing.
        team_fee (list[Fee]): The entry fees for a team as a whole taking part in
            this class. Use the Fee element to specify a fee for an individual
            competitor in the team. Use the TeamFee subelement of the Class element
            to specify a fee on event level.
        fee (list[Fee]): The entry fees for an individual competitor taking part in
            the race class. Use the TeamFee element to specify a fee for the team as
            a whole. Use the Fee subelement of the Class element to specify
            a fee on event level.
        first_start (datetime.datetime, optional)
        status (RaceClassStatus, optional): The status of the race, e.g. if results
            should be considered invalid due to misplaced constrols.
        course (list[SimpleCourse]): The courses assigned to this class.
            For a mass-start event or a relay event, there are usually multiple
            courses per class due to the usage of spreading methods.
        online_controls (list[Control]): The controls that are online controls
            for this class.
        race_number (int, optional): The ordinal number of the race that the
            information belongs to for a multi-race event, starting at 1.
        max_number_of_competitors (int, optional): The maximum number of competitors
            that are allowed to take part in the race class. A competitor corresponds
            to a person (if an individual event) or a team (if a team or relay event).
            This attribute overrides the maxNumberOfCompetitors attribute in
            the Class element.
        modifytime (datetime.datetime, optional)
    """

    punching_system: List[str] = element(tag="PunchingSystem", default_factory=list)
    team_fee: List[Fee] = element(tag="TeamFee", default_factory=list)
    fee: List[Fee] = element(tag="Fee", default_factory=list)
    first_start: Optional[datetime.datetime] = element(tag="FirstStart", default=None)
    status: Optional[
        Literal[
            "StartTimesNotAllocated",
            "StartTimesAllocated",
            "NotUsed",
            "Completed",
            "Invalidated",
            "InvalidatedNoFee",
        ]
    ] = element(tag="Status", default=None)
    course: List[SimpleCourse] = element(tag="Course", default_factory=list)
    online_controls: List[Control] = element(tag="OnlineControl", default_factory=list)
    race_number: Optional[int] = attr(name="raceNumber", default=None)
    max_number_of_competitors: Optional[int] = attr(name="maxNumberOfCompetitors", default=None)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


"""Defines the kind of information to include in the result list, and how
to sort it. For example, the result list of a beginner's class may include
just "finished" or "did not finish" instead of the actual times.

Valid values:
    Default: The result list should include place and time for each competitor,
        and be ordered by place.
    Unordered: The result list should include place and time for each competitor,
        but be unordered with respect to times (e.g. sorted by competitor name).
    UnorderedNoTimes: The result list should not include any places and times,
        and be unordered with respect to times (e.g. sorted by competitor name).
"""
ResultListMode = Literal["Default", "Unordered", "UnorderedNoTimes"]

"""The status of the class - enum

Attributes:
    Normal: The default status.
    Divided: The class has been divided in two or more classes due to a
        large number of entries.
    Joined: The class has been joined with another class due to a small number
        of entries.
    Invalidated: The results are considered invalid due to technical issues such as
        misplaced controls. Entry fees are not refunded.
    Invalidated_not_fee: The results are considered invalid due to technical issues
        such as misplaced controls. Entry fees are refunded.
"""
EventClassStatus = Literal["Normal", "Divided", "Joined", "Invalidated", "InvalidatedNoFee"]


class ClassType(BaseXmlModel):
    """Defines a class type, which is used to group classes in categories.

    Attributes:
        id (Id, optional)
        name (str): The name of the class type
        modifytime (datetime, optional)
    """

    id: Optional[Id] = element(tag="Id", default=None)
    name: str = element(tag="Name")
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


EventForm = Literal["Individual", "Team", "Relay"]


class Class_(BaseXmlModel):
    """Defines a class in an event

    Attributes:
        name (str): The name of the class
        id: Optional[Id]
        shortname (Optional[str]): The abbreviated name of a class, used when
            space is limited.
        classtype (List[ClassType]): The class type(s) for the class.
        leg (List[Leg]): Information about the legs, if the class is a relay class.
            One Leg element per leg must be present.
        team_fee (List[Fee]): The entry fees for a team as a whole taking part in
            this class. Use the Fee element to specify a fee for an individual
            competitor in the team. Use the TeamFee subelement of the RaceClass
            element to specify a fee on race level.
        fee (List[Fee]): The entry fees for an individual competitor taking part in
            the class. Use the TeamFee element to specify a fee for the team as a
            whole. Use the Fee subelement of the RaceClass element to specify a
            fee on race level.
        status (EventClassStatus): The overall status of the class, e.g. if overall
            results should be considered invalid due to misplaced controls.
            Defaults to normal
        raceclass (List[RaceClass]): Race-specific information for the class,
            e.g. course(s) assigned to the class.
        too_few_entries_substitute_class (Optional[Class_]): The class that competitors
            in this class should be transferred to if there are too
            few entries in this class.
        too_many_entries_substitue_class (Optional[Class_]): The class that competitors
            that are not qualified (e.g. due to too low ranking) should be transferred
            to if there are too many entries in this class.
        min_age (Optional[int]): The lowest allowed age for a competitor
            taking part in the class.
        max_age (Optional[int]): The highest allowed age for a competitor
            taking part in the class.
        sex (Optional[Sex])
        min_number_of_team_members (Optional[int]): The minimum number of members in
            a team taking part in the class, if the class is a team class.
        max_number_of_team_members (Optional[int]): The maximum number of members in
            a team taking part in the class, if the class is a team class.
        min_team_age (Optional[int]): The lowest allowed age sum of the team members
            for a team taking part in the class.
        max_team_age (Optional[int]): The highest allowed age sum of the team members
            for a team taking part in the class.
        number_of_competitors (Optional[int]): The number of competitors in the class.
            A competitor corresponds to a person (if an individual event) or
            a team (if a team or relay event).
        max_number_of_competitors (Optional[int]): The maximum number of competitors
            that are allowed to take part in the class. A competitor corresponds to
            a person (if an individual event) or a team (if a team or relay event).
            If the maximum number of competitors varies between races in a multi-day
            event, use the maxNumberOfCompetitors attribute in the RaceClass element.
        resultlist_mode (ResultListMode): Defines the kind of information to include
            in the result list, and how to sort it. For example, the result list of
            a beginner's class may include just "finished" or "did not finish"
            instead of the actual times.
    """

    id: Optional[Id] = element(tag="Id", default=None)
    name: str = element(tag="Name")
    shortname: Optional[str] = element(tag="ShortName", default=None)
    classtype: List[ClassType] = element(tag="ClassType", default_factory=list)
    leg: List[Leg] = element(tag="Leg", default_factory=list)
    team_fee: List[Fee] = element(tag="TeamFee", default_factory=list)
    fee: List[Fee] = element(tag="Fee", default_factory=list)
    status: EventClassStatus = element(tag="Status", default="Normal")
    race_class: List[RaceClass] = element(tag="RaceClass", default_factory=list)
    too_few_entries_substitute_class: Optional[Class_] = element(
        tag="TooFewEntriesSubstituteClass", default=None
    )
    too_many_entries_substitute_class: Optional[Class_] = element(
        tag="TooManyEntriesSubstituteClass", default=None
    )
    min_age: Optional[int] = attr(name="minAge", default=None)
    max_age: Optional[int] = attr(name="maxAge", default=None)
    sex: Optional[Sex] = attr(default=None)
    min_number_of_team_members: Optional[int] = attr(name="minNumberOfTeamMembers", default=None)
    max_number_of_team_members: Optional[int] = attr(name="maxNumberOfTeamMembers", default=None)
    min_team_age: Optional[int] = attr(name="minTeamAge", default=None)
    max_team_age: Optional[int] = attr(name="maxTeamAge", default=None)
    number_of_competitors: Optional[int] = attr(name="numberOfCompetitors", default=None)
    max_number_of_competitors: Optional[int] = attr(name="maxNumberOfCompetitors", default=None)
    resultlist_mode: ResultListMode = attr(name="resultListMode", default="Default")
