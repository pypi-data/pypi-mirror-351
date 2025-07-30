import koco_product_sqlmodel.dbmodels.definition as sqm
import koco_product_sqlmodel.dbmodels.viewdef as vdm
import koco_product_sqlmodel.dbmodels.support as sup
import koco_product_sqlmodel.mdb_connect.mdb_connector as mdb_con
import koco_product_sqlmodel.mdb_connect.viewdef as viewdef
from sqlmodel import SQLModel, Session, select, text
from copy import deepcopy


def select_article_from_catalog(
    engine=None,
    article: str = None,
    article_id: int = None,
    catalog_id: int = None,
    supplier: str = None,
    year: int = None,
) -> sqm.CArticle:
    if not engine:
        engine = mdb_con.mdb_engine
    if article_id and catalog_id:
        with Session(engine) as session:
            statement = (
                select(sqm.CArticle)
                .join(sqm.CFamily, sqm.CFamily.id == sqm.CArticle.family_id)
                .join(
                    sqm.CProductGroup,
                    sqm.CProductGroup.id == sqm.CFamily.product_group_id,
                )
                .join(sqm.CCatalog, sqm.CCatalog.id == sqm.CProductGroup.catalog_id)
                .where(sqm.CArticle.article_id == article_id)
                .where(sqm.CCatalog.id == catalog_id)
            )
            res = session.exec(statement).first()
        return res
    if article and catalog_id:
        with Session(engine) as session:
            statement = (
                select(sqm.CArticle)
                .join(sqm.CFamily, sqm.CFamily.id == sqm.CArticle.family_id)
                .join(
                    sqm.CProductGroup,
                    sqm.CProductGroup.id == sqm.CFamily.product_group_id,
                )
                .join(sqm.CCatalog, sqm.CCatalog.id == sqm.CProductGroup.catalog_id)
                .where(sqm.CArticle.article == article)
                .where(sqm.CCatalog.id == catalog_id)
            )
            res = session.exec(statement).first()
        return res

    if article and supplier and year:
        with Session(engine) as session:
            statement = (
                select(sqm.CArticle)
                .join(sqm.CFamily, sqm.CFamily.id == sqm.CArticle.family_id)
                .join(
                    sqm.CProductGroup,
                    sqm.CProductGroup.id == sqm.CFamily.product_group_id,
                )
                .join(sqm.CCatalog, sqm.CCatalog.id == sqm.CProductGroup.catalog_id)
                .where(sqm.CArticle.article == article)
                .where(sqm.CCatalog.supplier == supplier)
                .where(sqm.CCatalog.year == year)
            )
            res = session.exec(statement).first()
        return res
    return None


def select_product_group_by_family_id(
    engine=None, family_id: int = None
) -> sqm.CProductGroup:
    if not family_id:
        return None
    if not engine:
        engine = mdb_con.mdb_engine
    with Session(engine) as session:
        statement = (
            select(sqm.CProductGroup)
            .join(sqm.CFamily, sqm.CFamily.product_group_id == sqm.CProductGroup.id)
            .where(sqm.CFamily.id == family_id)
        )
        res = session.exec(statement).one_or_none()
    return res


def select_option(engine=None, option: sqm.COption = None) -> sqm.COption:
    if not option:
        return
    if not engine:
        engine = mdb_con.mdb_engine
    with Session(engine) as session:
        statement = (
            select(sqm.COption)
            .where(sqm.COption.option == option.option)
            .where(sqm.COption.family_id == option.family_id)
            .where(sqm.COption.type == option.type)
            .where(sqm.COption.category == option.category)
        )
        return session.exec(statement=statement).one_or_none()


def select_catalog_by_product_group_id(
    engine=None,
    product_group_id: int = None,
) -> sqm.CCatalog:
    if not product_group_id:
        return None
    if not engine:
        engine = mdb_con.mdb_engine
    with Session(engine) as session:
        statement = (
            select(sqm.CCatalog)
            .join(sqm.CProductGroup, sqm.CProductGroup.catalog_id == sqm.CCatalog.id)
            .where(sqm.CProductGroup.id == product_group_id)
        )
        res = session.exec(statement).one_or_none()
    return res


def select_family_objects_by_family_id(
    engine=None,
    family_id: int = None,
    family_obj: sqm.CArticle | sqm.CApplication | sqm.COption = None,
) -> list[sqm.CArticle | sqm.CApplication | sqm.COption]:
    if not family_id:
        return []
    if not engine:
        engine = mdb_con.mdb_engine
    with Session(engine) as session:
        statement = select(family_obj).where(family_obj.family_id == family_id)
        res = session.exec(statement).all()
    return res


def select_single_object_by_id(
    engine=None,
    object_type: SQLModel = None,
    id: int = None,
) -> SQLModel:
    if not id:
        return None
    if not object_type:
        return None
    if not engine:
        engine = mdb_con.mdb_engine
    with Session(engine) as session:
        statement = select(object_type).where(object_type.id == id)
        res = session.exec(statement=statement).one_or_none()
    return res


def translate_db_object(db_obj: SQLModel, language: str = "de") -> SQLModel:
    translated_obj = deepcopy(db_obj)
    db_obj_type = type(db_obj)
    # vd = sqm.ViewDef[db_obj_type]
    vd = viewdef.collect_viewdef(db_obj_type=db_obj_type)
    with Session(mdb_con.mdb_engine) as session:
        for vdfield in vd:
            if vd[vdfield]["is_translated"]:
                ttable_obj = select_translation_by_object_id_type_column_language(
                    parent=sup.get_table_from_sqlmodels(db_obj_type),
                    parent_id=db_obj.id,
                    column=vdfield,
                    language=language,
                )
                if ttable_obj:
                    translated_obj.__setattr__(vdfield, ttable_obj.translation)
    return translated_obj


def select_translation_by_object_id_type_column_language(
    parent: str, parent_id: int, column: str, language: str = "de"
) -> SQLModel:
    with Session(mdb_con.mdb_engine) as session:
        statement = (
            select(vdm.TDictionary)
            .join(
                vdm.TTranslationMapper,
                vdm.TTranslationMapper.dictionary_id == vdm.TDictionary.id,
            )
            .where(vdm.TTranslationMapper.parent == parent)
            .where(vdm.TTranslationMapper.parent_id == parent_id)
            .where(vdm.TTranslationMapper.columnname == column)
            .where(vdm.TDictionary.lang == language)
        )
        translation_obj = session.exec(statement).one_or_none()
        print(translation_obj)
    return translation_obj


def select_objects_generic_select(
    engine=None,
    object_type: SQLModel = None,
    where_str: str = None,
):
    if not engine:
        engine = mdb_con.mdb_engine
    if not object_type:
        return None
    if where_str:
        statement = select(object_type)
    statement = select(object_type).where(text(where_str))
    return statement


def select_objects_generic(
    engine=None,
    object_type: SQLModel = None,
    where_str: str = None,
    return_search_str: bool = False,
) -> tuple[list[SQLModel], str] | list[SQLModel]:
    if not engine:
        engine = mdb_con.mdb_engine
    if not object_type:
        return None
    statement = select_objects_generic_select(
        engine=engine, object_type=object_type, where_str=where_str
    )
    with Session(engine) as session:
        res = session.exec(statement).all()
    if return_search_str:
        return res, statement.__str__().replace('"', "")
    return res


def select_by_text_statement(
    engine=None,
    search_str: str = None,
) -> SQLModel:
    if not engine:
        engine = mdb_con.mdb_engine
    if not search_str:
        return None
    with Session(engine) as session:
        res = session.exec(text(search_str)).all()
    return res


def _build_article_list_str(family_id: int, session: Session) -> str:
    statement = select(sqm.CArticle.id).where(sqm.CArticle.family_id == family_id)
    article_ids = session.exec(statement).all()
    article_list = ""
    for art_id in article_ids:
        article_list += f"{art_id},"
    return article_list[:-1]


def select_family_urls_by_family_id(
    engine=None, family_id: int = None, include_family_articles: bool = True
) -> list[sqm.CUrl]:
    if not family_id:
        return []
    if not engine:
        engine = mdb_con.mdb_engine
    with Session(engine) as session:
        if not include_family_articles:
            statement = (
                select(sqm.CUrl)
                .where(sqm.CUrl.parent_id == family_id)
                .where(sqm.CUrl.parent == "family")
                .order_by(sqm.CUrl.id)
            )
            return session.exec(statement).all()
        article_list_str = _build_article_list_str(family_id=family_id, session=session)
    if not article_list_str:
        return select_family_urls_by_family_id(
            family_id=family_id, include_family_articles=False
        )
    with Session(engine) as session:
        statement = (
            select(sqm.CUrl)
            .where(
                text(
                    f"(curl.parent_id={family_id} and curl.parent='family') or (curl.parent_id in ({article_list_str}) and curl.parent='article')"
                )
            )
            .order_by(sqm.CUrl.id)
        )
        # print(statement)
        res = session.exec(statement).all()
    return res


def select_family_spectables_by_family_id(
    engine=None, family_id: int = None, include_family_articles: bool = True
) -> list[sqm.CSpecTable]:
    if not family_id:
        return []
    if not engine:
        engine = mdb_con.mdb_engine
    if not include_family_articles:
        with Session(engine) as session:
            statement = (
                select(sqm.CSpecTable)
                .where(sqm.CSpecTable.parent_id == family_id)
                .where(sqm.CSpecTable.parent == "family")
            )
            res = session.exec(statement).all()
        return res
    with Session(engine) as session:
        article_list_str = _build_article_list_str(family_id=family_id, session=session)
        statement = (
            select(sqm.CSpecTable)
            .where(
                text(
                    f"(parent_id={family_id} and parent='family') or (parent_id in ({article_list_str}) and parent='article')"
                )
            )
            .order_by(sqm.CSpecTable.parent)
            .order_by(sqm.CSpecTable.id)
        )
        res = session.exec(statement).all()
    return res


def select_family_spectable_items_by_family_id(
    engine=None, family_id: int = None, include_family_articles: bool = True
) -> list[sqm.CSpecTableItem]:
    if not family_id:
        return []
    if not engine:
        engine = mdb_con.mdb_engine
    if not include_family_articles:
        with Session(engine) as session:
            statement = (
                select(
                    sqm.CSpecTableItem,
                )
                .join(
                    sqm.CSpecTable,
                    sqm.CSpecTable.id == sqm.CSpecTableItem.spec_table_id,
                )
                .where(sqm.CSpecTable.parent_id == family_id)
                .where(sqm.CSpecTable.parent == "family")
                .where(sqm.CSpecTableItem.spec_table_id == sqm.CSpecTable.id)
            )
            res = session.exec(statement).all()
        return res
    with Session(engine) as session:
        article_list_str = _build_article_list_str(family_id=family_id, session=session)
        # if not article_list_str:
        #     return select_family_urls_by_family_id(family_id=family_id, include_family_articles=False)

        statement = (
            select(sqm.CSpecTableItem)
            .join(sqm.CSpecTable, sqm.CSpecTable.id == sqm.CSpecTableItem.spec_table_id)
            .where(
                text(
                    f"(parent_id={family_id} and parent='family') or (parent_id in ({article_list_str}) and parent='article')"
                )
            )
            .order_by(sqm.CSpecTable.parent)
            .order_by(sqm.CSpecTable.id)
            .order_by(sqm.CSpecTableItem.id)
        )
        res = session.exec(statement).all()
    return res


def select_category_mapping_of_family(
    engine=None,
    family_id: int = None,
) -> list[str]:
    if not family_id:
        return []
    if not engine:
        engine = mdb_con.mdb_engine
    res = []
    with Session(engine) as session:
        statement = select(sqm.CCategoryMapper).where(
            sqm.CCategoryMapper.family_id == family_id
        )
        mappings: list[sqm.CCategoryMapper] = session.exec(statement).all()
        for mapping in mappings:
            parent_list = []
            statement = select(sqm.CCategoryTree).where(
                sqm.CCategoryTree.id == mapping.category_id
            )
            cat = session.exec(statement).one_or_none()
            category = cat.category
            export_target = cat.export_target
            mapping_id = mapping.id
            while cat.parent_id != 1:
                statement = select(sqm.CCategoryTree).where(
                    sqm.CCategoryTree.id == cat.parent_id
                )
                cat = session.exec(statement).one_or_none()
                if not cat:
                    break
                parent_list.append(cat.category)
            r_str = ""
            for p in parent_list[::-1]:
                r_str += (
                    f'<a href="/database/categorymapper/edit?id={mapping_id}">[{mapping_id}]</a>&nbsp;'
                    + p
                    + " --> "
                )
            r_str += export_target + ": " + category
            res.append(r_str)
    return res


def select_ccategory_tree_export_targets():
    with Session(mdb_con.mdb_engine) as session:
        statement = (
            select(vdm.TViewDefSelectValue)
            .join(
                vdm.TViewdefColumn,
                vdm.TViewdefColumn.id == vdm.TViewDefSelectValue.columnid,
            )
            .join(vdm.TViewdefTable, vdm.TViewdefColumn.tableid == vdm.TViewdefTable.id)
            .where(vdm.TViewdefTable.tablename == "ccategorytree")
            .where(vdm.TViewdefColumn.columnname == "export_target")
        )
        res = session.exec(statement).all()
        result = []
        for target in res:
            # print(target)
            statement = (
                select(sqm.CCategoryTree)
                .where(sqm.CCategoryTree.parent_id == None)
                .where(sqm.CCategoryTree.export_target == target.value)
            )
            res_t = session.exec(statement=statement).one_or_none()
            result.append({"target": target.value, "id": res_t.id})
        return result


def select_ccategory_tree_elements_by_parent_id(
    parent_id: int | None = None, export_target: str = None
):
    with Session(mdb_con.mdb_engine) as session:
        print(parent_id)
        if parent_id == None:
            statement = (
                select(sqm.CCategoryTree)
                .where(sqm.CCategoryTree.parent_id == None)
                .where(sqm.CCategoryTree.export_target == export_target)
            )
            # print(statement)
            res = session.exec(statement=statement).one()
            parent_id = res.id
        statement = (
            select(sqm.CCategoryTree)
            .where(sqm.CCategoryTree.parent_id == parent_id)
            .where(sqm.CCategoryTree.export_target == export_target)
        )
        return session.exec(statement).all()


def select_family_from_catalog(
    engine,
    family: str = None,
    family_id: int = None,
    catalog_id: int = None,
    supplier: str = None,
    year: int = None,
) -> sqm.CFamily:
    if family_id and catalog_id:
        with Session(engine) as session:
            statement = (
                select(sqm.CFamily)
                .join(
                    sqm.CProductGroup,
                    sqm.CProductGroup.id == sqm.CFamily.product_group_id,
                )
                .join(sqm.CCatalog, sqm.CCatalog.id == sqm.CProductGroup.catalog_id)
                .where(sqm.CFamily.family_id == family_id)
                .where(sqm.CCatalog.id == catalog_id)
            )
            res = session.exec(statement).one_or_none()
        return res
    if family and catalog_id:
        with Session(engine) as session:
            statement = (
                select(sqm.CFamily)
                .join(
                    sqm.CProductGroup,
                    sqm.CProductGroup.id == sqm.CFamily.product_group_id,
                )
                .join(sqm.CCatalog, sqm.CCatalog.id == sqm.CProductGroup.catalog_id)
                .where(sqm.CFamily.family == family)
                .where(sqm.CCatalog.id == catalog_id)
            )
            res = session.exec(statement).one_or_none()
        return res
    if family and supplier and year:
        with Session(engine) as session:
            statement = (
                select(sqm.CFamily)
                .join(
                    sqm.CProductGroup,
                    sqm.CProductGroup.id == sqm.CFamily.product_group_id,
                )
                .join(sqm.CCatalog, sqm.CCatalog.id == sqm.CProductGroup.catalog_id)
                .where(sqm.CFamily.family == family)
                .where(sqm.CCatalog.supplier == supplier)
                .where(sqm.CCatalog.year == year)
            )
            res = session.exec(statement).one_or_none()
        return res
    return None


def select_catalog(
    engine=None,
    catalog_id: int = None,
    supplier: str = None,
    year: int = None,
) -> sqm.CCatalog:
    if not engine:
        engine = mdb_con.mdb_engine
    if catalog_id:
        statement = select(sqm.CCatalog).where(sqm.CCatalog.id == catalog_id)
        with Session(engine) as session:
            res = session.exec(statement).one_or_none()
        return res
    if supplier and year:
        statement = (
            select(sqm.CCatalog)
            .where(sqm.CCatalog.supplier == supplier)
            .where(year == year)
        )
        with Session(engine) as session:
            res = session.exec(statement).one_or_none()
        return res
    if supplier and year == None:
        statement = (
            select(sqm.CCatalog)
            .where(sqm.CCatalog.supplier == supplier)
            .order_by(sqm.CCatalog.insdate)
        )
        with Session(engine) as session:
            res = session.exec(statement).all()
        return res[-1]

    return None


def select_spectable(
    engine=None,
    spectable_id: int = None,
    name: str = None,
    parent_id: int = None,
    parent_type: str = None,
    st_type: str = None,
) -> sqm.CSpecTable:
    if not engine:
        engine = mdb_con.mdb_engine
    if spectable_id:
        statement = select(sqm.CSpecTable).where(sqm.CSpecTable.id == spectable_id)
        with Session(engine) as session:
            res = session.exec(statement).one_or_none()
        return res
    if parent_id and parent_type and name:
        statement = (
            select(sqm.CSpecTable)
            .where(sqm.CSpecTable.parent_id == parent_id)
            .where(sqm.CSpecTable.name == name)
        )
        with Session(engine) as session:
            res = session.exec(statement).one_or_none()
        return res
    if parent_id and parent_type and st_type:
        statement = (
            select(sqm.CSpecTable)
            .where(sqm.CSpecTable.parent_id == parent_id)
            .where(sqm.CSpecTable.type == st_type)
        )
        with Session(engine) as session:
            res = session.exec(statement).one_or_none()
        return res
    return None


def Main():
    pass


if __name__ == "__main__":
    Main()
