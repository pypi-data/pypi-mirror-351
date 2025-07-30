from sqlmodel import select, Session, text, SQLModel
from sqlalchemy.engine import Engine
import koco_product_sqlmodel.mdb_connect.init_db_con as mdb_init
import koco_product_sqlmodel.dbmodels.changelog as sql_change
import koco_product_sqlmodel.dbmodels.definition as sql_def
import koco_product_sqlmodel.mdb_connect.generic_object_connect as mdb_gen
import koco_product_sqlmodel.mdb_connect.articles as mdb_art
import koco_product_sqlmodel.mdb_connect.applications as mdb_app
import koco_product_sqlmodel.mdb_connect.options as mdb_opt
import koco_product_sqlmodel.mdb_connect.families as mdb_fam

# import koco_product_sqlmodel.mdb_connect.product_groups as mdb_pg
import koco_product_sqlmodel.dbmodels.support as dbm_support
import koco_product_sqlmodel.fastapi.routes.search_object as r_search
import copy as copy


def get_changes(
    entity_id: int | None = None,
    entity_type: str | None = None,
    parent_id: int | None = None,
    parent_type: str | None = None,
    skip: int | None = None,
    limit: int | None = None,
    remove_last_change: bool = True,
) -> list[sql_change.CChangelogGet]:
    if entity_id != None or entity_type != None:
        changes = get_changes_for_entity_with_id(
            entity_id=entity_id, entity_type=entity_type
        )
    elif parent_id != None and parent_type != None:
        changes = get_changes_for_items_in_parent(
            parent_id=parent_id, parent_type=parent_type
        )
    else:
        changes = get_latest_changes(limit=limit)

    if remove_last_change:
        changes = remove_latest_change_of_db_entity(changes=changes)
    if changes == []:
        return changes
    changes = fill_user_name_field(changes=changes)
    limit, skip = r_search.check_limit_skip_vals(
        limit=limit, skip=skip, number_of_results=len(changes)
    )
    return sorted(changes[skip : skip + limit], key=lambda x: x.insdate, reverse=True)


def get_changes_count(
    entity_id: int | None = None,
    entity_type: str | None = None,
    parent_id: int | None = None,
    parent_type: str | None = None,
    remove_last_change: bool = True,
) -> int:
    return {
        "count": len(
            get_changes(
                entity_id=entity_id,
                entity_type=entity_type,
                parent_id=parent_id,
                parent_type=parent_type,
                remove_last_change=remove_last_change,
            )
        )
    }


def get_changes_for_items_in_parent(parent_id: int | None, parent_type: int | None):
    changes = []
    if parent_id == None or parent_type == None or parent_type == "ccatalog":
        return changes
    if parent_type == "cspectable":
        changes = _get_changed_spectable_items_for_spectable(spectable_id=parent_id)
    if parent_type == "carticle":
        changes = _get_changed_items_for_article(article_id=parent_id)
    if parent_type == "cfamily":
        changes = _get_changed_items_for_family(family_id=parent_id)
    if parent_type == "cproductgroup":
        changes = _get_changed_items_for_productgroup(productgroup_id=parent_id)
    # if parent_type == "ccatalog":
    #     changes = _get_changed_items_for_catalog(catalog_id=parent_id)
    changes += get_changes_for_entity_with_id(
        entity_id=parent_id, entity_type=parent_type
    )
    return changes


# def _get_changed_items_for_catalog(catalog_id: int) -> list[sql_change.CChangelog]:
#     productgroups = mdb_pg.get_product_group_db(catalog_id=catalog_id)
#     result = []
#     for pg in productgroups:
#         result += _get_changed_items_for_productgroup(productgroup_id=pg.id)


def _get_changed_items_for_productgroup(
    productgroup_id: int,
) -> list[sql_change.CChangelog]:
    families = mdb_fam.get_families_db(product_group_id=productgroup_id)
    result = []
    for fam in families:
        result += _get_changed_items_for_family(family_id=fam.id)
    return result


def _get_changed_items_for_family(family_id: int) -> list[sql_change.CChangelog]:
    result = []
    spectables: sql_def.CSpecTable = mdb_gen.get_objects_from_parent(
        db_obj_type=sql_def.CSpecTable, parent_id=family_id, parent="family"
    )
    for st in spectables:
        result += _get_changed_spectable_items_for_spectable(spectable_id=st.id)
        result += get_changes_for_entity_with_id(
            entity_id=st.id, entity_type="cspectable"
        )
    urls: list[sql_def.CUrl] = mdb_gen.get_objects_from_parent(
        db_obj_type=sql_def.CSpecTable, parent_id=family_id, parent="family"
    )
    for url in urls:
        result += get_changes_for_entity_with_id(entity_id=url.id, entity_type="curl")
    articles = mdb_art.get_articles_db(family_id=family_id)
    for article in articles:
        result += _get_changed_items_for_article(article_id=article.id)
        result += get_changes_for_entity_with_id(
            entity_id=article.id, entity_type="carticle"
        )
    applications = mdb_app.get_applications_db(family_id=family_id)
    for app in applications:
        result += get_changes_for_entity_with_id(
            entity_id=app.id, entity_type="capplication"
        )
    options = mdb_opt.get_options_db(family_id=family_id)
    for opt in options:
        result += get_changes_for_entity_with_id(
            entity_id=opt.id, entity_type="coptions"
        )
    return result


def _get_changed_items_for_article(article_id: int) -> list[sql_change.CChangelog]:
    result = []
    spectables: sql_def.CSpecTable = mdb_gen.get_objects_from_parent(
        db_obj_type=sql_def.CSpecTable, parent_id=article_id, parent="article"
    )
    for st in spectables:
        result += _get_changed_spectable_items_for_spectable(spectable_id=st.id)
        result += get_changes_for_entity_with_id(
            entity_id=st.id, entity_type="cspectable"
        )
    urls: list[sql_def.CUrl] = mdb_gen.get_objects_from_parent(
        db_obj_type=sql_def.CSpecTable, parent_id=article_id, parent="article"
    )
    for url in urls:
        result += get_changes_for_entity_with_id(entity_id=url.id, entity_type="curl")
    return result


def _get_changed_spectable_items_for_spectable(
    spectable_id: int,
) -> list[sql_change.CChangelog]:
    with Session(mdb_init.mdb_engine) as session:
        statement = (
            select(sql_change.CChangelog)
            .where(sql_change.CChangelog.entity_type == "cspectableitem")
            .where(
                text(
                    f"json_value(cchangelog.new_values, '$.spec_table_id')={
                        spectable_id}"
                )
            )
        )
        result = session.exec(statement=statement).all()
    return result


def remove_latest_change_of_db_entity(
    changes: list[sql_change.CChangelog],
) -> list[sql_change.CChangelog]:
    initial_list = copy.deepcopy(changes)
    new_list = []
    already_investigated = []
    worker_list = []
    for change in initial_list:
        i_obj = (change.entity_id, change.entity_type)
        if i_obj in already_investigated:
            continue
        else:
            already_investigated.append(i_obj)
        worker_list = [
            rc
            for rc in changes
            if rc.entity_id == i_obj[0] and rc.entity_type == i_obj[1]
        ]
        if (
            len(worker_list) <= 1
        ):  # only initial entry available, object was never changed
            continue
        wl = sorted(worker_list, key=lambda x: x.insdate, reverse=True)
        new_list += copy.deepcopy(wl[1:])
        worker_list = []
    return new_list


def fill_user_name_field(
    changes: list[sql_change.CChangelog],
) -> list[sql_change.CChangelogGet]:
    result = []
    for c in changes:
        r = sql_change.CChangelogGet(**c.model_dump())
        r.user_name = _get_user_name_from_id(user_id=c.user_id)
        result.append(r)
    return result


def _get_user_name_from_id(user_id: int) -> str | None:
    with Session(mdb_init.mdb_engine) as session:
        user = session.exec(
            select(sql_def.CUser).where(sql_def.CUser.id == user_id)
        ).one_or_none()
        if user != None:
            return user.last_name


def get_latest_changes(limit: int = 10) -> list[sql_change.CChangelogGet] | None:
    statement = (
        select(sql_change.CChangelog)
        .order_by(sql_change.CChangelog.insdate.desc())
        .limit(limit)
    )
    with Session(mdb_init.mdb_engine) as session:
        results = session.exec(statement=statement).all()
        return results


def get_changes_for_entity_with_id(
    entity_id: int | None,
    entity_type: str | None,
) -> list[sql_change.CChangelogGet] | None:
    if entity_id == None and entity_type == None:
        statement = select(sql_change.CChangelog)
    elif entity_type == None:
        statement = select(sql_change.CChangelog).where(
            sql_change.CChangelog.entity_id == entity_id
        )
    elif entity_id == None:
        statement = select(sql_change.CChangelog).where(
            sql_change.CChangelog.entity_type == entity_type
        )
    else:
        statement = (
            select(sql_change.CChangelog)
            .where(sql_change.CChangelog.entity_id == entity_id)
            .where(sql_change.CChangelog.entity_type == entity_type)
        )

    res = []
    with Session(mdb_init.mdb_engine) as session:
        results = session.exec(statement=statement).all()
        for r in results:
            return_res = sql_change.CChangelogGet(**r.model_dump())
            return_res.user_name = get_user_name_from_id(
                session=session, user_id=r.user_id
            )
            res.append(return_res)
    return res


def get_user_name_from_id(session: Session = None, user_id: int = None) -> str | None:
    if not user_id:
        return
    if session != None:
        statemnt_user = select(sql_def.CUser.name).where(sql_def.CUser.id == user_id)
        user_name = session.exec(statement=statemnt_user).one_or_none()
        return user_name
    with Session(mdb_init.mdb_engine) as session:
        return get_user_name_from_id(session=session, user_id=user_id)


def get_change_by_id(id: int) -> sql_change.CChangelogGet | None:
    statement = select(sql_change.CChangelog).where(sql_change.CChangelog.id == id)
    with Session(mdb_init.mdb_engine) as session:
        res = session.exec(statement=statement).one_or_none()
        if res != None:
            return_res = sql_change.CChangelogGet(**res.model_dump())
            return_res.user_name = get_user_name_from_id(user_id=res.user_id)
            return return_res


def log_results_to_db(
    entity_type: str, entity_id: int, action: str, user_id: int, new_values: str|None
):
    log_data = sql_change.CChangelog(
        entity_id=entity_id,
        entity_type=entity_type,
        action=action,
        user_id=user_id,
        new_values=new_values,
    )
    # print(log_data)
    with Session(mdb_init.mdb_engine) as session:
        session.add(instance=log_data)
        session.commit()


def write_initial_object_status_to_changelog(
    db_object: sql_def.SQLModel, user_id: int
) -> None:
    log_data = sql_change.CChangelog(
        entity_id=db_object.id,
        entity_type=dbm_support.get_table_from_sqlmodels(model=type(db_object)),
        action="POST",
        user_id=user_id,
        new_values=str(db_object.model_dump_json(exclude=("insdate", "upddate"))),
        insdate=db_object.insdate,
    )
    with Session(mdb_init.mdb_engine) as session:
        session.add(instance=log_data)
        session.commit()


def reset_changelog() -> None:
    statement_drop = """
    DROP TABLE IF EXISTS cchangelog;
    """
    statement_create = """
    CREATE TABLE cchangelog (
        id INT NOT NULL AUTO_INCREMENT,
        entity_type VARCHAR(64),
        entity_id INT NOT NULL,
        user_id INT,
        action VARCHAR(64),
        insdate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        new_values JSON,
        PRIMARY KEY(id)
    );    
    """
    with Session(mdb_init.mdb_engine) as session:
        session.exec(statement=text(statement_drop))
        session.exec(statement=text(statement_create))


def log_initial_status(logfunc: callable, obj_type: SQLModel, user_id: int = 1) -> None:
    print("Logging: ", obj_type)
    with Session(mdb_init.mdb_engine) as session:
        cats = session.exec(statement=select(obj_type)).all()
        for cat in cats:
            logfunc(db_object=cat, user_id=user_id)


def init_changelog(user_id: int) -> None:
    log_initial_status(
        logfunc=write_initial_object_status_to_changelog,
        obj_type=sql_def.CCatalog,
        user_id=user_id,
    )
    log_initial_status(
        logfunc=write_initial_object_status_to_changelog,
        obj_type=sql_def.CProductGroup,
        user_id=user_id,
    )
    log_initial_status(
        logfunc=write_initial_object_status_to_changelog,
        obj_type=sql_def.CFamily,
        user_id=user_id,
    )
    log_initial_status(
        logfunc=write_initial_object_status_to_changelog,
        obj_type=sql_def.CArticle,
        user_id=user_id,
    )
    log_initial_status(
        logfunc=write_initial_object_status_to_changelog,
        obj_type=sql_def.CSpecTable,
        user_id=user_id,
    )
    log_initial_status(
        logfunc=write_initial_object_status_to_changelog,
        obj_type=sql_def.CSpecTableItem,
        user_id=user_id,
    )
    log_initial_status(
        logfunc=write_initial_object_status_to_changelog,
        obj_type=sql_def.CApplication,
        user_id=user_id,
    )
    log_initial_status(
        logfunc=write_initial_object_status_to_changelog,
        obj_type=sql_def.COption,
        user_id=user_id,
    )
    log_initial_status(
        logfunc=write_initial_object_status_to_changelog,
        obj_type=sql_def.CUrl,
        user_id=user_id,
    )


def main():
    pass


if __name__ == "__main__":
    main()
