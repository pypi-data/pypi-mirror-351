from fastapi import APIRouter, Depends, HTTPException, Request

import koco_product_sqlmodel.fastapi.routes.security as sec
import koco_product_sqlmodel.dbmodels.definition as sqlm
import koco_product_sqlmodel.mdb_connect.catalogs as mdb_cat
import koco_product_sqlmodel.mdb_connect.mdb_connector as mdb_con
import koco_product_sqlmodel.mdb_connect.changelog as mdb_change

router = APIRouter(
    dependencies=[Depends(sec.get_current_active_user)],
    tags=["Endpoints to CATALOG-data"],
)


@router.get("/")
def get_catalogs() -> list[mdb_cat.CCatalogGet]:
    catalogs = mdb_cat.collect_catalogs_db_items()
    cats_get = []
    for cat in catalogs:
        cats_get.append(
            sqlm.CCatalogGet(
                id=cat.id,
                supplier=cat.supplier,
                year=cat.year,
                user_id=cat.user_id,
                insdate=cat.insdate,
                upddate=cat.upddate,
            )
        )
    return cats_get


@router.get("/{id}/")
def get_catalog_by_id(id) -> mdb_cat.CCatalogGet:
    catalog = mdb_cat.collect_catalog_by_id(id)
    return catalog


@router.post("/", dependencies=[Depends(sec.has_post_rights)])
async def create_catalog(
    catalog: sqlm.CCatalogPost, request: Request
) -> mdb_cat.CCatalogGet:
    user_id = await sec.get_user_id_from_request(request=request)
    new_catalog = mdb_cat.create_catalog(
        mdb_cat.CCatalog(
            supplier=catalog.supplier,
            year=catalog.year,
            status=catalog.status,
            user_id=user_id,
        )
    )
    return await get_and_log_updated_model(request=request, updated_object=new_catalog)


@router.patch(
    "/{id}/",
    dependencies=[
        Depends(sec.has_post_rights),
    ],
)
async def update_catalog(
    id: int, catalog: sqlm.CCatalogPost, request: Request
) -> mdb_cat.CCatalogGet:
    catalog.user_id = await sec.get_user_id_from_request(request=request)
    updated_catalog = mdb_cat.update_catalog(id=id, catalog=catalog)
    if updated_catalog == None:
        raise HTTPException(status_code=404, detail="Catalog not found")
    return await get_and_log_updated_model(
        request=request, updated_object=updated_catalog
    )


async def get_and_log_updated_model(
    request: Request, updated_object: sqlm.CCatalog
) -> sqlm.CCatalog:
    user_id = await sec.get_user_id_from_request(request=request)
    entity_type = "ccatalog"
    result = sqlm.CCatalogGet(**updated_object.model_dump())
    mdb_change.log_results_to_db(
        entity_id=result.id,
        entity_type=entity_type,
        action=request.method,
        user_id=user_id,
        new_values=str(result.model_dump_json(exclude=("insdate", "upddate"))),
    )
    return result


@router.delete("/{id}/", dependencies=[Depends(sec.has_post_rights)])
async def delete_catalog_by_id(
    id: int, delete_recursive: bool = True, request: Request = None
) -> dict[str, bool]:
    """
    Delete a catalog item by ccatalog.id.

    * Request parameter: *delete_recursive* = true

    If set to *true* all subitems contained in given catalog will be removed from database to avoid orphaned data
    """
    user_id = await sec.get_user_id_from_request(request=request)
    mdb_con.delete_catalog_by_id(
        log_func=mdb_change.log_results_to_db,
        catalog_id=id,
        delete_connected_items=delete_recursive,
        user_id=user_id,
    )
    return {"ok": True}


def main():
    pass


if __name__ == "__main__":
    main()
