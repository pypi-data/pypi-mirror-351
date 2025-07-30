from fastapi import APIRouter, Depends, HTTPException, Request

import koco_product_sqlmodel.fastapi.routes.security as sec
import koco_product_sqlmodel.dbmodels.definition as sqlm
import koco_product_sqlmodel.mdb_connect.families as mdb_fam
import koco_product_sqlmodel.mdb_connect.mdb_connector as mdb_con
import koco_product_sqlmodel.mdb_connect.changelog as mdb_change

router = APIRouter(
    dependencies=[Depends(sec.get_current_active_user)],
    tags=["Endpoints to FAMILY-data"],
)
# router = APIRouter()


@router.get("/")
def get_families(product_group_id: int = None):
    """
    GET families from DB.
    Optional parameter:
    * *product_group_id* - when specified, only families from the selected product_groups are retrieved
    """
    fams = mdb_fam.get_families_db(product_group_id=product_group_id)
    fams_get = []
    for fam in fams:
        fam_dump = fam.model_dump()
        fam_get = sqlm.CFamilyGet(**fam_dump)
        fams_get.append(fam_get)
    return fams_get


@router.get("/{id}/")
def get_family_by_id(id):
    pg_fam = mdb_fam.get_family_db_by_id(id=id)
    if pg_fam == None:
        raise HTTPException(status_code=404, detail="Family not found")
    return sqlm.CFamilyGet(**pg_fam.model_dump())


@router.post("/", dependencies=[Depends(sec.has_post_rights)])
async def create_family(fam: sqlm.CFamilyPost, request: Request) -> sqlm.CFamilyGet:
    fam.user_id = await sec.get_user_id_from_request(request=request)
    new_fam = mdb_fam.create_family_DB(family=sqlm.CFamily(**fam.model_dump()))
    return await get_and_log_updated_model(request=request, updated_object=new_fam)


@router.patch(
    "/{id}/",
    dependencies=[
        Depends(sec.has_post_rights),
    ],
)
async def update_family(
    id: int, fam: sqlm.CFamilyPost, request: Request
) -> sqlm.CFamilyGet:
    fam.user_id = await sec.get_user_id_from_request(request=request)
    updated_family = mdb_fam.update_family_DB(id=id, fam_post=fam)
    if updated_family == None:
        raise HTTPException(status_code=404, detail="Family not found")
    return await get_and_log_updated_model(
        request=request, updated_object=updated_family
    )


async def get_and_log_updated_model(
    request: Request, updated_object: sqlm.CFamily
) -> sqlm.CFamily:
    user_id = await sec.get_user_id_from_request(request=request)
    entity_type = "cfamily"
    result = sqlm.CFamily(**updated_object.model_dump())
    mdb_change.log_results_to_db(
        entity_id=result.id,
        entity_type=entity_type,
        action=request.method,
        user_id=user_id,
        new_values=str(result.model_dump_json(exclude=("insdate", "upddate"))),
    )
    return result


@router.delete("/{id}/", dependencies=[Depends(sec.has_post_rights)])
async def delete_family_by_id(
    id: int, delete_recursive: bool = True, request: Request = None
) -> dict[str, bool]:
    """
    Delete a family item by cfamily.id.

    * Request parameter: *delete_recursive* = true

    If set to *true* all subitems contained in given family will be removed from database to avoid orphaned data
    """
    user_id = await sec.get_user_id_from_request(request=request)
    mdb_con.delete_family_by_id(
        log_func=mdb_change.log_results_to_db, family_id=id, delete_connected_items=delete_recursive, user_id=user_id
    )
    return {"ok": True}


def main():
    pass


if __name__ == "__main__":
    main()
