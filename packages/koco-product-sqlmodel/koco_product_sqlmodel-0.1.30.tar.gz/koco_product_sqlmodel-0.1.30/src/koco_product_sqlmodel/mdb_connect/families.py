from sqlmodel import Session, select
import koco_product_sqlmodel.mdb_connect.mdb_connector as mdb_con
import koco_product_sqlmodel.dbmodels.definition as sql_def


def create_family(family: sql_def.CFamily) -> sql_def.CFamily:
    if not family:
        return
    with Session(mdb_con.mdb_engine) as session:
        session.add(family)
        session.commit()
        statement = (
            select(sql_def.CFamily)
            .where(sql_def.CFamily.family == family.family)
            .where(sql_def.CFamily.product_group_id == family.product_group_id)
        )
        return session.exec(statement=statement).one_or_none()


def create_family_DB(family: sql_def.CFamilyPost) -> sql_def.CFamily:
    if not family:
        return
    with Session(mdb_con.mdb_engine) as session:
        session.add(family)
        session.commit()
        statement = (
            select(sql_def.CFamily)
            .where(sql_def.CFamily.family == family.family)
            .where(sql_def.CFamily.product_group_id == family.product_group_id)
        )
        return session.exec(statement=statement).one_or_none()


def update_family_DB(id: int | None, fam_post: sql_def.CFamilyPost) -> sql_def.CFamily | None:
    if id == None:
        return
    with Session(mdb_con.mdb_engine) as session:
        statement = select(sql_def.CFamily).where(sql_def.CFamily.id == id)
        fam = session.exec(statement=statement).one_or_none()
        if fam == None:
            return
        fam_data = fam_post.model_dump(exclude_unset=True)
        fam = fam.sqlmodel_update(fam_data)
        session.add(fam)
        session.commit()
        session.refresh(fam)
    return fam


# def collect_families(product_group_id: int = 1):
#     with Session(mdb_engine) as session:
#         statement = select(CFamily).where(CFamily.product_group_id == product_group_id)
#         results = session.exec(statement)
#         res = []
#         for r in results.all():
#             statement = (
#                 select(CUrl.KOCO_url)
#                 .where(CUrl.parent_id == r.id)
#                 .where(CUrl.parent == "family")
#                 .where(CUrl.type == "photo")
#             )
#             KOCO_url = session.exec(statement).first()
#             res.append({"family": r, "url": KOCO_url})
#         # print(product_group_id)
#         statement = (
#             select(CProductGroup.product_group, CCatalog.supplier, CCatalog.id)
#             .join(CCatalog, CCatalog.id == CProductGroup.catalog_id)
#             .where(CProductGroup.id == product_group_id)
#         )
#         result = session.exec(statement).one_or_none()
#         info = {"product_group": "", "catalog_id": None, "supplier": ""}
#         if result:
#             info = {
#                 "product_group": result[0],
#                 "catalog_id": result[2],
#                 "supplier": result[1],
#             }
#     mappings = {}
#     for r in res:
#         mappings[r["family"].id] = select_category_mapping_of_family(
#             family_id=r["family"].id
#         )
#     # print (res, info)

#     return res, info, mappings


# def set_excel_import_values(engine=None, family: CFamily = None) -> CFamily:
#     if not family:
#         return None
#     if not engine:
#         engine = mdb_engine
#     with Session(engine) as session:
#         statement = (
#             select(CFamily)
#             .where(CFamily.family == family.family)
#             .where(CFamily.product_group_id == family.product_group_id)
#         )
#         nfam = session.exec(statement=statement).one_or_none()
#         if nfam:
#             nfam.description = family.description
#             nfam.short_description = family.short_description
#             nfam.type = family.type
#             session.add(nfam)
#             session.commit()
#             nfam = session.exec(statement=statement).one_or_none()
#         return nfam


# def collect_family(family_id: int = 1, table_header_hrefs: bool = True) -> dict:
#     with Session(mdb_engine) as session:
#         # print("Collecting family")
#         statement = select(CFamily).where(CFamily.id == family_id)
#         results = session.exec(statement)
#         family = {}
#         r = results.one_or_none()
#         statement = (
#             select(CUrl.KOCO_url)
#             .where(CUrl.parent_id == family_id)
#             .where(CUrl.parent == "family")
#             .where(CUrl.type == "photo")
#         )
#         image_url = session.exec(statement).first()
#         # print(r)
#         family["family"] = {
#             "id": r.id,
#             "family": r.family,
#             "type": r.type,
#             "product_group_id": r.product_group_id,
#             "image_url": image_url,
#             "insdate": r.insdate,
#             "upddate": r.upddate,
#             "status": r.status,
#             "user": r.user_id,
#         }
#         statement = (
#             select(CApplication.application)
#             .where(CApplication.family_id == family_id)
#             .order_by(CApplication.id)
#         )
#         results = session.exec(statement)
#         applications = [r for r in results]
#         if applications:
#             family["applications"] = applications
#         statement = (
#             select(COption)
#             .where(COption.family_id == family_id)
#             .where(COption.type == "Options")
#             .order_by(COption.id)
#         )
#         results = session.exec(statement)
#         # options=[r for r in results]
#         if results:
#             out_opts = _rearrange_options_for_category(results)
#             if out_opts:
#                 family["options"] = out_opts
#         # print(family['options'])
#         statement = (
#             select(COption.option)
#             .where(COption.family_id == family_id)
#             .where(COption.type == "Features")
#             .order_by(COption.id)
#         )
#         results = session.exec(statement)
#         features = [r for r in results]
#         if features:
#             family["features"] = features
#         statement = (
#             select(CCatalog.id, CCatalog.supplier, CProductGroup.product_group)
#             .join(CProductGroup)
#             .where(family["family"]["product_group_id"] == CProductGroup.id)
#         )
#         results = session.exec(statement)
#         r = results.first()
#         family["family"]["catalog_id"] = r[0]
#         statement = (
#             select(CUrl)
#             .where(CUrl.parent_id == family_id)
#             .where(CUrl.parent == "family")
#         )
#         results = session.exec(statement).all()
#         family["family"]["urls"] = translate_url_type(results)
#         durls = [durl for durl in family["family"]["urls"] if _url_is_drawing(durl)]
#         durls = sorted(durls, key=lambda t: t.type)
#         if durls:
#             family["family"]["durls"] = durls
#         family["supplier"] = r[1]
#         family["product_group"] = r[2]
#     family["articles"] = collect_overview_spectables(
#         fam_info=family, family_id=family_id, table_header_hrefs=table_header_hrefs
#     )
#     family["family"]["st"] = collect_family_spectables(family_id=family_id)
#     family["mappings"] = select_category_mapping_of_family(family_id=family_id)
#     return family


def get_families_db(product_group_id: int = None) -> list[sql_def.CFamily]:
    if not product_group_id:
        statement = select(sql_def.CFamily)
    else:
        statement = select(sql_def.CFamily).where(sql_def.CFamily.product_group_id == product_group_id)
    with Session(mdb_con.mdb_engine) as session:
        return session.exec(statement=statement).all()


def get_family_db_by_id(id: int) -> sql_def.CFamily:
    statement = select(sql_def.CFamily).where(sql_def.CFamily.id == id)
    with Session(mdb_con.mdb_engine) as session:
        return session.exec(statement=statement).one_or_none()


# def _url_is_drawing(url: CUrl) -> bool:
#     try:
#         ext_str = path.splitext(url.KOCO_url)[1].lower()
#     except:
#         return False
#     if ext_str in (
#         ".png",
#         ".jpg",
#         ".jpeg",
#         ".gif",
#         ".bmp",
#     ):
#         return True
#     return False


# def _rearrange_options_for_category(options: list) -> dict:
#     out_opts = {}
#     # out_opts['General']=[]
#     gen_opts = []
#     for opt in options:
#         if opt.category == None:
#             gen_opts.append(opt.option)
#         else:
#             if opt.category in out_opts:
#                 out_opts[opt.category].append(opt.option)
#             else:
#                 out_opts[opt.category] = [opt.option]
#     if gen_opts:
#         out_opts["General"] = gen_opts
#     return out_opts


def main() -> None:
    pass


if __name__ == "__main__":
    main()
