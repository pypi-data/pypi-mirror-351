from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column
from sqlalchemy.types import TIMESTAMP
from sqlmodel import Field, SQLModel, text
from sqlmodel.main import Relationship
import koco_product_sqlmodel.dbmodels.models_enums as m_enum


class COptionPost(SQLModel):
    type: str | None = Field(
        default=m_enum.OptionFeatureEnum.features.value, max_length=64
    )  # distinguish between 'Option' and 'Feature', use same table for storage
    option: str | None = Field(default=None, max_length=256)
    category: str | None = Field(default=None, max_length=256)
    user_id: int | None = Field(default=1, foreign_key="cuser.id")
    family_id: int | None = Field(default=None, foreign_key="cfamily.id")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "feature",
                    "option": "Even though I am called 'option' I am still a feature description",
                    "category": "Mechanical",
                    "user_id": 1,
                    "family_id": 12,
                },
                {
                    "type": "option",
                    "option": "This time I am really the option description",
                    "category": "Mechanical",
                    "user_id": 1,
                    "family_id": 12,
                },
            ]
        }
    }


class COptionGet(COptionPost):
    id: int | None
    upddate: datetime
    insdate: datetime


class COption(COptionGet, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: str | None = Field(
        default=m_enum.OptionFeatureEnum.features.value, max_length=64
    )  # distinguish between 'Option' and 'Feature', use same table for storage
    option: str | None = Field(default=None, max_length=256)
    category: str | None = Field(default=None, max_length=256)
    user_id: int = Field(default=1, foreign_key="cuser.id")
    family_id: int | None = Field(default=None, foreign_key="cfamily.id")
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
    family: Optional["CFamily"] = Relationship(back_populates="options")


def main():
    pass


if __name__ == "__main__":
    main()
