from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column
from sqlalchemy.types import TIMESTAMP
from sqlmodel import Field, SQLModel, text
from sqlmodel.main import Relationship

import koco_product_sqlmodel.dbmodels.models_enums as m_enum


class CProductGroupPost(SQLModel):
    product_group: str = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=4096)
    image_url: str | None = Field(default=None, max_length=1024)
    supplier_site_url: str | None = Field(default=None, max_length=1024)
    catalog_id: int | None = Field(default=None, foreign_key="ccatalog.id")
    status: int = Field(
        default=m_enum.StatusEnum.in_work.value
    )  # general status of the data set 1: "in work", 2: "ready for review". 3: "released"
    user_id: int = Field(default=1, foreign_key="cuser.id")
    order_priority: int = Field(default=0)


class CProductGroupGet(CProductGroupPost):
    id: int | None = None
    upddate: datetime = None
    insdate: datetime = None


class CProductGroup(CProductGroupGet, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_group: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=4096)
    image_url: str | None = Field(default=None, max_length=1024)
    supplier_site_url: str | None = Field(default=None, max_length=1024)
    catalog_id: Optional[int] = Field(default=None, foreign_key="ccatalog.id")
    status: int = Field(
        default=m_enum.StatusEnum.in_work.value
    )  # general status of the data set 1: "in work", 2: "ready for review". 3: "released"
    user_id: int = Field(default=1, foreign_key="cuser.id")
    order_priority: int = Field(default=0)
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
    catalog: Optional["CCatalog"] = Relationship(back_populates="product_groups")
    families: List["CFamily"] = Relationship(back_populates="product_group")


def main():
    pass


if __name__ == "__main__":
    main()
