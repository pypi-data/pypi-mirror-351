from fastapi import APIRouter, Depends, HTTPException, Request

import koco_product_sqlmodel.fastapi.routes.security as sec
import koco_product_sqlmodel.dbmodels.definition as sqlm
import koco_product_sqlmodel.mdb_connect.product_groups as mdb_pg
import koco_product_sqlmodel.mdb_connect.mdb_connector as mdb_con
import koco_product_sqlmodel.mdb_connect.changelog as mdb_change

router = APIRouter(
    dependencies=[Depends(sec.get_current_active_user)],
    tags=["Endpoints to PRODUCT GROUP-data"],
)
# router = APIRouter()


@router.get("/")
def get_product_groups(
    catalog_id: int = None, supplier: str = None, year: int = None
) -> list[mdb_pg.CProductGroupGet]:
    """
    GET products groups from DB.
    Optional parameter:
    * *catalog_id* - when specified, only product_groups from the selected catalog are retrieved
    * *supplier*, *year* - when *catalog_id* is not specified, *supplier* and *year* can be specified to
    identify the catalog from which the product groups shall be selected.
    * *supplier* - when only *supplier* is specified, the latest catalog (highest *catalog_id*) will be used to filter the product groups
    """
    pgs, _ = mdb_pg.collect_product_groups(
        catalog_id=catalog_id, supplier=supplier, year=year
    )
    pgs_get = []
    for pg in pgs:
        pg_dump = pg.model_dump()
        pg_get = sqlm.CProductGroupGet(**pg_dump)
        pgs_get.append(pg_get)
    return pgs_get


@router.get("/{id}/")
def get_product_group_by_id(id) -> mdb_pg.CProductGroupGet:
    pg_db = mdb_pg.collect_product_group_by_id(id=id)
    if pg_db == None:
        raise HTTPException(status_code=404, detail="Product group not found")
    return sqlm.CProductGroupGet(**pg_db.model_dump())


@router.post("/", dependencies=[Depends(sec.has_post_rights)])
async def create_product_group(
    pg: sqlm.CProductGroupPost, request: Request
) -> mdb_pg.CProductGroupGet:
    pg.user_id = await sec.get_user_id_from_request(request=request)
    new_pg = mdb_pg.create_productgroup(
        product_group=sqlm.CProductGroup(**pg.model_dump())
    )
    return await get_and_log_updated_model(request=request, updated_object=new_pg)


@router.patch(
    "/{id}/",
    dependencies=[
        Depends(sec.has_post_rights),
    ],
)
async def update_product_group(
    id: int, pg: sqlm.CProductGroupPost, request: Request
) -> mdb_pg.CProductGroupGet:
    pg.user_id = await sec.get_user_id_from_request(request=request)
    updated_pg = mdb_pg.update_product_group(id=id, pg_post=pg)
    if updated_pg == None:
        raise HTTPException(status_code=404, detail="Product group not found")
    return await get_and_log_updated_model(request=request, updated_object=updated_pg)


async def get_and_log_updated_model(
    request: Request, updated_object: sqlm.CProductGroup
) -> sqlm.CProductGroup:
    user_id = await sec.get_user_id_from_request(request=request)
    entity_type = "cproductgroup"
    result = sqlm.CProductGroup(**updated_object.model_dump())
    mdb_change.log_results_to_db(
        entity_id=result.id,
        entity_type=entity_type,
        action=request.method,
        user_id=user_id,
        new_values=str(result.model_dump_json(exclude=("insdate", "upddate"))),
    )
    return result


@router.delete("/{id}/", dependencies=[Depends(sec.has_post_rights)])
async def delete_product_group_by_id(
    id: int, delete_recursive: bool = True, request: Request = None
) -> dict[str, bool]:
    """
    Delete a product group item by cproductgroup.id.

    * Request parameter: *delete_recursive* = true

    If set to *true* all subitems contained in given product group will be removed from database to avoid orphaned data
    """
    user_id = await sec.get_user_id_from_request(request=request)
    mdb_con.delete_product_group_by_id(
        product_group_id=id, delete_connected_items=delete_recursive, user_id=user_id
    )
    return {"ok": True}


def main():
    pass


if __name__ == "__main__":
    main()
