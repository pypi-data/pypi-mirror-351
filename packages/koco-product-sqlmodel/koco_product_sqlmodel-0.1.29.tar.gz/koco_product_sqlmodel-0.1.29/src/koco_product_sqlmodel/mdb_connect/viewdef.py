import sqlmodel as sqlm
import koco_product_sqlmodel.mdb_connect.init_db_con as mdb_init
import koco_product_sqlmodel.dbmodels.viewdef as vd
import koco_product_sqlmodel.dbmodels.support as supp


def type_str_to_type(type_str: str):
    ts = type_str.lower()
    if ts == "int":
        return int
    if ts == "str":
        return str
    if ts == "float":
        return float
    if ts == "bool":
        return bool
    return str


def collect_select_values(vdcol_id: int, type_str: str):
    """Collect select_values for viewdef"""
    values = []
    with sqlm.Session(mdb_init.mdb_engine) as session:
        statement = (
            sqlm.select(vd.TViewDefSelectValue)
            .where(vd.TViewDefSelectValue.columnid == vdcol_id)
            .order_by(vd.TViewDefSelectValue.pos)
        )
        results = session.exec(statement).all()
    for res in results:
        if type_str.lower() == "str":
            values.append(res.value)
        elif type_str.lower() == "int":
            values.append(int(res.value))
        elif type_str.lower() == "float":
            values.append(float(res.value))
        elif type_str.lower() == "bool":
            if res.value.lower() == "true":
                values.append(True)
            else:
                values.append(False)
    return values


def collect_viewdef(db_obj_type: sqlm.SQLModel) -> dict:
    """collect a viewdef from the database tables"""
    viewdef = {}
    tablename = supp.get_table_from_sqlmodels(db_obj_type)
    with sqlm.Session(mdb_init.mdb_engine) as session:
        statement = (
            sqlm.select(vd.TViewdefColumn)
            .join(vd.TViewdefTable, vd.TViewdefTable.tablename == tablename)
            .where(vd.TViewdefColumn.tableid == vd.TViewdefTable.id)
            .order_by(vd.TViewdefColumn.pos)
        )
        vdcs = session.exec(statement).all()
    if not vdcs:
        return viewdef
    for vdc in vdcs:
        viewdef[vdc.columnname] = {
            "pos": vdc.pos,
            "is_textarea": vdc.istextarea,
            "is_editable": vdc.iseditable,
            "is_translated": vdc.istranslated,
            "is_select": vdc.isselect,
            "type": vdc.type,
        }
        if vdc.isselect:
            viewdef[vdc.columnname]["is_select"] = vdc.isselect
            viewdef[vdc.columnname]["select_values"] = collect_select_values(
                vdc.id, vdc.type
            )

    return viewdef


def Main():
    pass


if __name__ == "__main__":
    Main()
