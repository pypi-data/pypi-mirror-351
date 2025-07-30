from koco_product_sqlmodel.mdb_connect.init_db_con import mdb_engine
from sqlmodel import Session, select
from koco_product_sqlmodel.dbmodels.definition import (
    CCatalog,
    CProductGroup,
    CProductGroupPost,
    CProductGroupGet,
)


def create_productgroup(product_group: CProductGroup) -> CProductGroup:
    if not product_group:
        return
    with Session(mdb_engine) as session:
        session.add(product_group)
        session.commit()
        statement = (
            select(CProductGroup)
            .where(CProductGroup.product_group == product_group.product_group)
            .where(CProductGroup.catalog_id == product_group.catalog_id)
        )
        pgn = session.exec(statement=statement).one_or_none()
        return pgn


def collect_product_groups(
    supplier: str = None,
    year: int = None,
    catalog_id: int = None,
    image_not_found_png: str = "/img/koco.png",
):
    with Session(mdb_engine) as session:
        if catalog_id:
            statement = (
                select(CProductGroup)
                .where(CProductGroup.catalog_id == catalog_id)
                .order_by(CProductGroup.id)
            )
            results = session.exec(statement).all()
            statement = select(CCatalog).where(CCatalog.id == catalog_id)
            cat = session.exec(statement).one_or_none()
            if cat:
                supplier = cat.supplier
        elif year:
            statement = (
                select(CProductGroup)
                .join(CCatalog, CCatalog.id == CProductGroup.catalog_id)
                .where(CCatalog.supplier == supplier)
                .where(CCatalog.year == year)
                .order_by(CProductGroup.id)
            )
            results = session.exec(statement).all()
        elif supplier:
            statement = (
                select(CCatalog).where(CCatalog.supplier == supplier).order_by(year)
            )
            cats = session.exec(statement).all()
            if cats:
                cat = cats[-1]
            else:
                return None, None
            statement = (
                select(CProductGroup)
                .where(CProductGroup.catalog_id == cat.id)
                .order_by(CProductGroup.id)
            )
            results = session.exec(statement).all()
        else:
            statement = select(CProductGroup).order_by(CProductGroup.id)
            results = session.exec(statement).all()
        for r in results:
            if not r.image_url:
                r.image_url = image_not_found_png

    return results, supplier


def collect_product_group_by_id(id: int) -> CProductGroup | None:
    with Session(mdb_engine) as session:
        statement = select(CProductGroup).where(CProductGroup.id == id)
        return session.exec(statement=statement).one_or_none()


def get_product_group_db(catalog_id: int = None) -> list[CProductGroup]:
    if not catalog_id:
        statement = select(CProductGroup)
    else:
        statement = select(CProductGroup).where(CProductGroup.catalog_id == catalog_id)
    with Session(mdb_engine) as session:
        return session.exec(statement=statement).all()


def update_product_group(
    id: int | None, pg_post: CProductGroupPost
) -> CProductGroup | None:
    if id == None:
        return
    with Session(mdb_engine) as session:
        statement = select(CProductGroup).where(CProductGroup.id == id)
        pg = session.exec(statement=statement).one_or_none()
        if pg == None:
            return
        pg_data = pg_post.model_dump(exclude_unset=True)
        pg = pg.sqlmodel_update(pg_data)
        session.add(pg)
        session.commit()
        session.refresh(pg)
    return pg


def main() -> None:
    pass


if __name__ == "__main__":
    main()
