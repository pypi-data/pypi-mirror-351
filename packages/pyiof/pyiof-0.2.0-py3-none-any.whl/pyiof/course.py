import datetime
from typing import List, Literal, Optional

from pydantic import conlist

from .base import GeoPosition, Id, Image, LanguageString, MapPosition
from .xml_base import BaseXmlModel, attr, element


class Leg(BaseXmlModel):
    """Defines extra information for a relay leg.

    Attributes:
        name (str, optional): The name of the leg, if not sequentially named.
        min_number_of_competitors (int, default=1): The minimum number of competitors
            in case of a parallel leg.
        max_number_of_competitors (int, default=1): The maximum number of competitors
            in case of a parallel leg.
    """

    name: Optional[str] = element(tag="Name", default=None)
    min_number_of_competitors: Optional[int] = attr(name="minNumberOfCompetitors", default=None)
    max_number_of_competitors: Optional[int] = attr(name="maxNumberOfCompetitors", default=None)


class SimpleCourse(BaseXmlModel):
    """Defines a course, excluding controls.

    Attributes:
        id (Id)
        name (str, optional): The name of the course.
        course_family (str, optional): The family or group of forked courses
            that the course is part of.
        length (float, optional): The length of the course, in meters.
        climb (float, optional): The climb of the course, in meters, along the
            expected best route choice.
        number_of_controls (int, optional): The number of controls in the course,
            excluding start and finish.
    """

    id: Optional[Id] = element(tag="Id", default=None)
    name: Optional[str] = element(tag="Name", default=None)
    course_family: Optional[str] = element(tag="CourseFamily", default=None)
    length: Optional[float] = element(tag="Length", default=None)
    climb: Optional[float] = element(tag="Climb", default=None)
    number_of_controls: Optional[int] = element(tag="NumberOfControls", default=None)


"""The type of a control: (ordinary) control, start, finish,
    crossing point or end of marked route.

Valid values:
    control
    start
    finish
    crossing_point
    end_of_marked_route
"""
ControlType = Literal["Control", "Start", "Finish", "CrossingPoint", "EndOfMarkedRoute"]


class Control(BaseXmlModel):
    """Defines a control, without any relationship to a particular course.

    Attributes:
        id (Id, optional): The code of the control.
        punching_unit_id (list[Id], optional): If the control has multiple punching
        units with separate codes, specify all these codes using elements of this kind.
        Omit this element if there is a single punching unit whose code is
        the same as the control code.
        name (list[LanguageString], optional): The name of the control, used for
            e.g. online controls ('spectator control', 'prewarning').
        position (GeoPosition, optional): The geographical position of the control.
        map_position (MapPosition, optional): The position of the control according
            to the map's coordinate system.
        type (ControlType): The type of the control: (ordinary) control, start, finish,
            crossing point or end of marked route. This attribute can be overridden
            on the CourseControl level. Defaults to ControlType.control
        modifytime (datetime.datetime, optional)
    """

    id: Optional[Id] = element(tag="Id", default=None)
    punching_unit_id: List[Id] = element(tag="PunchingUnitId", default_factory=list)
    name: List[LanguageString] = element(tag="Name", default_factory=list)
    position: Optional[GeoPosition] = element(tag="Position", default=None)
    map_position: Optional[MapPosition] = element(tag="MapPosition", default=None)
    type: ControlType = attr(default="control")
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class SimpleRaceCourse(SimpleCourse):
    """Defines a course for a certain race, excluding controls.

    Attributes:
        id (Id)
        name (str, optional): The name of the course.
        course_family (str, optional): The family or group of forked courses
            that the course is part of.
        length (float, optional): The length of the course, in meters.
        climb (float, optional): The climb of the course, in meters, along the
            expected best route choice.
        number_of_controls (int, optional): The number of controls in the course,
            excluding start and finish.
        raceNumber (int, optional): The ordinal number of the race that the
            information belongs to for a multi-race event, starting at 1.
    """

    race_number: Optional[int] = attr(name="raceNumber", default=None)


class ControlAnswer(BaseXmlModel):
    """Defines the the selected answer, the correct answer and the time used on a Trail-O control.

    Attributes:
        answer (str): The answer that the competitor selected. If the
            competitor did not give any answer, use an empty string.
        correct_answer (str): The correct answer. If no answer is correct, use an empty string.
        time (float, optional): The time in seconds used to give the answer, in case of a timed
            control. Fractions of seconds (e.g. 258.7) may be used if the time resolution is
            higher than one second.
    """

    answer: str = element(tag="Answer")
    correct_answer: str = element(tag="CorrectAnswer", default="")
    time: Optional[float] = element(tag="Time", default=None)


class CourseControl(BaseXmlModel):
    """A control included in a particular course.

    control (list[str]): The code(s) of the control(s), without course-specific information.
        Specifying multiple control codes means that the competitor is required to punch one
        of the controls, but not all of them.

    """

    control: conlist(item_type=str, min_length=1) = element(tag="Control")  # type: ignore
    map_text: Optional[str] = element(tag="MapText", default=None)
    map_text_position: Optional[MapPosition] = element(tag="MapTextPosition", default=None)
    leg_length: Optional[float] = element(tag="LegLength", default=None)
    score: Optional[float] = element(tag="Score", default=None)
    type: Optional[ControlType] = attr(default=None)
    random_order: bool = attr(name="randomOrder", default=False)
    special_instruction: Optional[
        Literal[
            "None",
            "TapedRoute",
            "FunnelTapedRoute",
            "MandatoryCrossingPoint",
            "MandatoryOutOfBoundsAreaPassage",
        ]
    ] = attr(name="specialInstruction", default=None)
    taped_route_length: Optional[float] = attr(name="tapedRouteLength", default=None)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class Course(BaseXmlModel):
    """Defines a course, i.e. a number of controls including start and finish."""

    id: Optional[Id] = element(tag="Id", default=None)
    name: str = element(tag="Name")
    course_family: Optional[str] = element(tag="CourseFamily", default=None)
    length: Optional[float] = element(tag="Length", default=None)
    climb: Optional[float] = element(tag="Climb", default=None)
    course_controls: conlist(item_type=CourseControl, min_length=2) = element(  # type: ignore
        tag="CourseControl"
    )
    map_id: Optional[int] = element(tag="MapId", default=None)
    number_of_competitors: Optional[int] = attr(name="numberOfCompetitors", default=None)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)

    def __add__(self, other):
        return Course(
            # id = Id(id=self.id.id + other.id.id),
            name=self.name + other.name,
            length=self.length + other.length,
            climb=self.climb + other.climb,
            course_controls=self.course_controls + other.course_controls,
        )


class Map(BaseXmlModel):
    """Map information, used in course setting software with regard to the "real" map."""

    id: Optional[Id] = element(tag="Id", default=None)
    image: Optional[Image] = element(tag="Image", default=None)
    scale: float = element(tag="Scale")
    map_position_top_left: MapPosition = element(tag="MapPositionTopLeft")
    map_position_bottom_right: MapPosition = element(tag="MapPositionBottomRight")


class Route(BaseXmlModel):
    """Defines a route, i.e. a number of geographical positions (waypoints) describing a
    competitor's navigation throughout a course.
    """

    base64: str


class StartName(BaseXmlModel):
    """
    Defines the name of the start place (e.g. Start 1), if the race has multiple start places.
    """

    start_name: str
    race_number: Optional[int] = attr(name="raceNumber", default=None)


class PersonCourseAssignment(BaseXmlModel):
    """Element that connects a course with an individual competitor. Courses should be
    present in the RaceCourseData element and are matched on course name and/or course
    family. Persons are matched by 1) BibNumber, 2) EntryId.
    """

    entry_id: Optional[Id] = element(tag="EntryId", default=None)
    bib_number: Optional[str] = element(tag="BibNumber", default=None)
    person_name: Optional[str] = element(tag="PersonName", default=None)
    class_name: Optional[str] = element(tag="ClassName", default=None)
    course_name: Optional[str] = element(tag="CourseName", default=None)
    course_family: Optional[str] = element(tag="CourseFamily", default=None)


class TeamMemberCourseAssignment(BaseXmlModel):
    """
    Element that connects a course with a relay team member. Courses should be present
    in the RaceCourseData element and are matched on course name and/or course family.
    Team members are matched by 1) BibNumber, 2) Leg and LegOrder, 3) EntryId.
    """

    entry_id: Optional[Id] = element(tag="EntryId", default=None)
    bib_number: Optional[str] = element(tag="BibNumber", default=None)
    leg: Optional[int] = element(tag="Leg", default=None)
    leg_order: Optional[int] = element(tag="LegOrder", default=None)
    team_member_name: Optional[int] = element(tag="TeamMemberName", default=None)
    course_name: Optional[str] = element(tag="CourseName", default=None)
    course_family: Optional[str] = element(tag="CourseFamily", default=None)


class TeamCourseAssignment(BaseXmlModel):
    """
    Element that connects a number of team members in a relay team to a number of courses.
    Teams are matched by 1) BibNumber, 2) TeamName+ClassName.
    """

    bib_number: Optional[str] = element(tag="BibNumber", default=None)
    team_name: Optional[str] = element(tag="TeamName", default=None)
    class_name: Optional[str] = element(tag="ClassName", default=None)
    team_member_course_assignment: List[TeamMemberCourseAssignment] = element(
        tag="TeamMemberCourseAssignment", default_factory=list
    )


class ClassCourseAssignment(BaseXmlModel):
    class_id: Optional[Id] = element(tag="ClassId", default=None)
    class_name: str = element(tag="ClassName")
    allowed_on_leg: List[int] = element(tag="AllowedOnLeg", default_factory=list)
    course_name: Optional[str] = element(tag="CourseName", default=None)
    course_family: Optional[str] = element(tag="CourseFamily", default=None)
    number_of_competitors: Optional[int] = attr(name="numberOfCompetitors", default=None)


class RaceCourseData(BaseXmlModel):
    """This element defines all the control and course information for a race."""

    map: List[Map] = element(tag="Map", default_factory=list)
    controls: List[Control] = element(tag="Control", default_factory=list)
    courses: List[Course] = element(tag="Course", default_factory=list)
    class_course_assignments: List[ClassCourseAssignment] = element(
        tag="ClassCourseAssignment", default_factory=list
    )
    person_course_assignments: List[PersonCourseAssignment] = element(
        tag="PersonCourseAssignment", default_factory=list
    )
    team_course_assignments: List[TeamCourseAssignment] = element(
        tag="TeamCourseAssignment", default_factory=list
    )
    race_number: Optional[int] = attr(name="raceNumber", default=None)
