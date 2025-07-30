from typing import Self, cast

import pydantic_xml
from pydantic_xml import attr, element  # noqa: F401


class BaseXmlModel(  # type: ignore
    pydantic_xml.BaseXmlModel,
    nsmap={
        "": "http://www.orienteering.org/datastandard/3.0",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    },
):
    def to_xml_tree(self, exclude_none: bool = True, **kwargs):
        return super().to_xml_tree(exclude_none=exclude_none, **kwargs)

    def to_xml(self, pretty_print: bool = True, **kwargs) -> bytes:
        return cast(
            bytes,
            super().to_xml(
                pretty_print=pretty_print,
                xml_declaration=True,
                encoding="UTF-8",
                skip_empty=True,
                **kwargs,
            ),
        )

    @classmethod
    def read_xml(cls, path: str, encoding: str = "utf-8") -> Self:
        with open(path, "rb") as f:
            return cls.from_xml(f.read())

    def write_xml(self, path: str) -> None:
        with open(path, "wb") as f:
            f.write(self.to_xml())
