from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile
from fastapi.responses import FileResponse

import koco_product_sqlmodel.fastapi.routes.security as sec
import koco_product_sqlmodel.dbmodels.definition as sqlm
import koco_product_sqlmodel.dbmodels.models_enums as sql_enum
import koco_product_sqlmodel.mdb_connect.filedata as mdb_file
import koco_product_sqlmodel.mdb_connect.generic_object_connect as mdb_gen
import koco_product_sqlmodel.mdb_connect.changelog as mdb_change
import os
import hashlib
import json

router = APIRouter(
    dependencies=[Depends(sec.get_current_active_user)],
    tags=["Endpoints to FILE-data"],
)


@router.get("/")
def get_files(
    entity_id: int = None, entity_type: str = None
) -> list[sqlm.CFileDataGet]:
    files: list[sqlm.CFileData] = mdb_file.get_files_db(
        entity_id=entity_id, entity_type=entity_type
    )
    files_get = []
    for f in files:
        files_get.append(sqlm.CFileDataGet(**f.model_dump()))
    return files_get


@router.get("/{id}/")
def get_file_by_id(id) -> sqlm.CFileDataGet:
    file = mdb_file.get_file_db_by_id(id)
    if file != None:
        return sqlm.CFileDataGet(**file.model_dump())
    return None


@router.post("/", dependencies=[Depends(sec.has_post_rights)])
async def create_filedata(
    filedata: sqlm.CFileDataPost, request: Request
) -> sqlm.CFileDataGet:
    """
    Post filedata.
    """
    filedata.user_id = await sec.get_user_id_from_request(request=request)
    new_filedata = mdb_file.create_filedata(sqlm.CFileData(**filedata.model_dump()))
    return await get_and_log_updated_model(request=request, updated_object=new_filedata)


@router.patch(
    "/{id}/",
    dependencies=[
        Depends(sec.has_post_rights),
    ],
)
async def update_filedata(
    id: int, filedata: sqlm.CFileDataPost, request: Request
) -> sqlm.CFileDataGet:
    filedata.user_id = await sec.get_user_id_from_request(request=request)
    updated_filedata = mdb_file.update_filedata(id=id, filedata=filedata)
    if updated_filedata == None:
        raise HTTPException(status_code=404, detail="File data not found")
    return await get_and_log_updated_model(
        request=request, updated_object=updated_filedata
    )


async def get_and_log_updated_model(
    request: Request, updated_object: sqlm.CFileData
) -> sqlm.CFileData:
    user_id = await sec.get_user_id_from_request(request=request)
    entity_type = "cfiledata"
    result = sqlm.CFileDataGet(**updated_object.model_dump())
    mdb_change.log_results_to_db(
        entity_id=result.id,
        entity_type=entity_type,
        action=request.method,
        user_id=user_id,
        new_values=str(result.model_dump_json(exclude=("insdate", "upddate"))),
    )
    return result


@router.delete("/{id}/", dependencies=[Depends(sec.has_post_rights)])
async def delete_fildata_by_id(id: int, remove_file_from_server: bool=False, request: Request = None) -> dict[str, bool]:
    """
    Delete a filedata-object item by id
    
    Arguments:
    * **remove_file_from_server**: deletes the file in the product_file folder if selected. 
    CAVEAT: File might be used for several db-objects. Only delete if really no longer needed.

    """
    if remove_file_from_server:
        obj:sqlm.CFileData = mdb_gen.get_object(db_obj_type=sqlm.CFileData, id=id)
        if obj == None:
            raise HTTPException(status_code=404, detail="Object not found")
        fname = os.path.join(os.environ.get('PRODUCT_FILE_FOLDER'), obj.blake2shash)
        os.remove(path=fname)
    res = mdb_gen.delete_object(db_obj_type=sqlm.CFileData, id=id)
    if res == None:
        raise HTTPException(status_code=404, detail="Object not found")
    user_id = await sec.get_user_id_from_request(request=request)
    mdb_change.log_results_to_db(
        entity_type="cfiledata",
        entity_id=id,
        action="DELETE",
        user_id=user_id,
        new_values=None,
    )
    return {"ok": True}

@router.get("/download/{hash_or_id}/")
async def download_product_file(hash_or_id: str, filename: str|None=None, get_unprocessed_file: bool=False) -> FileResponse:
    """
    Download file with given hash or id (generate a download-link). If the length of the string is shorter than a blake2s-hash, 
    *hash_or_id* is converted into an id (integer).
    Arguments: 
    * filename: if given: file will be downloaded with the given filename. When omitted file will be downloaded as is (hash, no extension)
    """
    if len(hash_or_id)!=64:
        try:
            filedata_id=int(hash_or_id)
        except:
            raise HTTPException(status_code=404, detail=f"Unable to generate filedata id from {hash_or_id}")
        filedata = mdb_file.get_file_db_by_id(id=filedata_id)
        if filedata == None:
            raise HTTPException(status_code=404, detail=f"Unable to find cfiledata with id {hash_or_id}")
    else:
        filedata = mdb_file.get_files_db_by_hash(hash=hash_or_id)
        if filedata==[]:
            raise HTTPException(status_code=404, detail=f"No cfiledata-entry with hash {hash_or_id} not found")
        filedata=filedata[0]
    try: 
        json_data = dict(json.loads(filedata.description_json))
    except:
        raise HTTPException(status_code=404, detail=f"filedata has no valid description_json information")
    if get_unprocessed_file or json_data.get('overlay')==None:
        hash=filedata.blake2shash
        path=os.environ.get('PRODUCT_FILE_FOLDER')
        fpath=os.path.join(path, hash)
        if os.path.exists(fpath) == False:
            raise HTTPException(status_code=404, detail=f"File with hash {hash} not found")
        if filename==None:
            filename=filedata.oldfilename
        return FileResponse(path=fpath, filename=filename)
    return mdb_file.process_filedata(filedata=filedata, json_data=json_data, filename=filename)

@router.post("/upload/", dependencies=[Depends(sec.has_post_rights)])
async def upload_product_file(
    documenttype: sql_enum.CDocumentType,
    entity_id: int,
    entity_type: str,
    mime_type: str,
    description_json: str=None,
    visibility: int=1,
    order_priority: int=100,
    file: UploadFile=File(...),
    request: Request=None
    ) -> sqlm.CFileDataGet:
    """
    Post file and add entry to cfiledata-table.

    Arguments: 
    * **documenttype**: type of document, eg. "photo"
    * **entity_id**: id of entity the file is uploaded for
    * **entity_type**: type of entity the file is uploaded for (eg., cfamily, cproductgroup, ...)
    * **mimetype**: mimetype of the uploaded file 
    * **description_json**: a valid json-string with more detailed description

    Returns: A CFileDataGet-object with newly added filedata-information.
    """
    user_id = await sec.get_user_id_from_request(request=request)
    try:
        _=json.loads(description_json)
    except:
        description_json='{"description": ""}'
    filedata = sqlm.CFileData(
        documenttype=documenttype,
        description_json=description_json,
        oldfilename=file.filename,
        user_id=user_id,
        entity_id=entity_id,
        entity_type=entity_type,
        mimetype=mime_type,
        visibility=visibility,
        order_priority=order_priority
    )
    pf_path=os.environ.get('PRODUCT_FILE_FOLDER')
    try:
        contents = file.file.read()
        blake2shash=hashlib.blake2s(contents).hexdigest()
        file.filename=os.path.join(pf_path,blake2shash)
        filedata.blake2shash=blake2shash
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        raise HTTPException(status_code=500, detail='Something went wrong')
    finally:
        file.file.close()
    new_filedata = mdb_file.create_filedata(sqlm.CFileData(**filedata.model_dump()))
    return await get_and_log_updated_model(request=request, updated_object=new_filedata)


@router.post("/exchange_image/{id}/", dependencies=[Depends(sec.has_post_rights)])
async def exchange_image_data(
    id: int,
    file: UploadFile=File(...),
    request: Request = None
    ) -> sqlm.CFileDataGet:
    """
    Upload image data for a given cfiledata-entry and update blake2shash and oldfilename.

    Arguments: 
    * **id**: id of entity the file is uploaded for

    Returns: A CFileDataGet-object with newly added filedata-information.
    """
    user_id = await sec.get_user_id_from_request(request=request)
    try:
        _=json.loads(description_json)
    except:
        description_json='{"description": ""}'
    filedata = mdb_file.get_file_db_by_id(id=id)
    pf_path=os.environ.get('PRODUCT_FILE_FOLDER')
    try:
        contents = file.file.read()
        filedata.oldfilename=file.filename
        blake2shash=hashlib.blake2s(contents).hexdigest()
        file.filename=os.path.join(pf_path,blake2shash)
        filedata.blake2shash=blake2shash
        filedata.user_id=user_id 
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        raise HTTPException(status_code=500, detail='Something went wrong')
    finally:
        file.file.close()
    new_filedata = mdb_file.update_filedata(id=id, filedata=sqlm.CFileDataPost(**filedata.model_dump()))
    return await get_and_log_updated_model(request=request, updated_object=new_filedata)

@router.get("/find_unused")
def find_unused()->list[str]:
    """
    Search for orphaned files not referenced by a cfiledata-entry
    """
    pf_path=os.environ.get('PRODUCT_FILE_FOLDER')
    all_files=os.walk(pf_path)
    b2s_hashes_fs=[]
    for f in all_files:
        if '.git' in f[0]:
            continue
        for ff in f[2]:
            if os.path.splitext(ff)[1]=='.sql':
                continue
            b2s_hashes_fs.append(ff)
    return mdb_file.check_for_unused_blake2shashes(in_list=b2s_hashes_fs)





def main():
    pass


if __name__ == "__main__":
    main()
