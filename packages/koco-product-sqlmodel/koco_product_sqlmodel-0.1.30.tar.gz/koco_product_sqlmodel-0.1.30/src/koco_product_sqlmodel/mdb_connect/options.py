from koco_product_sqlmodel.mdb_connect.init_db_con import mdb_engine
from sqlmodel import Session, select
from koco_product_sqlmodel.dbmodels.definition import COption, COptionGet, COptionPost


def create_option(option: COption):
    with Session(mdb_engine) as session:
        session.add(option)
        session.commit()
        statement = (
            select(COption)
            .where(COption.option == option.option)
            .where(COption.family_id == option.family_id)
            .where(COption.category == option.category)
            .where(COption.type == option.type)
        )
    return session.exec(statement=statement).one_or_none()


def update_option_DB(id: int | None, opt_post: COptionPost) -> COption | None:
    if id == None:
        return
    with Session(mdb_engine) as session:
        statement = select(COption).where(COption.id == id)
        opt = session.exec(statement=statement).one_or_none()
        if opt == None:
            return
        opt_data = opt_post.model_dump(exclude_unset=True)
        opt = opt.sqlmodel_update(opt_data)
        session.add(opt)
        session.commit()
        session.refresh(opt)
    return opt


def get_options_db(family_id: int | None) -> list[COptionGet]:
    if family_id == None:
        statement = select(COption)
    else:
        statement = select(COption).where(COption.family_id == family_id)
    with Session(mdb_engine) as session:
        return session.exec(statement=statement).all()


def get_option_db_by_id(id: int) -> COption:
    if not id:
        return
    statement = select(COption).where(COption.id == id)
    with Session(mdb_engine) as session:
        return session.exec(statement=statement).one_or_none()


def delete_option_by_id(id: int) -> int | None:
    statement = select(COption).where(COption.id == id)
    with Session(mdb_engine) as session:
        opt = session.exec(statement=statement).one_or_none()
        if opt == None:
            return
        session.delete(opt)
        session.commit()
        return 1


def main() -> None:
    pass


if __name__ == "__main__":
    main()
