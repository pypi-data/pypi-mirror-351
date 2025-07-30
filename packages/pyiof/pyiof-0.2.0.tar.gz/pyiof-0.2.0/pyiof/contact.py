import datetime
from typing import List, Literal, Optional

from .base import GeoPosition, Id, Image
from .fee import Account
from .xml_base import BaseXmlModel, attr, element


class Country(BaseXmlModel):
    """Defines the name of the country

    Attributes:
        name: Name of the country
        code: The International Olympic Committee's 3-letter code of the country
              as stated in https://en.wikipedia.org/wiki/List_of_IOC_country_codes.
              Note that several of the IOC codes are different from the standard
              ISO 3166-1 alpha-3 codes.
    """

    name: str = ""
    code: str = attr()


class Address(BaseXmlModel):
    """The postal address of a person or organisation.

    Attributes:
        careof (str, optional)
        street (str, optional)
        zipcode (str, optional)
        city (str, optional)
        state (str, optional)
        country (Country, optional)
        type (str, optional): The address type, e.g. visitor address or invoice address.
    """

    care_of: Optional[str] = element(tag="CareOf", default=None)
    street: Optional[str] = element(tag="Street", default=None)
    zip_code: Optional[str] = element(tag="ZipCode", default=None)
    city: Optional[str] = element(tag="City", default=None)
    state: Optional[str] = element(tag="State", default=None)
    country: Optional[Country] = element(tag="Country", default=None)
    type: Optional[str] = attr(default=None)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class Contact(BaseXmlModel):
    """Contact information for a person, organisation or other entity.

    Attributes:
        contact (str): contact information
        type (str): type of contact, one of {PhoneNumber, MobilePhoneNumber, FaxNumber,
                    EmailAddress, WebAddress, Other}
        modifyTime (datetime, optional)
    """

    contact: str
    type: Literal[
        "PhoneNumber",
        "MobilePhoneNumber",
        "FaxNumber",
        "EmailAddress",
        "WebAddress",
        "Other",
    ] = attr()
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class PersonName(BaseXmlModel):
    family_name: str = element(tag="Family", default="")
    given_name: str = element(tag="Given", default="")


Sex = Literal["M", "F", "B"]


class Person(BaseXmlModel):
    """Represents a person.
    This could either be a competitor (see the Competitor element)
    or contact persons in an organisation (see the Organisation element).

    Attributes:
        Id
    """

    ids: List[Id] = element(tag="Id", default_factory=list)
    name: PersonName = element(tag="Name")
    birth_date: Optional[datetime.date] = element(tag="BirthDate", default=None)
    nationality: Optional[Country] = element(tag="Nationality", default=None)
    address: List[Address] = element(tag="Address", default_factory=list)
    contact: List[Contact] = element(tag="Contact", default_factory=list)
    sex: Optional[Literal["M", "F"]] = attr(default=None)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class Role(BaseXmlModel):
    """Role

    A role defines a connection between a person and some kind of task,
    responsibility or engagement, e.g. being a course setter at an event.

    Attributes:
        person (Person): person which has the role
        type (str): The type of role
    """

    person: Person = element(tag="Person")
    type: str = attr()


class Organisation(BaseXmlModel):
    """Organisation

    Information about an organisation, i.e. address, contact person(s) etc.
    An organisation is a general term including federations, clubs, etc.

    Attributes:
        id (Id, optional)
        name (str): Full name of the organisation
        shortname
    """

    id: Optional[Id] = element(tag="Id", default=None)
    name: str = element(tag="Name")
    short_name: Optional[str] = element(tag="ShortName", default=None)
    media_name: Optional[str] = element(tag="MediaName", default=None)
    parent_organisation_id: Optional[int] = element(tag="ParentOrganisationId", default=None)
    country: Optional[Country] = element(tag="Country", default=None)
    address: List[Address] = element(tag="Address", default_factory=list)
    contact: List[Contact] = element(tag="Contact", default_factory=list)
    position: Optional[GeoPosition] = element(tag="Position", default=None)
    account: List[Account] = element(tag="Account", default_factory=list)
    roles: List[Role] = element(tag="Role", default_factory=list)
    logotype: List[Image] = element(tag="Logotype", default_factory=list)
    type: Optional[
        Literal[
            "IOF",
            "IOFRegion",
            "NationalFederation",
            "NationalRegion",
            "Club",
            "School",
            "Company",
            "Military",
            "Other",
        ]
    ] = attr(default=None)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)


class EntryReceiver(BaseXmlModel):
    addresses: List[Address] = element(tag="Address")
    contacts: List[Contact] = element(tag="Contact")
