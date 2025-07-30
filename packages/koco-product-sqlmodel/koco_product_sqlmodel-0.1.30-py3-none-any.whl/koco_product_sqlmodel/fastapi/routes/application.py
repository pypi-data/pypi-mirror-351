from fastapi import HTTPException, Request

import koco_product_sqlmodel.fastapi.routes.security as rsec
import koco_product_sqlmodel.dbmodels.definition as sqlm
import koco_product_sqlmodel.mdb_connect.generic_object_connect as mdb_gen
import koco_product_sqlmodel.fastapi.routes.generic_route as rgen
import koco_product_sqlmodel.mdb_connect.changelog as mdb_change


class ApplicationRoute(rgen.MyBaseRoute):
    def __init__(
        self,
        sqlmodel_db: sqlm.SQLModel,
        sqlmodel_post: sqlm.SQLModel,
        sqlmodel_get: sqlm.SQLModel,
        tags: list[str],
    ):
        super().__init__(
            sqlmodel_db=sqlmodel_db,
            sqlmodel_post=sqlmodel_post,
            sqlmodel_get=sqlmodel_get,
            tags=tags,
        )

    async def post_object(
        self, object: sqlm.CApplicationPost, request: Request
    ) -> sqlm.CApplicationGet:
        object.user_id = await rsec.get_user_id_from_request(request=request)
        new_obj = mdb_gen.post_object(db_obj=self.sqlmodel_db(**object.model_dump()))
        return await self.get_and_log_updated_model(
            request=request, updated_object=new_obj
        )

    async def patch_object(
        self, id: int, obj: sqlm.CApplicationPost, request: Request
    ) -> sqlm.CApplicationGet:
        obj.user_id = await rsec.get_user_id_from_request(request=request)
        updated_object = mdb_gen.patch_object(
            id=id, db_obj=obj, db_obj_type=self.sqlmodel_db
        )
        if updated_object == None:
            raise HTTPException(status_code=404, detail="Object not found")
        return await self.get_and_log_updated_model(
            request=request, updated_object=updated_object
        )


route_application = ApplicationRoute(
    sqlmodel_db=sqlm.CApplication,
    sqlmodel_get=sqlm.CApplicationGet,
    sqlmodel_post=sqlm.CApplicationPost,
    tags=["Endpoints to APPLICATION-data"],
)


def main():
    pass


if __name__ == "__main__":
    main()
