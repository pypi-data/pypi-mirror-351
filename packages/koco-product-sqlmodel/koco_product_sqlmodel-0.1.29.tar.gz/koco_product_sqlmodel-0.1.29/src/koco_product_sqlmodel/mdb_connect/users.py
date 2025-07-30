import sqlmodel as sql
import koco_product_sqlmodel.dbmodels.definition as sqlm
import koco_product_sqlmodel.mdb_connect.init_db_con as dbcon


def get_user_by_name(name_str: str) -> sqlm.CUser | None:
    with sql.Session(dbcon.mdb_engine) as session:
        statement = sql.select(sqlm.CUser).where(sqlm.CUser.name == name_str)
        return session.exec(statement=statement).one_or_none()


def main():
    pass


if __name__ == "__main__":
    main()
