from datetime import datetime
from typing import Optional
from sqlalchemy import Column
from sqlalchemy.types import TIMESTAMP

from sqlmodel import Field, SQLModel, text


class CBacklog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    backlog_text: str = Field(default=None, max_length=1024)
    status: int = Field(default=1)
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


def main():
    pass


if __name__ == "__main__":
    main()
