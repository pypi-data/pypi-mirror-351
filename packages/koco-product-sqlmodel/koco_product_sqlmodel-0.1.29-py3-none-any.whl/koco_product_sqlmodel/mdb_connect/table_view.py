from sqlmodel import Session, select, text
import sqlmodel
from koco_product_sqlmodel.mdb_connect.init_db_con import mdb_engine
from koco_product_sqlmodel.dbmodels.support import get_table_from_sqlmodels
from koco_product_sqlmodel.mdb_connect.viewdef import collect_viewdef


def collect_table_data(table: sqlmodel = None, where_str: str = None):
    if table == None:
        return None
    if where_str:
        statement = select(table).where(text(where_str))
    else:
        statement = select(table)
    viewdef = collect_viewdef(table)
    with Session(mdb_engine) as session:
        results = session.exec(statement)
        td = {"heading": table.__qualname__}
        td["table_headers"] = [[key for key in viewdef]]
        # print(td)
        qd = []
        td["hrefs"] = []
        for r in results.all():
            line = []
            r_dict = r.dict()
            for th in td["table_headers"][0]:
                line.append(r_dict[th])
            qd.append(line)
        td["hrefs"] = ["" for th in td["table_headers"][0]]
        td["hrefs"][0] = f"/database/{get_table_from_sqlmodels(table)[1:]}/edit?id="
        td["query_data"] = qd
        td["breadcrumb"] = (
            ("/", "Home"),
            ("/database", "Database"),
            ("#", f'view {td["heading"]}'),
        )
    return td


def main() -> None:
    pass


if __name__ == "__main__":
    main()
