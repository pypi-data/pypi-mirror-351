from datetime import datetime
from typing import Optional
from sqlalchemy import Column
from sqlalchemy.types import TIMESTAMP

from sqlmodel import Field, SQLModel, text

# Lines needed to avoid warning due to unset inherit_cache attribute
from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore


class TViewdefTable(SQLModel, table=True):
    id: int = Field(sa_column=Column(primary_key=True, autoincrement=True))
    tablename: Optional[str] = Field(default=None, max_length=32)
    description: Optional[str] = Field(default=None, max_length=4096)
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


class TViewdefColumn(SQLModel, table=True):
    id: int = Field(sa_column=Column(primary_key=True, autoincrement=True))
    tableid: int = Field(default=0)
    columnname: str = Field(default=None, max_length=32)
    pos: str = Field(default=None, max_length=15)
    istextarea: bool = Field(default=False)
    iseditable: bool = Field(default=False)
    istranslated: bool = Field(default=False)
    isselect: bool = Field(default=False)
    type: str = Field(default=None, max_length=15)
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


class TViewDefSelectValue(SQLModel, table=True):
    id: int = Field(sa_column=Column(primary_key=True, autoincrement=True))
    columnid: int = Field(default=0)
    pos: str = Field(default=None, max_length=15)
    value: str = Field(default=False, max_length=31)
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


class TDictionary(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    keystr: str = Field(max_length=4096)
    lang: str = Field(default="de", max_length=64)
    translation: str = Field(max_length=4096)
    user_id: int = Field(default=1, foreign_key="cuser.id")
    status: int = (Field(default=1),)
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


class TTranslationMapper(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    parent: Optional[str] = Field(
        default=None, max_length=64
    )  # selector if table belongs to 'carticle', 'cfamily', 'cproductgroup'
    parent_id: int = Field(default=None)
    columnname: str = Field(default=None, max_length=64)
    dictionary_id: int = Field(default=1)  # ID of
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


def Main():
    pass


if __name__ == "__main__":
    Main()
