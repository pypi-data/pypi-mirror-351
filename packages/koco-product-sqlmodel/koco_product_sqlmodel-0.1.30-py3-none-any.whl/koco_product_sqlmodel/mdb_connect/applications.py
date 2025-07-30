from koco_product_sqlmodel.mdb_connect.init_db_con import mdb_engine
from sqlmodel import Session, select
from koco_product_sqlmodel.dbmodels.definition import (
    CApplication,
    CApplicationGet,
    CApplicationPost,
)


def create_application(application: CApplication):
    with Session(mdb_engine) as session:
        session.add(application)
        session.commit()
        statement = (
            select(CApplication)
            .where(CApplication.application == application.application)
            .where(
                CApplication.family_id == application.family_id,
            )
        )
    return session.exec(statement=statement).one_or_none()


def update_application_DB(
    id: int | None, app_post: CApplicationPost
) -> CApplication | None:
    if id == None:
        return
    with Session(mdb_engine) as session:
        statement = select(CApplication).where(CApplication.id == id)
        app = session.exec(statement=statement).one_or_none()
        if app == None:
            return
        app_data = app_post.model_dump(exclude_unset=True)
        app = app.sqlmodel_update(app_data)
        session.add(app)
        session.commit()
        session.refresh(app)
    return app


def get_applications_db(family_id: int) -> list[CApplication]:
    if not family_id:
        statement = select(CApplication)
    else:
        statement = select(CApplication).where(CApplication.family_id == family_id)
    with Session(mdb_engine) as session:
        return session.exec(statement=statement).all()


def get_application_db_by_id(id: int) -> CApplication:
    if not id:
        return
    statement = select(CApplication).where(CApplication.id == id)
    with Session(mdb_engine) as session:
        return session.exec(statement=statement).one_or_none()


def delete_application_by_id(id: int) -> int | None:
    statement = select(CApplication).where(CApplication.id == id)
    with Session(mdb_engine) as session:
        app = session.exec(statement=statement).one_or_none()
        if app == None:
            return
        session.delete(app)
        session.commit()
        return 1


def main() -> None:
    pass


if __name__ == "__main__":
    main()
