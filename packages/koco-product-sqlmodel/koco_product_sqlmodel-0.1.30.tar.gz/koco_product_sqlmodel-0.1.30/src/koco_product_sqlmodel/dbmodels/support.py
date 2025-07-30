import koco_product_sqlmodel.dbmodels.definition as adb
import koco_product_sqlmodel.dbmodels.viewdef as vd
import sqlmodel as sqlm


def get_entity_type_from_sqlmodel_object(object: sqlm.SQLModel):
    return object.__class__.__name__.lower()


def get_table_from_sqlmodels(model: sqlm.SQLModel) -> str:
    t_dict = {
        adb.CArticle: "carticle",
        adb.CCatalog: "ccatalog",
        adb.CProductGroup: "cproductgroup",
        adb.CFamily: "cfamily",
        adb.CApplication: "capplication",
        adb.COption: "coption",
        adb.CSpecTable: "cspectable",
        adb.CSpecTableItem: "cspectableitem",
        adb.CFileData: "cfiledata",
        adb.CUrl: "curl",
        adb.CBacklog: "cbacklog",
        adb.CCategoryTree: "ccategorytree",
        adb.CCategoryMapper: "ccategorymapper",
        adb.CUser: "cuser",
        adb.CUserRole: "cuserrole",
        vd.TViewdefTable: "tviewdeftable",
        vd.TViewdefColumn: "tviewdefcolumn",
        vd.TViewDefSelectValue: "tviewdefselectvalue",
        vd.TDictionary: "tdictionary",
        vd.TTranslationMapper: "ttranslationmapper",
    }
    if model in t_dict:
        return t_dict[model]
    return ""


def get_db_object_type(db_object_str: str) -> sqlm.SQLModel:
    str_dict = {
        "article": adb.CArticle,
        "catalog": adb.CCatalog,
        "productgroup": adb.CProductGroup,
        "family": adb.CFamily,
        "application": adb.CApplication,
        "option": adb.COption,
        "spectable": adb.CSpecTable,
        "spectableitem": adb.CSpecTableItem,
        "filedata": adb.CFileData,
        "url": adb.CUrl,
        "backlog": adb.CBacklog,
        "categorymapper": adb.CCategoryMapper,
        "categorytree": adb.CCategoryTree,
        "user": adb.CUser,
        "userrole": adb.CUserRole,
        "translationmapper": vd.TTranslationMapper,
        "dictionary": vd.TDictionary,
        "viewdeftable": vd.TViewdefTable,
        "viewdefcolumn": vd.TViewdefColumn,
        "viewdefselectvalue": vd.TViewDefSelectValue,
    }
    obj_str = db_object_str.lower()
    if obj_str in str_dict:
        return str_dict[obj_str]
    if obj_str[1:] in str_dict:
        return str_dict[obj_str[1:]]
    return None


def Main():
    pass


if __name__ == "__main__":
    Main()
