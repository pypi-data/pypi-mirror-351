from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column
from sqlalchemy.types import TIMESTAMP

from sqlmodel import Field, SQLModel, text
from sqlmodel.main import Relationship

import koco_product_sqlmodel.dbmodels.models_enums as m_enum


class CSpecTablePost(SQLModel):
    name: str | None = Field(default=None, max_length=256)
    type: m_enum.SpectableTypeEnum = Field(
        default=m_enum.SpectableTypeEnum.overview.value, max_length=64
    )  # selector if 'singlecol', 'multicol', 'overview'
    has_unit: bool | None = None  # switch if unit col is needed or not
    parent: m_enum.SpectableParentEnum = Field(
        default=m_enum.SpectableParentEnum.family.value, max_length=64
    )  # selector if table belongs to 'article', 'family', 'product_group', or 'catalog'
    user_id: int = Field(default=1, foreign_key="cuser.id")
    parent_id: int = Field(default=None)
    description_json: str | None = Field(default=None, max_length=4096)  # JSON-data



class CSpecTableGet(CSpecTablePost):
    id: int
    upddate: datetime
    insdate: datetime


class CSpecTable(CSpecTableGet, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(default=None, max_length=256)
    type: m_enum.SpectableTypeEnum = Field(
        default=m_enum.SpectableTypeEnum.overview.value, max_length=64
    )  # selector if 'singlecol', 'multicol', 'overview'
    has_unit: bool | None = None  # switch if unit col is needed or not
    parent: m_enum.SpectableParentEnum = Field(
        default=m_enum.SpectableParentEnum.family.value, max_length=64
    )  # selector if table belongs to 'article', 'family', 'product_group', or 'catalog'
    user_id: int = Field(default=1, foreign_key="cuser.id")
    upddate: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        )
    )
    insdate: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
        )
    )
    parent_id: int = Field(default=None)
    description_json: str | None = Field(default=None, max_length=4096)  # JSON-data
    spec_table_items: List["CSpecTableItem"] = Relationship(back_populates="spec_table")


class CSpecTableItemPost(SQLModel):
    pos: str | None = Field(default=None, max_length=32)
    name: str | None = Field(default=None, max_length=256)
    value: str | None = Field(default=None, max_length=256)
    min_value: str | None = Field(default=None, max_length=256)
    max_value: str | None = Field(default=None, max_length=256)
    unit: str | None = Field(default=None, max_length=256)
    user_id: int = Field(default=1, foreign_key="cuser.id")
    spec_table_id: int | None = Field(default=None, foreign_key="cspectable.id")


class CSpecTableItemGet(CSpecTableItemPost):
    id: int
    upddate: datetime
    insdate: datetime


class CSpecTableItem(CSpecTableItemGet, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pos: str | None = Field(default=None, max_length=32)
    name: str | None = Field(default=None, max_length=256)
    value: str | None = Field(default=None, max_length=256)
    min_value: str | None = Field(default=None, max_length=256)
    max_value: str | None = Field(default=None, max_length=256)
    unit: str | None = Field(default=None, max_length=256)
    user_id: int = Field(default=1, foreign_key="cuser.id")
    upddate: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        )
    )
    insdate: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
        )
    )
    spec_table_id: int | None = Field(default=None, foreign_key="cspectable.id")
    spec_table: CSpecTable = Relationship(back_populates="spec_table_items")


def main():
    pass


if __name__ == "__main__":
    main()
