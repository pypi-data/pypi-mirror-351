from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.types import TIMESTAMP

from sqlmodel import Field, SQLModel, text, Enum
import koco_product_sqlmodel.dbmodels.models_enums as m_enum

"""
Module used to describe the filedata-sqlmodel to handle data from mariadb-table cfiledata.
The filedata-table will replace the curl-table and is a little more generic.
Files are stored in a single folder, using the blake2s-hash of the file content as filename.
A mapping is generated using the blake2shash-column in the cfiledata-table
"""


class CFileDataPost(SQLModel):
    documenttype: m_enum.CDocumentType | None = None
    description_json: str | None = Field(default=None, max_length=4096)  # JSON-data
    oldfilename: str | None = Field(default=None, max_length=1024)
    entity_id: int | None = Field(default=None)
    entity_type: str | None = Field(
        default=None, max_length=64
    )  # table-name of the sql-table in lower-case
    mimetype: str | None = Field(default=None, max_length=256)
    blake2shash: str | None = Field(default=None, max_length=64)
    visibility: int = m_enum.CFiledataVisibility.everywhere.value
    order_priority: int = 100
    user_id: int = Field(default=1, foreign_key="cuser.id")


class CFileDataGet(CFileDataPost):
    id: int | None = None
    insdate: datetime | None
    upddate: datetime | None


class CFileData(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    documenttype: m_enum.CDocumentType | None = None
    description_json: str | None = Field(default=None, max_length=4096)  # JSON-data
    oldfilename: str | None = Field(default=None, max_length=1024)
    entity_id: int | None = Field(default=None)
    entity_type: str | None = Field(
        default=None, max_length=64
    )  # table-name of the sql-table in lower-case
    mimetype: str | None = Field(default=None, max_length=256)
    blake2shash: str | None = Field(default=None, max_length=64)
    visibility: int = m_enum.CFiledataVisibility.everywhere.value
    order_priority: int = 100
    user_id: int = Field(default=1, foreign_key="cuser.id")
    upddate: datetime = Field(
        sa_column=sa.Column(
            TIMESTAMP,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        )
    )
    insdate: datetime = Field(
        sa_column=sa.Column(
            TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
        )
    )


def main():
    pass


if __name__ == "__main__":
    main()
