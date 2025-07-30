# from koco_product_sqlmodel.dbmodels.definition import CProductGroup
import koco_product_sqlmodel.dbmodels.models_enums as m_enum
from datetime import datetime
from typing import List
from sqlalchemy import Column
from sqlalchemy.types import TIMESTAMP

from sqlmodel import Field, SQLModel, text
from sqlmodel.main import Relationship


class CCatalogPost(SQLModel):
    supplier: str = Field(default=None, max_length=128)
    year: int | None = None
    status: int = Field(
        default=m_enum.StatusEnum.in_work.value
    )  # general status of the data set 1: "in work", 2: "ready for review". 3: "released"
    user_id: int = Field(default=1, foreign_key="cuser.id")


class CCatalogGet(CCatalogPost):
    id: int | None
    insdate: datetime | None
    upddate: datetime | None


class CCatalog(CCatalogGet, table=True):
    id: int | None = Field(default=None, primary_key=True)
    supplier: str = Field(default=None, max_length=128)
    year: int | None = None
    status: int = Field(
        default=m_enum.StatusEnum.in_work.value
    )  # general status of the data set 1: "in work", 2: "ready for review". 3: "released"
    user_id: int = Field(default=1, foreign_key="cuser.id")
    insdate: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
        )
    )
    upddate: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        )
    )
    product_groups: List["CProductGroup"] = Relationship(back_populates="catalog")


def main():
    pass


if __name__ == "__main__":
    main()
