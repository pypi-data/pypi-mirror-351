from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.types import TIMESTAMP
import koco_product_sqlmodel.dbmodels.models_enums as m_enum

from sqlmodel import Field, SQLModel, text


class CUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None, min_length=4, max_length=128)
    first_name: str | None = Field(default=None, max_length=128)
    last_name: str | None = Field(default=None, max_length=128)
    email: str | None = Field(default=None, max_length=256)
    password: bytes | None = Field(default=None, max_length=32)
    role_id: int = Field(default=m_enum.CUserRoleIdEnum.reader.value)
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


class CUserRole(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    role: str | None = Field(default=None, min_length=4, max_length=64)
    description: str | None = Field(default=None, max_length=1024)
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


def main():
    pass


if __name__ == "__main__":
    main()
