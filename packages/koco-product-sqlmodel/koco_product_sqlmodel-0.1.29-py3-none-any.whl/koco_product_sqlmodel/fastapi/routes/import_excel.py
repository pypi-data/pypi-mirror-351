from fastapi import APIRouter, Depends, Request, File, UploadFile
import koco_product_sqlmodel.fastapi.routes.security as sec
import koco_product_sqlmodel.dbmodels.definition as sqlm
import koco_product_sqlmodel.dbmodels.models_enums as sql_enum
import koco_product_sqlmodel.mdb_connect.import_excel as mdb_imp_xlxs

router = APIRouter(
    dependencies=[Depends(sec.get_current_active_user)],
    tags=["Endpoints to IMPORT-functionality"],
)

@router.post("/excel/spectable", dependencies=[Depends(sec.has_post_rights)])
async def import_excel_spectable(
    entity_id: int,
    entity_type: str,
    spectable_name: str,
    spectable_type: sql_enum.SpectableTypeEnum,
    file: UploadFile=File(...),
    request: Request=None
    ) -> sqlm.CSpecTable:
    """
    Post excel file for import as cspectable + items.

    Arguments: 
    * **entity_id**: id of entity the file is uploaded for
    * **entity_type**: type of entity the file is uploaded for (eg., cfamily, cproductgroup, ...)
    * **spectable_name**: name of spectable
    * **spectable_type**: type of spectable (overview, singlecol, multicol)

    Returns: A CSpectable-object that was created from the import file.
    """
    user_id = await sec.get_user_id_from_request(request=request)
    # try:
    new_spectable=mdb_imp_xlxs.import_spectable_from_excel(
        file_content=file.file,
        entity_id=entity_id,
        entity_type=entity_type,
        spectable_name=spectable_name,
        spectable_type=spectable_type,
        user_id=user_id
        )
    # except Exception:
    #     raise HTTPException(status_code=500, detail='Something went wrong')
    # finally:
    file.file.close()
    return new_spectable
    
def main():
    pass


if __name__ == "__main__":
    main()
