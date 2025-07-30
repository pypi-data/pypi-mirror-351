from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column
from sqlalchemy.types import TIMESTAMP

from sqlmodel import Field, SQLModel, text
from sqlmodel.main import Relationship
import koco_product_sqlmodel.dbmodels.models_enums as m_enum


class CApplicationPost(SQLModel):
    application: str | None = Field(default=None, max_length=256)
    family_id: int | None = Field(default=None, foreign_key="cfamily.id")
    user_id: int = Field(default=1, foreign_key="cuser.id")


class CApplicationGet(CApplicationPost):
    id: int | None = None
    upddate: datetime
    insdate: datetime


class CApplication(CApplicationGet, table=True):
    id: int | None = Field(default=None, primary_key=True)
    application: str | None = Field(default=None, max_length=256)
    family_id: int | None = Field(default=None, foreign_key="cfamily.id")
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
    family: Optional["CFamily"] = Relationship(back_populates="applications")


def main():
    pass


if __name__ == "__main__":
    main()
