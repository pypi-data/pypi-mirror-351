from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.types import TIMESTAMP

from sqlmodel import Field, SQLModel, text
import koco_product_sqlmodel.dbmodels.models_enums as m_enum


class CUrlPost(SQLModel):
    # type: m_enum.CUrlTypeEnum | None = Field(
    #     default=m_enum.CUrlTypeEnum.datasheet.value, max_length=64
    # )
    type: str | None = None
    supplier_url: str | None = Field(default=None, max_length=1024)
    KOCO_url: str | None = Field(default=None, max_length=1024)
    description: str | None = Field(default=None, max_length=1024)
    parent_id: int | None = Field(default=None)
    parent: m_enum.CUrlParentEnum | None = Field(
        default=m_enum.CUrlParentEnum.family.value, max_length=64
    )  # selector if table belongs to 'article', 'family', 'categorytree'
    user_id: int = Field(default=1, foreign_key="cuser.id")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "CUrlTypeEnum",
                    "supplier_url": "URL to respective data from supplier",
                    "KOCO_url": "URL to respective data on KOCO server",
                    "description": "Description of the data source",
                    "parent_id": 1,
                    "parent": "CUrlParentEnum",
                    "user_id": 1,
                }
            ]
        }
    }


class CUrlGet(CUrlPost):
    id: int
    upddate: datetime
    insdate: datetime


class CUrl(CUrlGet, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: str | None = None
    # type: m_enum.CUrlTypeEnum | None = Field(
    #     default=m_enum.CUrlTypeEnum.datasheet.value, max_length=64
    # )
    supplier_url: str | None = Field(default=None, max_length=1024)
    KOCO_url: str | None = Field(default=None, max_length=1024)
    description: str | None = Field(default=None, max_length=1024)
    parent_id: int | None = Field(default=None)
    parent: str | None = Field(
        default=m_enum.CUrlParentEnum.family.value, max_length=64
    )  # selector if table belongs to 'article', 'family', 'categorytree'
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
