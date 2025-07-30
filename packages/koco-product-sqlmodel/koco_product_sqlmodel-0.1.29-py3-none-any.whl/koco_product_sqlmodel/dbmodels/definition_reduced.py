from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel

import koco_product_sqlmodel.dbmodels.models_enums as m_enums


class CSpecTableItem(SQLModel):
    id: int | None = Field(default=None)
    pos: str | None = Field(default=None, max_length=32)
    name: str | None = Field(default=None, max_length=256)
    value: str | None = Field(default=None, max_length=256)
    min_value: str | None = Field(default=None, max_length=256)
    max_value: str | None = Field(default=None, max_length=256)
    unit: str | None = Field(default=None, max_length=256)
    user_id: int | None
    upddate: datetime | None
    insdate: datetime | None
    spec_table_id: int | None


class CSpecTable(SQLModel):
    id: int | None = Field(default=None)
    name: str | None = Field(default=None, max_length=256)
    type: m_enums.SpectableTypeEnum | None = Field(
        default=m_enums.SpectableTypeEnum.overview
    )
    has_unit: bool | None = None  # switch if unit col is needed or not
    parent: m_enums.SpectableParentEnum | None = Field(
        default=m_enums.SpectableParentEnum.family
    )
    user_id: int | None
    upddate: datetime | None
    insdate: datetime | None
    parent_id: int | None
    spec_table_items: List[CSpecTableItem]


class CUrl(SQLModel):
    id: int | None = Field(default=None)
    type: m_enums.CUrlTypeEnum | None = Field(default=m_enums.CUrlTypeEnum.datasheet)
    supplier_url: str | None = Field(default=None, max_length=1024)
    KOCO_url: str | None = Field(default=None, max_length=1024)
    description: str | None = Field(default=None, max_length=1024)
    parent_id: int | None = Field(default=None)
    parent: m_enums.CUrlParentEnum | None = Field(default=m_enums.CUrlParentEnum.family)
    user_id: int | None = Field(default=1)
    upddate: datetime | None
    insdate: datetime | None


class COption(SQLModel):
    id: int | None = Field(default=None)
    type: m_enums.OptionFeatureEnum | None = Field(
        default=m_enums.OptionFeatureEnum.feature
    )
    option: str | None = Field(default=None, max_length=256)
    category: str | None = Field(default=None, max_length=256)
    user_id: int | None = Field(default=1)
    family_id: int | None = Field(default=None)
    upddate: datetime | None
    insdate: datetime | None


class CApplication(SQLModel):
    id: int | None = Field(default=None)
    application: str | None = Field(default=None, max_length=256)
    family_id: int | None = Field(default=None)
    user_id: int | None = Field(default=1)
    upddate: datetime | None
    insdate: datetime | None


class CArticle(SQLModel):
    id: int | None = Field(default=None)
    article: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=4096)
    short_description: str | None = Field(default=None, max_length=256)
    upddate: datetime | None
    insdate: datetime | None
    family_id: int | None
    status: m_enums.StatusEnum | None = Field(default=m_enums.StatusEnum.in_work)
    user_id: int | None


class CFamily(SQLModel):
    id: int | None = Field(default=None)
    family: str | None = Field(default=None, max_length=256)
    type: str | None = Field(default=None, max_length=1024)
    description: str | None = Field(default=None, max_length=1024)
    short_description: str | None = Field(default=None, max_length=256)
    upddate: datetime | None
    insdate: datetime | None
    product_group_id: int | None = Field(default=None)
    status: m_enums.StatusEnum | None = Field(default=m_enums.StatusEnum.in_work)
    user_id: int | None = Field(default=1)
    articles: List[CArticle] | None
    applications: List[CApplication] | None
    options: List[COption] | None


class CProductGroup(SQLModel):
    id: Optional[int] = Field(default=None)
    product_group: str = Field(default=None, max_length=256)
    description: Optional[str] = Field(default=None, max_length=1024)
    image_url: Optional[str] = Field(default=None, max_length=1024)
    supplier_site_url: Optional[str] = Field(default=None, max_length=1024)
    catalog_id: Optional[int] = Field(default=None)
    status: m_enums.StatusEnum | None = Field(default=m_enums.StatusEnum.in_work)
    user_id: int | None
    order_priority: int | None
    upddate: datetime | None
    insdate: datetime | None
    families: List[CFamily] | None


class CCatalog(SQLModel):
    id: int | None = Field(default=None)
    supplier: str | None = Field(default=None, max_length=128)
    year: int | None = None
    status: m_enums.StatusEnum | None = Field(default=m_enums.StatusEnum.in_work)
    user_id: int | None = None
    insdate: datetime | None = None
    upddate: datetime | None = None
    # product_groups: List[CProductGroup]|None


# class CUser(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str = Field(default=None, min_length=4, max_length=128)
#     first_name: Optional[str] = Field(default=None, max_length=128)
#     last_name: Optional[str] = Field(default=None, max_length=128)
#     email: Optional[str] = Field(default=None, max_length=256)
#     password: Optional[bytes] = Field(default=None, max_length=32)
#     role_id: int = Field(default=1)
#     insdate: datetime = Field(
#         sa_column=Column(
#             TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
#         )
#     )
#     upddate: datetime = Field(
#         sa_column=Column(
#             TIMESTAMP,
#             nullable=False,
#             server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
#         )
#     )


# class CUserRole(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     role: str = Field(default=None, min_length=4, max_length=64)
#     description: Optional[str] = Field(default=None, max_length=1024)
#     insdate: datetime = Field(
#         sa_column=Column(
#             TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
#         )
#     )
#     upddate: datetime = Field(
#         sa_column=Column(
#             TIMESTAMP,
#             nullable=False,
#             server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
#         )
#     )


# class CBacklog(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     backlog_text: str = Field(default=None, max_length=1024)
#     status: int = Field(default=1)
#     user_id: int = Field(default=1, foreign_key="cuser.id")
#     upddate: datetime = Field(
#         sa_column=Column(
#             TIMESTAMP,
#             nullable=False,
#             server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
#         )
#     )
#     insdate: datetime = Field(
#         sa_column=Column(
#             TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
#         )
#     )

# class CCategoryTree(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     category: str = Field(default=None, max_length=128)
#     export_target: str = Field(default=None, max_length=16)
#     description: str = Field(default=None, max_length=4096)
#     parent_id: int = Field(default=None)
#     pos: int = Field(default=1)
#     user_id: int = Field(default=1, foreign_key="cuser.id")
#     upddate: datetime = Field(
#         sa_column=Column(
#             TIMESTAMP,
#             nullable=False,
#             server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
#         )
#     )
#     insdate: datetime = Field(
#         sa_column=Column(
#             TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
#         )
#     )


# class CCategoryMapper(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     category_id: Optional[int] = Field(default=None, foreign_key=CCategoryTree.id)
#     family_id: Optional[int] = Field(default=None, foreign_key=CFamily.id)
#     user_id: int = Field(default=1, foreign_key="cuser.id")
#     upddate: datetime = Field(
#         sa_column=Column(
#             TIMESTAMP,
#             nullable=False,
#             server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
#         )
#     )
#     insdate: datetime = Field(
#         sa_column=Column(
#             TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
#         )
#     )


def Main():
    pass


if __name__ == "__main__":
    Main()
