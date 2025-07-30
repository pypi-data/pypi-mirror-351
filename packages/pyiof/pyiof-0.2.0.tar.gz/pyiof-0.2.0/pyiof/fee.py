import datetime
from typing import Literal, Optional

from pydantic import condecimal, confloat, conlist

from .base import Id, LanguageString
from .xml_base import BaseXmlModel, attr, element

# from pydantic import validator


class Account(BaseXmlModel):
    """The bank account of an organisation or an event.

    Attributes:
        account (str): account information
        type (str, optional): The account type.
    """

    account: str
    type: Optional[str] = attr(default=None)


class Amount(BaseXmlModel):
    """Defines a monetary amount.

    Attributes:
        amount (decimal.Decimal)
        currency (str, optional)
    """

    amount: condecimal(max_digits=30)  # type: ignore
    currency: Optional[str] = attr(default=None)


FeeType = Literal["Normal", "Late"]


class Fee(BaseXmlModel):
    """A fee that applies when entering a class at a race or ordering a service.

    Attributes:
        id (Id)
        name (list[LanguageString]): A describing name of the fee,
            e.g. 'Late entry fee', at least one entry
        amount (Amount, optional): The fee amount, optionally including currency code.
            This element must not be present if a Percentage element exists.
        taxable_amount (Amount, optional): The fee amount that is taxable,
            i.e. considered when calculating taxes for an event. This element must
            not be present if a Percentage element exists,
            or if an Amount element does not exist.
        percentage (double, optional): The percentage to increase or decrease already
            existing fees in a fee list with. This element must not be present
            if an Amount element exists.
        taxable_percentage (double, optional): The percentage to increase or decrease
            already existing taxable fees in a fee list with. This element must not
            be present if an Amount element exists, or if a Percentage element
            does not exist.
        valid_from_time (datetime.datetime, optional):  The time when the
            fee takes effect.
        valid_to_time (datetime.datetime, optional): The time when the fee expires.
        from_birth_date (datetime.date, optional): The start of the birth date interval
            that the fee should be applied to. Omit if no lower birth date restriction.
        to_birth_date (datetime.date, optional): The end of the birth date interval
            that the fee should be applied to. Omit if no upper birth date restriction.
        type (str, optional): The type of Fee. Allowed values: Normal, Late.
            Default=Normal
    """

    id: Optional[Id] = element(tag="Id", default=None)
    name: conlist(item_type=LanguageString, min_length=1) = element(tag="Name")  # type: ignore
    amount: Optional[Amount] = element(tag="Amount", default=None)
    taxable_amount: Optional[Amount] = element(tag="TaxableAmount", default=None)
    percentage: Optional[float] = element(tag="Percentage", default=None)  # type: ignore
    taxable_percentage: Optional[float] = element(  # type: ignore
        tag="TaxablePercentage", default=None
    )
    valid_from_time: Optional[datetime.datetime] = element(tag="ValidFromTime", default=None)
    valid_to_time: Optional[datetime.datetime] = element(tag="ValidToTime", default=None)
    from_date_of_birth: Optional[datetime.date] = element(tag="FromDateOfBirth", default=None)
    to_date_of_birth: Optional[datetime.date] = element(tag="ToDateOfBirth", default=None)
    type: Optional[FeeType] = attr(default=None)
    modify_time: Optional[datetime.datetime] = attr(name="modifyTime", default=None)

    # TODO: not compatible with tests
    # @validator("percentage")
    # def validate_exclusive_amount_percentage(cls, percentage, values):
    #     """Validate that only one of amount or percentage is present.
    #     Might validator only applied to percentage, as amount is set first.
    #     """
    #     if percentage is not None and values["amount"] is not None:
    #         raise ValueError("Fee: only one of amount or percentage can be defined")
    #     return percentage

    # @validator("taxable_amount")
    # def validate_taxable_amount(cls, taxable_amount, values):
    #     if taxable_amount is not None and values["amount"] is None:
    #         raise ValueError(
    #             "Fee: taxable_amount only applicable if amount is defined"
    #         )
    #     return taxable_amount

    # @validator("taxable_percentage")
    # def validate_taxable_percentage(cls, taxable_percentage, values):
    #     if taxable_percentage is not None and values["amount"] is None:
    #         raise ValueError(
    #             "Fee: taxable_percentage only applicable if percentage is defined"
    #         )
    #     return taxable_percentage


class AssignedFee(BaseXmlModel):
    """Contains information about a fee that has been assigned to a
    competitor or a team, and the amount that has been paid.

    Attributes:
        fee (Fee): The fee that has been assigned to the competitor or the team.
        paid_amount (Amount, optional): The amount that has been paid,
            optionally including currency code.
    """

    fee: Fee = element(tag="Fee")
    paid_amount: Optional[Amount] = element(tag="PaidAmount", default=None)
    modifyTime: Optional[datetime.datetime] = attr(default=None)
