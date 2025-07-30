from koco_product_sqlmodel.mdb_connect.init_db_con import mdb_engine
import koco_product_sqlmodel.mdb_connect.product_groups as mdb_pg
from sqlmodel import Session, select
from koco_product_sqlmodel.dbmodels.definition import (
    CCatalog,
    CCatalogPost,
    CCatalogGet,
)


def collect_catalogs() -> list:
    with Session(mdb_engine) as session:
        statement = select(CCatalog)
        results = session.exec(statement)
        res = []
        for r in results:
            res.append({"id": r.id, "supplier": r.supplier, "year": r.year})
    return res


def collect_catalogs_db_items() -> list[CCatalog]:
    with Session(mdb_engine) as session:
        statement = select(CCatalog)
        return session.exec(statement=statement).all()


def collect_catalog_by_id(id: int) -> CCatalog | None:
    with Session(mdb_engine) as session:
        statement = select(CCatalog).where(CCatalog.id == id)
        return session.exec(statement).one_or_none()


def create_catalog(catalog: CCatalog):
    with Session(mdb_engine) as session:
        session.add(catalog)
        session.commit()
        statement = select(CCatalog).where(CCatalog.id == catalog.id)
    return session.exec(statement=statement).one_or_none()


def update_catalog(id: int | None, catalog: CCatalogPost):
    if id == None:
        return
    with Session(mdb_engine) as session:
        statement = select(CCatalog).where(CCatalog.id == id)
        cat = session.exec(statement=statement).one_or_none()
        if cat == None:
            return
        cat_data = catalog.model_dump(exclude_unset=True)
        cat = cat.sqlmodel_update(cat_data)
        session.add(cat)
        session.commit()
        session.refresh(cat)
    return cat


def main() -> None:
    pass


if __name__ == "__main__":
    main()
