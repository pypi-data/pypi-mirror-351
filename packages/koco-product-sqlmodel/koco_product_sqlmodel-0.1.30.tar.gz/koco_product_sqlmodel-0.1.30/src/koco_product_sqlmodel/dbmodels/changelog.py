from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.types import TIMESTAMP

from sqlmodel import Field, SQLModel, text, JSON

# Lines needed to avoid warning due to unset inherit_cache attribute
from sqlmodel.sql.expression import Select, SelectOfScalar

import koco_product_sqlmodel.dbmodels.models_enums as m_enum

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore


class CChangelogPost(SQLModel):
    entity_id: int | None = Field(default=None)
    entity_type: str | None = Field(default=None, max_length=64)
    user_id: int = Field(default=1)
    action: str | None = None
    new_values: str | None = None


class CChangelogGet(CChangelogPost):
    id: int | None
    user_name: str | None = None
    insdate: datetime | None


class CChangelog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    entity_id: int | None = Field(default=None)
    entity_type: str | None = Field(default=None, max_length=64)
    user_id: int = Field(default=1, foreign_key="cuser.id")
    insdate: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
        )
    )
    action: str | None = None
    new_values: str | None = None


def Main():
    pass


if __name__ == "__main__":
    Main()
