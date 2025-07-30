from fastapi import APIRouter, HTTPException, Depends
import koco_product_sqlmodel.dbmodels.definition as sql_def
import koco_product_sqlmodel.mdb_connect.select as mdb_select
import koco_product_sqlmodel.fastapi.routes.security as sec

router = APIRouter(
    tags=["Endpoints to generic object search methods"],
    dependencies=[
        Depends(sec.get_current_active_user),
    ],
)


def get_product_group_by_field_like(
    search_field: str,
    search_string: str,
    catalog_id: int | None,
    order_by_field: str | None = None,
    revert_order: bool = False,
) -> list[sql_def.CProductGroup]:
    if search_field not in sql_def.CProductGroupGet().__dict__.keys():
        raise HTTPException(status_code=404, detail="search_field not in cproductgroup")
    if order_by_field == None:
        order_by_field = search_field
    else:
        if order_by_field not in sql_def.CProductGroupGet().__dict__.keys():
            raise HTTPException(
                status_code=404, detail="order_by_field not in cproductgroup"
            )
    if catalog_id == None:
        res = mdb_select.select_objects_generic(
            object_type=sql_def.CProductGroup,
            where_str=f"cproductgroup.{search_field} like '%{search_string}%'",
            return_search_str=False,
        )
    else:
        res = mdb_select.select_objects_generic(
            object_type=sql_def.CProductGroup,
            where_str=f"cproductgroup.{search_field} like '%{search_string}%' and cproductgroup.catalog_id={catalog_id}",
            return_search_str=False,
        )
    s_res = sorted(
        res, key=lambda x: x.__getattribute__(order_by_field), reverse=revert_order
    )
    return s_res


@router.get("/product_group/")
def get_product_group_where_search_field_like(
    search_field: str,
    search_string: str,
    order_by_field: str = None,
    revert_order: bool = False,
    limit: int | None = None,
    skip: int | None = None,
    catalog_id: int | None = None,
) -> list[sql_def.CProductGroupGet]:
    """
    Search for strings in fields of the cproductgroup-table.
    ## Parameter:
    * *search_field*: name of the table-column to be searched in
    * *search_string*: string-value that should be used for the search. The search is a SQL-search using ```like```.
    * *order_by_field*: search is sorted by content of order_by_field field. If empty the *search_field* is used for ordering.
    * *revert_order*: search is sorted by content of search field. If *revert_order* is set to **true** the search order is reverted
    * *skip, limit*: typical skip and limit parameter for pagination. To be used the with rout ```/product_group/count/{search_field}``` to get the full number of relevant entries.
    * *catalog_id*: limit the search to product groups within a catalog with catalog.id==catalog_id.
    """
    res = get_product_group_by_field_like(
        search_field=search_field,
        search_string=search_string,
        catalog_id=catalog_id,
        order_by_field=order_by_field,
        revert_order=revert_order,
    )
    if res == None:
        return
    pgs = []
    limit, skip = check_limit_skip_vals(
        limit=limit, skip=skip, number_of_results=len(res)
    )
    for item in res[skip : skip + limit]:
        pgs.append(sql_def.CProductGroupGet(**item.model_dump()))
    return pgs


@router.get("/product_group/count/", response_description='{"count": 0}')
def get_product_group_count_where_search_field_like(
    search_field: str, search_string: str, catalog_id: int | None = None
) -> dict[str, int]:
    """
    Get count of hits for a search for strings in fields of the cproductgroup-table.
    ## Parameter:
    * *search_field*: name of the table-column to be searched in
    * *search_string*: string-value that should be used for the search. The search is a SQL-search using ```like```.
    * *catalog_id*: limit the search to product groups within a catalog with catalog.id==catalog_id.
    """
    res = get_product_group_by_field_like(
        search_field=search_field, search_string=search_string, catalog_id=catalog_id
    )
    if res == None:
        return {"count": 0}
    return {"count": len(res)}


def get_family_by_field_like(
    search_field: str,
    search_string: str,
    productgroup_id: int | None,
    order_by_field: str | None = None,
    revert_order: bool = False,
) -> list[sql_def.CFamily]:
    if search_field not in sql_def.CFamilyGet().__dict__.keys():
        raise HTTPException(status_code=404, detail="search_field not in cfamily")
    if order_by_field == None:
        order_by_field = search_field
    else:
        if order_by_field not in sql_def.CFamilyGet().__dict__.keys():
            raise HTTPException(status_code=404, detail="order_by_fiels not in cfamily")
    if productgroup_id == None:
        res = mdb_select.select_objects_generic(
            object_type=sql_def.CFamily,
            where_str=f"cfamily.{search_field} like '%{search_string}%'",
            return_search_str=False,
        )
    else:
        res = mdb_select.select_objects_generic(
            object_type=sql_def.CFamily,
            where_str=f"cfamily.{search_field} like '%{search_string}%' and cfamily.product_group_id={productgroup_id}",
            return_search_str=False,
        )
    s_res = sorted(
        res, key=lambda x: x.__getattribute__(order_by_field), reverse=revert_order
    )
    return s_res


@router.get("/family/")
def get_family_where_search_field_like(
    search_field: str,
    search_string: str,
    order_by_field: str | None = None,
    revert_order: bool = False,
    limit: int | None = None,
    skip: int | None = None,
    productgroup_id: int | None = None,
) -> list[sql_def.CFamilyGet]:
    """
    Search for strings in fields of the cfamily-table.
    ## Parameter:
    * *search_field*: name of the table-column to be searched in
    * *search_string*: string-value that should be used for the search. The search is a SQL-search using ```like```.
    * *order_by_field*: search is sorted by content of order_by_field field. If empty the *search_field* is used for ordering.
    * *revert_order*: search is sorted by content of search field. If *revert_order* is set to **true** the search order is reverted
    * *skip, limit*: typical skip and limit parameter for pagination. To be used the with rout ```/family/count/{search_field}``` to get the full number of relevant entries.
    * *productgroup_id*: limit the search to families within a product group with family.product_group_id==productgroup_id.
    """
    res = get_family_by_field_like(
        search_field=search_field,
        search_string=search_string,
        productgroup_id=productgroup_id,
        order_by_field=order_by_field,
        revert_order=revert_order,
    )
    if res == None:
        return
    pgs = []
    limit, skip = check_limit_skip_vals(
        limit=limit, skip=skip, number_of_results=len(res)
    )
    for item in res[skip : skip + limit]:
        pgs.append(sql_def.CFamilyGet(**item.model_dump()))
    return pgs


@router.get("/family/count/", response_description='{"count": 0}')
def get_family_count_where_search_field_like(
    search_field: str, search_string: str, productgroup_id: int | None = None
) -> dict[str, int]:
    """
    Get count of hits for a search for strings in fields of the cfamily-table.
    ## Parameter:
    * *search_field*: name of the table-column to be searched in
    * *search_string*: string-value that should be used for the search. The search is a SQL-search using ```like```.
    * *productgroup_id*: limit the search to families within a product group with family.product_group_id==productgroup_id.
    """
    res = get_family_by_field_like(
        search_field=search_field,
        search_string=search_string,
        productgroup_id=productgroup_id,
    )
    if res == None:
        return {"count": 0}
    return {"count": len(res)}


def get_article_by_field_like(
    search_field: str,
    search_string: str,
    family_id: int | None = None,
    order_by_field: str | None = None,
    revert_order: bool = False,
) -> list[sql_def.CArticle]:
    if search_field not in sql_def.CArticleGet().__dict__.keys():
        raise HTTPException(status_code=404, detail="search_field not in carticle")
    if order_by_field == None:
        order_by_field = search_field
    else:
        if order_by_field not in sql_def.CArticleGet().__dict__.keys():
            raise HTTPException(status_code=404, detail="order_by_file not in carticle")
    if family_id == None:
        res = mdb_select.select_objects_generic(
            object_type=sql_def.CArticle,
            where_str=f"carticle.{search_field} like '%{search_string}%'",
            return_search_str=False,
        )
    else:
        res = mdb_select.select_objects_generic(
            object_type=sql_def.CArticle,
            where_str=f"carticle.{search_field} like '%{search_string}%' and carticle.family_id={family_id}",
            return_search_str=False,
        )
    s_res = sorted(
        res, key=lambda x: x.__getattribute__(order_by_field), reverse=revert_order
    )
    return s_res


@router.get("/article/")
def get_article_where_search_field_like(
    search_field: str,
    search_string: str,
    order_by_field: str | None = None,
    revert_order: bool = False,
    limit: int | None = None,
    skip: int | None = None,
    family_id: int | None = None,
) -> list[sql_def.CArticleGet]:
    """
    Search for strings in fields of the carticle-table.
    ## Parameter:
    * *search_field*: name of the table-column to be searched in
    * *search_string*: string-value that should be used for the search. The search is a SQL-search using ```like```.
    * *order_by_field*: search is sorted by content of order_by_field field. If empty the *search_field* is used for ordering.
    * *revert_order*: search is sorted by content of search field. If *revert_order* is set to **true** the search order is reverted
    * *skip, limit*: typical skip and limit parameter for pagination. To be used the with rout ```/article/count/{search_field}``` to get the full number of relevant entries.
    * *family_id*: limit the search to families within a product group with article.family_id==family_id.
    """
    res = get_article_by_field_like(
        search_field=search_field,
        search_string=search_string,
        family_id=family_id,
        order_by_field=order_by_field,
        revert_order=revert_order,
    )
    if res == None:
        return
    arts = []
    limit, skip = check_limit_skip_vals(
        limit=limit, skip=skip, number_of_results=len(res)
    )
    for item in res[skip : skip + limit]:
        arts.append(sql_def.CArticleGet(**item.model_dump()))
    return arts


@router.get("/article/count/", response_description='{"count": 0}')
def get_article_count_where_search_field_like(
    search_field: str, search_string: str, family_id: int | None = None
) -> dict[str, int]:
    """
    Get count if hits for a search for strings in fields of the carticle-table.
    ## Parameter:
    * *search_field*: name of the table-column to be searched in
    * *search_string*: string-value that should be used for the search. The search is a SQL-search using ```like```.
    * *productgroup_id*: limit the search to families within a product group with article.family_id==family_id.
    """
    res = get_article_by_field_like(
        search_field=search_field, search_string=search_string, family_id=family_id
    )
    if res == None:
        return {"count": 0}
    return {"count": len(res)}


def check_limit_skip_vals(
    limit: int | None, skip: int | None, number_of_results: int
) -> tuple[int, int]:
    if limit == None or limit > number_of_results:
        return (number_of_results, 0)
    if skip == None:
        return (limit, 0)
    return (limit, skip)


def main():
    pass


if __name__ == "__main__":
    main()
