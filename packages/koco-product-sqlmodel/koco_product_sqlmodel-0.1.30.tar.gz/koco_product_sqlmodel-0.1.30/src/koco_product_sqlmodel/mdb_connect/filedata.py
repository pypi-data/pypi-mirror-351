from koco_product_sqlmodel.mdb_connect.init_db_con import mdb_engine
from sqlmodel import Session, select, text
from fastapi import HTTPException, Response
from fastapi.responses import StreamingResponse
from koco_product_sqlmodel.dbmodels.definition import (
    CFileData,
    CFileDataGet,
    CFileDataPost,
)
# import PIL as pil
from PIL import Image
import os
import io
import json
import copy

def process_filedata(filedata: CFileData, json_data: dict, filename: str=None)->Response:
    if "overlay" in json_data.keys():
        over_data = json_data.get("overlay")
        if type(over_data) != dict:
            over_data=dict(json.loads(json_data.get("overlay")))
        overlay_id=over_data.get("id")
        ofiledata = get_file_db_by_id(id=overlay_id)
        if ofiledata==None:
            raise HTTPException(status_code=404, detail=f"image data with id {overlay_id} for overlay not found")
        resImage = overlay_images(cf_background=filedata, cf_overlay=ofiledata, over_info = over_data)
    if filename==None:
        se = os.path.splitext(filedata.oldfilename)
        filename= se[0] + '_p' + '.png'
    s_response = StreamingResponse(resImage, media_type="image/png")
    s_response.headers["Content-Disposition"]=f"attachment; filename={filename}"
    return s_response


def overlay_images(cf_background: CFileData, cf_overlay: CFileData, over_info: dict)->io.BytesIO:
    image_background = Image.open(load_file_into_buffer(cf=cf_background), formats=None)
    image_overlay = Image.open(load_file_into_buffer(cf=cf_overlay), formats=None)
    size_factor=image_background.size[0]/image_overlay.size[0]*over_info.get("xs_percent")/100.0
    image_overlay=image_overlay.resize(size=(int(image_overlay.size[0]*size_factor), int(image_overlay.size[1]*size_factor)))
    xo=int(image_background.size[0]*over_info.get("xo_percent")/100.0)
    yo=int(image_background.size[1]*over_info.get("yo_percent")/100.0)
    image_background.paste(im=image_overlay, box=(xo,yo))
    rbytes=io.BytesIO()
    image_background.save(rbytes, format='PNG')
    # image_background.save("test.png")
    rbytes.seek(0)
    return rbytes



def load_file_into_buffer(cf: CFileData)->io.BytesIO:
    hash=cf.blake2shash
    path=os.environ.get('PRODUCT_FILE_FOLDER')
    fpath=os.path.join(path, hash)
    if os.path.exists(fpath) == False:
        raise HTTPException(status_code=404, detail=f"File with hash {hash} not found. cfiledata.id = {cf.id}")
    with open(file=fpath, mode="rb") as fh:
        return io.BytesIO(fh.read())

def create_filedata(filedata: CFileData):
    with Session(mdb_engine) as session:
        session.add(filedata)
        session.commit()
        statement = (
            select(CFileData)
            .where(
                CFileData.blake2shash == filedata.blake2shash
            )
            .where (
                CFileData.entity_id==filedata.entity_id
            )
            .where (
                CFileData.entity_type==filedata.entity_type
            )
        )
    return session.exec(statement=statement).one_or_none()


def update_filedata(id: int | None, filedata: CFileDataPost) -> CFileData | None:
    if id == None:
        return
    with Session(mdb_engine) as session:
        statement = select(CFileData).where(CFileData.id == id)
        fd = session.exec(statement=statement).one_or_none()
        if fd == None:
            return
        fd_data = filedata.model_dump(exclude_unset=True)
        fd = fd.sqlmodel_update(fd_data)
        session.add(fd)
        session.commit()
        session.refresh(fd)
    return fd


def get_files_db(entity_id: int, entity_type: str) -> list[CFileData] | None:
    if entity_id == None and entity_type == None:
        statement = select(CFileData)
    elif entity_id != None and entity_type == None:
        statement = select(CFileData).where(CFileData.entity_id == entity_id)
    elif entity_id == None and entity_type != None:
        statement = select(CFileData).where(CFileData.entity_type == entity_type)
    else:
        statement = (
            select(CFileData)
            .where(CFileData.entity_id == entity_id)
            .where(CFileData.entity_type == entity_type)
        )
    with Session(mdb_engine) as session:
        return session.exec(statement=statement).all()


def get_file_db_by_id(id: int) -> CFileData:
    if not id:
        return
    statement = select(CFileData).where(CFileData.id == id)
    with Session(mdb_engine) as session:
        return session.exec(statement=statement).one_or_none()

def get_files_db_by_hash(hash: str) -> CFileData:
    statement = select(CFileData).where(CFileData.blake2shash == hash)
    with Session(mdb_engine) as session:
        return session.exec(statement=statement).all()


# def delete_application_by_id(id: int) -> int | None:
#     statement = select(CApplication).where(CApplication.id == id)
#     with Session(mdb_engine) as session:
#         app = session.exec(statement=statement).one_or_none()
#         if app == None:
#             return
#         session.delete(app)
#         session.commit()
#         return 1

def check_for_unused_blake2shashes(in_list: list[str])->list[str]:
    statement = text('SELECT distinct blake2shash FROM cfiledata')
    with Session(mdb_engine) as session:
        db_b2s = session.exec(statement=statement).all()
    out_list=copy.deepcopy(in_list)
    for b2s in db_b2s:
        if b2s[0] in out_list:
            out_list.remove(b2s[0])
    return out_list


def main() -> None:
    pass


if __name__ == "__main__":
    main()
