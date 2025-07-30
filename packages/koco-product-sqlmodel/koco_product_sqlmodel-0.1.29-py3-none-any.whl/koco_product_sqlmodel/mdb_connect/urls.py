from koco_product_sqlmodel.mdb_connect.init_db_con import mdb_engine
from sqlmodel import Session, select
from koco_product_sqlmodel.dbmodels.definition import (
    CUrl,
)


def create_curl(curl: CUrl) -> CUrl:
    with Session(mdb_engine) as session:
        session.add(curl)
        session.commit()
        statement = (
            select(CUrl)
            .where(CUrl.KOCO_url == curl.KOCO_url)
            .where(CUrl.supplier_url == curl.supplier_url)
            .where(CUrl.parent == curl.parent)
            .where(CUrl.parent_id == curl.parent_id)
            .where(CUrl.type == curl.type)
        )
    res = session.exec(statement=statement).all()
    if not res:
        return None
    nres = sorted(res, key=lambda x: x.insdate)
    return nres[-1]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
