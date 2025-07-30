from koco_product_sqlmodel.mdb_connect.init_db_con import mdb_engine
from sqlmodel import SQLModel, Session, select
from typing import Callable

# import koco_product_sqlmodel.mdb_connect.changelog as mdb_change
import koco_product_sqlmodel.dbmodels.definition as sqm
import koco_product_sqlmodel.dbmodels.viewdef as vd
import koco_product_sqlmodel.dbmodels.support as sup
import os
import datetime as dt


def isnull(input, output):
    if not input:
        return output
    return input


def check_field_for_update(old_val: str, new_val: str):
    if old_val == new_val:
        return old_val, False
    return new_val, True


def translate_url_type(in_t: tuple = None) -> tuple:
    td = {
        "photo": "Photo",
        "step": "Step",
        "drawing": "Drawing",
        "datasheet": "Datasheet",
        "software": "Software",
        "supplier_site": "Supplier website",
        "speed_curves": "Speed curves",
        "screw_option": "Screw option",
        "torque_performance_curve": "Torque performance curve",
        "force_curve": "Force curce",
        "accessories": "Accessories",
        "product_datasheet": "Product datasheet",
        "manual": "Manual",
        "user_interface_software": "User interface software",
        "catalog": "Catalog",
        "certifications": "Certificates",
    }
    for element in in_t:
        element.type = td[element.type]
    return in_t


def create_mapper_table():
    SQLModel.metadata.create_all(mdb_engine)


def backup_database(
    fileurl: str = None, db_backup_folder: str = None, shell_com_path: str = None
) -> int:
    if not fileurl:
        fileurl = os.path.join(
            db_backup_folder,
            dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d-%H-%M-%S")
            + "_db_backup.sql",
        )
    if not os.path.exists(db_backup_folder):
        os.makedirs(db_backup_folder, mode=0o777, exist_ok=True)
    if not os.path.exists(db_backup_folder):
        return -1
    mysql_cmd = os.path.join(shell_com_path, "mysqldump")
    os.system(
        f"{mysql_cmd} -u {os.environ["MARIADB_USER"]} -p'{os.environ["MARIADB_PW"]}' {os.environ["MARIADB_DATABASE"]} > {os.path.join(db_backup_folder,fileurl)}"
    )
    if not os.path.exists(fileurl):
        return -1
    return 1


def restore_database(fileurl: str = None, shell_com_path: str = None):
    if not fileurl:
        return -1
    if not os.path.exists(fileurl):
        return -1
    mysql_cmd = os.path.join(shell_com_path, "mysql")
    os.system(
        f"{mysql_cmd} -u {os.environ["MARIADB_USER"]} -p'{os.environ["MARIADB_PW"]}' {os.environ["MARIADB_DATABASE"]} < {fileurl}"
    )
    return 1


def delete_database_backup(fileurl: str = None):
    if not fileurl:
        return -1
    if not os.path.exists(fileurl):
        return -1
    os.remove(fileurl)
    return 1


def update_object(db_object: SQLModel, update_data: dict):
    with Session(mdb_engine) as session:
        print(update_data)
        for d in update_data:
            db_object.__setattr__(d, update_data[d])
        session.add(db_object)
        session.commit()


def create_object(db_object_type: SQLModel, data: dict) -> SQLModel:
    db_obj = db_object_type()
    with Session(mdb_engine) as session:
        for d in data:
            db_obj.__setattr__(d, data[d])
        session.add(db_obj)
        session.commit()
        n_obj = session.exec(
            select(db_object_type).order_by(db_object_type.id.desc()).limit(1)
        ).one_or_none()
    return n_obj


def delete_translations_by_object_id(obj_id: int, object_type: SQLModel):
    with Session(mdb_engine) as session:
        statement = (
            select(vd.TTranslationMapper)
            .where(
                vd.TTranslationMapper.parent
                == sup.get_table_from_sqlmodels(object_type)
            )
            .where(vd.TTranslationMapper.parent_id == obj_id)
        )
        res = session.exec(statement)
        for object in res.all():
            session.delete(object)
        session.commit()


def delete_object_by_id(
    log_func: Callable[[str, int, str, int, str], None],
    obj_id: int,
    object_type: SQLModel,
    delete_connected_items: bool = False,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        if not delete_connected_items:
            statement = select(object_type).where(object_type.id == obj_id)
            res = session.exec(statement)
            res = res.one_or_none()
            session.delete(res)
            log_func(
                entity_type=sup.get_table_from_sqlmodels(model=object_type),
                entity_id=res.id,
                action="DELETE",
                user_id=user_id,
                new_values=None,
            )
            session.commit()
            return
        if object_type in (
            sqm.CUrl,
            sqm.CApplication,
            sqm.CSpecTableItem,
            sqm.CBacklog,
            sqm.COption,
            sqm.CCategoryMapper,
            sqm.CCategoryTree,
        ):
            statement = select(object_type).where(object_type.id == obj_id)
            res = session.exec(statement)
            res = res.one_or_none()
            session.delete(res)
            log_func(
                entity_type=sup.get_table_from_sqlmodels(model=object_type),
                entity_id=res.id,
                action="DELETE",
                user_id=user_id,
                new_values=None,
            )
            session.commit()
    if object_type == sqm.CSpecTable:
        delete_spectable_by_id(
            log_func=log_func,
            spectable_id=obj_id,
            delete_connected_items=True,
            user_id=user_id,
        )
        return
    if object_type == sqm.CArticle:
        delete_article_by_id(
            log_func=log_func,
            article_id=obj_id,
            delete_connected_items=True,
            user_id=user_id,
        )
        return
    if object_type == sqm.CFamily:
        delete_family_by_id(
            log_func=log_func,
            family_id=obj_id,
            delete_connected_items=True,
            user_id=user_id,
        )
        return
    if object_type == sqm.CProductGroup:
        delete_product_group_by_id(
            log_func=log_func,
            product_group_id=obj_id,
            delete_connected_items=True,
            user_id=user_id,
        )
        return
    if object_type == sqm.CCatalog:
        delete_catalog_by_id(
            log_func=log_func,
            catalog_id=obj_id,
            delete_connected_items=True,
            user_id=user_id,
        )
        return
    delete_translations_by_object_id(obj_id=obj_id, object_type=object_type)


def delete_catalog_by_id(
    log_func: Callable[[str, int, str, int, str], None],
    catalog_id: int,
    delete_connected_items: bool = False,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        cat = session.exec(
            select(sqm.CCatalog).where(sqm.CCatalog.id == catalog_id)
        ).one_or_none()
    if cat:
        delete_catalog(
            log_func=log_func,
            catalog=cat,
            delete_connected_items=delete_connected_items,
            user_id=user_id,
        )


def delete_catalog(
    log_func: Callable[[str, int, str, int, str], None],
    catalog: sqm.CCatalog,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    if delete_connected_items:
        _delete_product_groups_from_catalog(
            log_func=log_func,
            catalog=catalog,
            delete_connected_items=True,
            user_id=user_id,
        )
    with Session(mdb_engine) as session:
        log_func(
            entity_type="ccatalog",
            entity_id=catalog.id,
            action="DELETE",
            user_id=user_id,
            new_values=None,
        )
        session.delete(catalog)
        session.commit()


def _delete_product_groups_from_catalog(
    log_func: Callable[[str, int, str, int, str], None],
    catalog: sqm.CCatalog,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = select(sqm.CProductGroup).where(
            sqm.CProductGroup.catalog_id == catalog.id
        )
        res = session.exec(statement)
        pgs = res.all()
    for pg in pgs:
        delete_product_group(
            log_func=log_func,
            product_group=pg,
            delete_connected_items=delete_connected_items,
            user_id=user_id,
        )


def delete_product_group_by_id(
    log_func: Callable[[str, int, str, int, str], None],
    product_group_id: int,
    delete_connected_items: bool = False,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        pg = session.exec(
            select(sqm.CProductGroup).where(sqm.CProductGroup.id == product_group_id)
        ).one_or_none()
    if pg:
        delete_product_group(
            log_func=log_func,
            product_group=pg,
            delete_connected_items=delete_connected_items,
            user_id=user_id,
        )


def delete_product_group(
    log_func: Callable[[str, int, str, int, str], None],
    product_group: sqm.CProductGroup,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    if delete_connected_items:
        _delete_filedata_from_product_group(log_func=log_func, pg=product_group, user_id=user_id)
        _delete_families_from_product_group(
            log_func=log_func,
            product_group=product_group,
            delete_connected_items=True,
            user_id=user_id,
        )
    with Session(mdb_engine) as session:
        log_func(
            entity_type="cproductgroup",
            entity_id=product_group.id,
            action="DELETE",
            user_id=user_id,
            new_values=None,
        )
        session.delete(product_group)
        session.commit()

def _delete_filedata_from_product_group(
    log_func: Callable[[str, int, str, int, str], None],
    pg: sqm.CProductGroup,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = (
            select(sqm.CFileData)
            .where(sqm.CFileData.entity_id == pg.id)
            .where(sqm.CFileData.entity_type == "cproductgroup")
        )
        res = session.exec(statement).all()
    for fd in res:
        _delete_filedata(log_func=log_func, fd=fd, user_id=user_id)

def _delete_families_from_product_group(
    log_func: Callable[[str, int, str, int, str], None],
    product_group: sqm.CProductGroup,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = select(sqm.CFamily).where(
            sqm.CFamily.product_group_id == product_group.id
        )
        res = session.exec(statement)
        families = res.all()
    for fam in families:
        delete_family(
            log_func=log_func,
            family=fam,
            delete_connected_items=delete_connected_items,
            user_id=user_id,
        )


def delete_family_by_id(
    log_func: Callable[[str, int, str, int, str], None],
    family_id: int,
    delete_connected_items: bool = False,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        fam = session.exec(
            select(sqm.CFamily).where(sqm.CFamily.id == family_id)
        ).one_or_none()
    if fam:
        delete_family(
            log_func=log_func,
            family=fam,
            delete_connected_items=delete_connected_items,
            user_id=user_id,
        )


def delete_family(
    log_func: Callable[[str, int, str, int, str], None],
    family: sqm.CFamily,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    if delete_connected_items:
        _delete_urls_from_family(log_func=log_func, family=family, user_id=user_id)
        _delete_filedata_from_family(log_func=log_func, family=family, user_id=user_id)
        _delete_options_from_family(log_func=log_func, family=family, user_id=user_id)
        _delete_applications_from_family(
            log_func=log_func, family=family, user_id=user_id
        )
        _delete_spectables_from_family(
            log_func=log_func,
            family=family,
            delete_connected_items=True,
            user_id=user_id,
        )
        _delete_articles_from_family(
            log_func=log_func,
            family=family,
            delete_connected_items=True,
            user_id=user_id,
        )
        _delete_family_from_category_mapper(family=family)
    with Session(mdb_engine) as session:
        if user_id:
            log_func(
                entity_type="cfamily",
                entity_id=family.id,
                action="DELETE",
                user_id=user_id,
                new_values=None,
            )
        session.delete(family)
        session.commit()


def delete_category_mapping_by_id(mapping_id: int):
    with Session(mdb_engine) as session:
        mapping = session.exec(
            select(sqm.CCategoryMapper).where(sqm.CCategoryMapper.id == mapping_id)
        ).one_or_none()
    if mapping:
        session.delete(mapping)
        session.commit()


def _delete_family_from_category_mapper(family: sqm.CFamily) -> None:
    with Session(mdb_engine) as session:
        statement = select(sqm.CCategoryMapper).where(
            sqm.CCategoryMapper.family_id == family.id
        )
        res = session.exec(statement)
        mappings = res.all()
    for mapping in mappings:
        delete_category_mapping_by_id(mapping_id=mapping.id)


def _delete_articles_from_family(
    log_func: Callable[[str, int, str, int, str], None],
    family: sqm.CFamily,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = select(sqm.CArticle).where(sqm.CArticle.family_id == family.id)
        res = session.exec(statement)
        articles = res.all()
    for art in articles:
        delete_article(
            log_func=log_func,
            article=art,
            delete_connected_items=delete_connected_items,
            user_id=user_id,
        )

def _delete_spectables_from_family(
    log_func: Callable[[str, int, str, int, str], None],
    family: sqm.CFamily,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = (
            select(sqm.CSpecTable)
            .where(sqm.CSpecTable.parent == "family")
            .where(sqm.CSpecTable.parent_id == family.id)
        )
        res = session.exec(statement).all()
    for st in res:
        delete_spectable(
            log_func=log_func,
            spectable=st,
            delete_connected_items=delete_connected_items,
            user_id=user_id,
        )

def _delete_urls_from_family(
    log_func: Callable[[str, int, str, int, str], None],
    family: sqm.CFamily,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = (
            select(sqm.CUrl)
            .where(sqm.CUrl.parent_id == family.id)
            .where(sqm.CUrl.parent == "family")
        )
        res = session.exec(statement).all()
    for url in res:
        _delete_url(log_func=log_func, url=url, user_id=user_id)

def _delete_filedata_from_family(
    log_func: Callable[[str, int, str, int, str], None],
    family: sqm.CFamily,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = (
            select(sqm.CFileData)
            .where(sqm.CFileData.entity_id == family.id)
            .where(sqm.CFileData.entity_type == "cfamily")
        )
        res = session.exec(statement).all()
    for fd in res:
        _delete_filedata(log_func=log_func, fd=fd, user_id=user_id)

def _delete_options_from_family(
    log_func: Callable[[str, int, str, int, str], None],
    family: sqm.CFamily,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = select(sqm.COption).where(sqm.COption.family_id == family.id)
        res = session.exec(statement).all()
    for option in res:
        _delete_option(log_func=log_func, option=option, user_id=user_id)


def _delete_applications_from_family(
    log_func: Callable[[str, int, str, int, str], None],
    family: sqm.CFamily,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = select(sqm.CApplication).where(
            sqm.CApplication.family_id == family.id
        )
        res = session.exec(statement).all()
    for application in res:
        _delete_application(log_func=log_func, application=application, user_id=user_id)


def delete_spectable_by_id(
    log_func: Callable[[str, int, str, int, str], None],
    spectable_id: int,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        st = session.exec(
            select(sqm.CSpecTable).where(sqm.CSpecTable.id == spectable_id)
        ).one_or_none()
    if st:
        delete_spectable(
            log_func=log_func,
            spectable=st,
            delete_connected_items=delete_connected_items,
            user_id=user_id,
        )


def delete_spectable(
    log_func: Callable[[str, int, str, int, str], None],
    spectable: sqm.CSpecTable,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    if delete_connected_items:
        _delete_spectableitems_from_spectable(
            log_func=log_func, spectable=spectable, user_id=user_id
        )
    with Session(mdb_engine) as session:
        if user_id != None:
            log_func(
                entity_type="cspectable",
                entity_id=spectable.id,
                action="DELETE",
                user_id=user_id,
                new_values=None,
            )
        session.delete(spectable)
        session.commit()


def delete_spectableitem_by_id(
        log_func: Callable[[str, int, str, int, str], None],
        spectableitem_id: int,
        user_id: int | None = None,
        ) -> None:
    with Session(mdb_engine) as session:
        sti = session.exec(
            select(sqm.CSpecTableItem).where(
                sqm.CSpecTableItem.id == spectableitem_id
            )
        ).one_or_none()
        if sti==None:
            return
        if user_id != None:
            log_func(
                entity_type="ccspectableitem",
                entity_id=sti.id,
                action="DELETE",
                user_id=user_id,
                new_values=None,
            )
        session.delete(sti)
        session.commit()
    

def _delete_spectableitems_from_spectable(
    log_func: Callable[[str, int, str, int, str], None],
    spectable: sqm.CSpecTable,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        stis = session.exec(
            select(sqm.CSpecTableItem).where(
                sqm.CSpecTableItem.spec_table_id == spectable.id
            )
        ).all()
        for sti in stis:
            if user_id != None:
                log_func(
                    entity_type="ccspectableitem",
                    entity_id=sti.id,
                    action="DELETE",
                    user_id=user_id,
                    new_values=None,
                )
            session.delete(sti)
        session.commit()


def delete_article_by_id(
    log_func: Callable[[str, int, str, int, str], None],
    article_id: int,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        art = session.exec(
            select(sqm.CArticle).where(sqm.CArticle.id == article_id)
        ).one_or_none()
    if art:
        delete_article(
            log_func=log_func,
            article=art,
            delete_connected_items=delete_connected_items,
            user_id=user_id,
        )


def delete_article(
    log_func: Callable[[str, int, str, int, str], None],
    article: sqm.CArticle,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    if delete_connected_items:
        _delete_urls_from_article(log_func=log_func, article=article, user_id=user_id)
        _delete_filedata_from_article(log_func=log_func, article=article, user_id=user_id)
        _delete_spectables_from_article(
            log_func=log_func,
            article=article,
            delete_connected_items=True,
            user_id=user_id,
        )
    with Session(mdb_engine) as session:
        session.delete(article)
        log_func(
            entity_type="carticle",
            entity_id=article.id,
            action="DELETE",
            user_id=user_id,
            new_values=None,
        )
        session.commit()


def _delete_spectables_from_article(
    log_func: Callable[[str, int, str, int, str], None],
    article: sqm.CArticle,
    delete_connected_items: bool = True,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = (
            select(sqm.CSpecTable)
            .where(sqm.CSpecTable.parent == "article")
            .where(sqm.CSpecTable.parent_id == article.id)
        )
        res = session.exec(statement).all()
    for st in res:
        delete_spectable(
            log_func=log_func,
            spectable=st,
            delete_connected_items=delete_connected_items,
            user_id=user_id,
        )


def _delete_urls_from_article(
    log_func: Callable[[str, int, str, int, str], None],
    article: sqm.CArticle,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = (
            select(sqm.CUrl)
            .where(sqm.CUrl.parent_id == article.id)
            .where(sqm.CUrl.parent == "article")
        )
        res = session.exec(statement).all()
    for url in res:
        _delete_url(log_func=log_func, url=url, user_id=user_id)

def _delete_url(
    log_func: Callable[[str, int, str, int, str], None],
    url: sqm.CUrl,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        if user_id != None:
            log_func(
                entity_type="curl",
                entity_id=url.id,
                action="DELETE",
                user_id=user_id,
                new_values=None,
            )
        session.delete(url)
        session.commit()

def _delete_filedata_from_article(
    log_func: Callable[[str, int, str, int, str], None],
    article: sqm.CArticle,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        statement = (
            select(sqm.CFileData)
            .where(sqm.CFileData.entity_id == article.id)
            .where(sqm.CFileData.entity_type == "carticle")
        )
        res = session.exec(statement).all()
    for fd in res:
        _delete_filedata(log_func=log_func, fd=fd, user_id=user_id)


def _delete_filedata(
    log_func: Callable[[str, int, str, int, str], None],
    fd: sqm.CFileData,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        if user_id != None:
            log_func(
                entity_type="cfiledata",
                entity_id=fd.id,
                action="DELETE",
                user_id=user_id,
                new_values=None,
            )
        session.delete(fd)
        session.commit()


def _delete_option(
    log_func: Callable[[str, int, str, int, str], None],
    option: sqm.COption,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        if user_id != None:
            log_func(
                entity_type="coption",
                entity_id=option.id,
                action="DELETE",
                user_id=user_id,
                new_values=None,
            )
        session.delete(option)
        session.commit()


def _delete_application(
    log_func: Callable[[str, int, str, int, str], None],
    application: sqm.CApplication,
    user_id: int | None = None,
):
    with Session(mdb_engine) as session:
        if user_id != None:
            log_func(
                entity_type="capplication",
                entity_id=application.id,
                action="DELETE",
                user_id=user_id,
                new_values=None,
            )
        session.delete(application)
        session.commit()


def insert_category_mapping(category_id: int, export_target: str, family_id: int):
    with Session(mdb_engine) as session:
        statement = (
            select(sqm.CCategoryMapper)
            .where(sqm.CCategoryMapper.category_id == category_id)
            .where(sqm.CCategoryMapper.family_id == family_id)
        )
        res = session.exec(statement).one_or_none()
        if res:
            return
        cm = sqm.CCategoryMapper(
            category_id=category_id, family_id=family_id, export_target=export_target
        )
        session.add(cm)
        session.commit()


def collect_category_tree(pid: int = 1) -> dict[dict[dict]]:
    rd = []
    with Session(mdb_engine) as session:
        rd = _get_ct_children(session, pid=pid, level=1)
    return rd


def _get_ct_children(session, pid: int = None, level: int = None):
    if level > 3:
        return None
    if pid == None:
        return None
    children = {}
    statement = (
        select(sqm.CCategoryTree)
        .where(sqm.CCategoryTree.parent_id == pid)
        .order_by(sqm.CCategoryTree.pos)
    )
    layer1 = session.exec(statement).all()
    for child in layer1:
        statement = (
            select(sqm.CUrl)
            .where(sqm.CUrl.parent == "categorytree")
            .where(sqm.CUrl.parent_id == child.id)
            .where(sqm.CUrl.type == "photo")
        )
        urls = session.exec(statement).all()
        children[child.id] = {
            "node": child,
            "children": _get_ct_children(session, pid=child.id, level=level + 1),
            "urls": urls,
        }
    return children


def _add_category_photo_url(cat_id: int = None, KOCO_url: str = None):
    url = sqm.CUrl(
        type="photo",
        KOCO_url=KOCO_url,
        parent_id=cat_id,
        parent="categorytree",
        user_id=1,
    )
    print(url)
    with Session(mdb_engine) as session:
        session.add(url)
        session.commit()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
