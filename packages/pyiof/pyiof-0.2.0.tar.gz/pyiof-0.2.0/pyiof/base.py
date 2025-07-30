import datetime
from typing import Literal, Optional

from .xml_base import BaseXmlModel, attr, element


class Id(BaseXmlModel):
    """Identifier element, used extensively. The id should be known
    and common for both systems taking part in the data exchange.

    Attributes:
        type (str, optional): The issuer of the identity, e.g. World Ranking List.
    """

    id: str = ""
    type: Optional[str] = attr(default=None)


class Image(BaseXmlModel):
    """Image file

    Defines an image file, either as a link (use the url attribute)
    or as base64-encoded binary data.

    Attributes:
        data: base64 encoded data
        mediatype (str): The type of the image file, e.g. image/jpeg. Refer to
                   https://www.iana.org/assignments/media-types/media-types.xhtml#image
                   for available media types.
        width (int, optional): The width of the image in pixels.
        height (int, optional): The height of the image in pixels.
        resolution (double, optional): The resolution of the image in dpi.
    """

    data: str
    mediatype: str = attr(name="mediaType")
    url: Optional[str] = attr(default=None)
    width: Optional[int] = attr(default=None)
    height: Optional[int] = attr(default=None)
    resolution: Optional[float] = attr(default=None)


class DateAndOptionalTime(BaseXmlModel):
    """Defines a point in time which either is known by date and time,
    or just by date. May be used for event dates, when the event date is
    decided before the time of the first start.

    Attributes:
        date (datetime.date): The date part, expressed in ISO 8601 format.
        time (datetime.time, optional): The time part, expressed in ISO 8601 format.
    """

    date: datetime.date = element(tag="Date")
    time: Optional[datetime.time] = element(tag="Time", default=None)


class LanguageString(BaseXmlModel):
    """Defines a text that is given in a particular language.

    Attributes:
        text (str)
        language (str, optional): The ISO 639-1 two-letter code of the language
            as stated in https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes.
    """

    text: str
    language: Optional[str] = attr(default=None)


class GeoPosition(BaseXmlModel):
    """Defines a geographical position, e.g. of a control.

    Attributes:
        lng (double): The longitude
        lat (double): The latitude
        alt (double): The altitude (elevation above sea level), in meters
    """

    lng: float = attr()
    lat: float = attr()
    alt: Optional[float] = attr(default=None)


"""
Unit type for map representation

Valid values:
    mm: Millimeters, used when the map is represented by a printed piece of paper.
    px: Pixels, used when the map is represented by a digital image.
"""
MapUnitType = Literal["mm", "px"]


class MapPosition(BaseXmlModel):
    """Defines a position in a map's coordinate system.

    Attributes:
        x (float): The number of units right of the center of the coordinate system.
        y (float): The number of units below the center of the coordinate system.
        unit (Unit, optional): The type of unit used, defaults to Unit.mm
    """

    x: float = attr()
    y: float = attr()
    unit: MapUnitType = attr(default="mm")


class Score(BaseXmlModel):
    """Score

    The score earned in an event for some purpose, e.g. a ranking list.
    Attributes:
        score (double): The actual score
        type (str): Purpose of score, e.g. name of ranking list
    """

    score: float
    type: Optional[str] = attr(default=None)
