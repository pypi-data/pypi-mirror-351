from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
import koco_product_sqlmodel.fastapi.routes.security as r_sec
from typing import Any

import datetime as dt
import os

router = APIRouter(tags=["Endpoints to DATABASE OPERATION data and methods"])


@router.get(
    "/backup",
    dependencies=[Depends(r_sec.has_post_rights)],
)
def backup_db(
    background_tasks: BackgroundTasks, filename: str = None
) -> dict[str, Any]:
    """
    Create a backup of the database on the server as zipped sql-file with timestamp as filename (default). Folder to be defined in
    OS-Environment-Variable **DB_BACKUP_FOLDER_URL**.
    *ARGS*
    **filename**: if provided the dump is saved with specified filename
    """
    if filename == None:
        filename = dt.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.zip")
    background_tasks.add_task(dump_db, filename)
    return {"file": filename}


def dump_db(filename: str):
    dpath = os.environ["DB_BACKUP_FOLDER_URL"]
    if not os.path.exists(path=dpath):
        raise HTTPException(
            status_code=500, detail=f"Folder {dpath} for DB-dump not found."
        )
    create_dump_command(fpath=dpath, filename=filename)
    os.system(command=create_dump_command(fpath=dpath, filename=filename))


def create_dump_command(fpath: str, filename: str) -> str:
    fname = os.path.join(fpath, filename)
    rstr = "mysqldump "
    rstr += f"-u'{os.environ['MARIADB_USER']}' "
    rstr += f"-p'{os.environ['MARIADB_PW']}' "
    rstr += f"{os.environ['MARIADB_DATABASE']}|"
    rstr += f"zip > {fname}"
    print(rstr)
    return rstr


def main():
    pass


if __name__ == "__main__":
    main()
