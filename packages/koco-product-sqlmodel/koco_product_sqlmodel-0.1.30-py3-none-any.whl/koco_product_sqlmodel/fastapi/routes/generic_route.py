from fastapi import APIRouter, Depends, HTTPException, Request
import koco_product_sqlmodel.mdb_connect.init_db_con as mdb_init
import koco_product_sqlmodel.fastapi.routes.security as sec
import koco_product_sqlmodel.dbmodels.definition as sqlm
import koco_product_sqlmodel.mdb_connect.generic_object_connect as mdb_gen
import koco_product_sqlmodel.mdb_connect.changelog as mdb_change
import koco_product_sqlmodel.dbmodels.support as dbm_support


class MyBaseRoute:
    def __init__(
        self,
        sqlmodel_db: sqlm.SQLModel,
        sqlmodel_get: sqlm.SQLModel,
        sqlmodel_post: sqlm.SQLModel,
        tags: list[str],
    ):
        self.router = APIRouter(
            dependencies=[Depends(sec.get_current_active_user)],
            tags=tags,
        )
        self.sqlmodel_db = sqlmodel_db
        self.sqlmodel_get = sqlmodel_get
        self.sqlmodel_post = sqlmodel_post
        self.router.add_api_route(
            path="/",
            endpoint=self.get_objects,
            methods=["GET"],
            response_model=list[self.sqlmodel_get],
        )
        self.router.add_api_route(
            path="/{id}/",
            endpoint=self.get_object,
            methods=["GET"],
            response_model=self.sqlmodel_get,
        )
        self.router.add_api_route(
            path="/",
            endpoint=self.post_object,
            methods=["POST"],
            dependencies=[Depends(sec.has_post_rights)],
            response_model=self.sqlmodel_get,
        )
        self.router.add_api_route(
            path="/{id}/",
            endpoint=self.patch_object,
            methods=["PATCH"],
            dependencies=[Depends(sec.has_post_rights)],
            response_model=self.sqlmodel_get,
        )
        self.router.add_api_route(
            path="/{id}/",
            endpoint=self.delete_object,
            methods=["DELETE"],
            dependencies=[Depends(sec.has_post_rights)],
        )

    def get_objects(self, family_id: int = None) -> list[sqlm.SQLModel]:
        """
        GET list of objects from DB.
        Optional parameter:
        * *family_id* - when specified, only objects from the selected family are retrieved
        """
        objects = mdb_gen.get_family_related_objects(
            db_obj_type=self.sqlmodel_db, family_id=family_id
        )
        objects_get: list[sqlm.SQLModel] = []
        for object in objects:
            objects_get.append(self.sqlmodel_get(**object.model_dump()))
        return objects_get

    def get_object(self, id) -> sqlm.SQLModel:
        object = mdb_gen.get_object(db_obj_type=self.sqlmodel_db, id=id)
        if object == None:
            raise HTTPException(status_code=404, detail="Object not found")
        return self.sqlmodel_get(**object.model_dump())

    def post_object(self, object: sqlm.SQLModel) -> sqlm.SQLModel:
        new_obj = mdb_gen.post_object(db_obj=self.sqlmodel_db(**object.model_dump()))
        return self.sqlmodel_get(**new_obj.model_dump())

    def patch_object(self, id: int, obj: sqlm.SQLModel) -> sqlm.SQLModel:
        updated_object = mdb_gen.patch_object(
            id=id, db_obj=obj, db_obj_type=self.sqlmodel_db
        )
        if updated_object == None:
            raise HTTPException(status_code=404, detail="Object not found")
        return self.sqlmodel_get(**updated_object.model_dump())

    async def delete_object(self, id: int, request: Request) -> dict[str, bool]:
        """
        Delete an object item by cobject.id.
        """
        res = mdb_gen.delete_object(db_obj_type=self.sqlmodel_db, id=id)
        if res == None:
            raise HTTPException(status_code=404, detail="Object not found")
        entity_type = dbm_support.get_entity_type_from_sqlmodel_object(object=res)
        user_id = await sec.get_user_id_from_request(request=request)
        mdb_change.log_results_to_db(
            entity_type=entity_type,
            entity_id=id,
            action="DELETE",
            user_id=user_id,
            new_values=None,
        )
        return {"ok": True}

    async def get_and_log_updated_model(
        self, request: Request, updated_object: sqlm.SQLModel
    ) -> sqlm.SQLModel:
        user_id = await sec.get_user_id_from_request(request=request)
        entity_type = dbm_support.get_entity_type_from_sqlmodel_object(
            object=updated_object
        )
        result: sqlm.SQLModel = self.sqlmodel_get(**updated_object.model_dump())
        mdb_change.log_results_to_db(
            entity_id=result.id,
            entity_type=entity_type,
            action=request.method,
            user_id=user_id,
            new_values=str(result.model_dump_json(exclude=("insdate", "upddate"))),
        )
        return result


class ParentRoute(MyBaseRoute):
    def __init__(
        self,
        sqlmodel_db: sqlm.SQLModel,
        sqlmodel_get: sqlm.SQLModel,
        sqlmodel_post: sqlm.SQLModel,
        tags: list[str],
    ):
        super().__init__(
            sqlmodel_db=sqlmodel_db,
            sqlmodel_get=sqlmodel_get,
            sqlmodel_post=sqlmodel_post,
            tags=tags,
        )

    def get_objects(
        self, parent_id: int | None = None, parent: str | None = None
    ) -> list[sqlm.SQLModel]:
        """
        GET list of objects from DB.
        Parameter:
        * *parent_id* - id of parent object
        * *parent* - parent object type
        """
        objects = mdb_gen.get_objects_from_parent(
            db_obj_type=self.sqlmodel_db, parent_id=parent_id, parent=parent
        )
        objects_get: list[any] = []
        for object in objects:
            objects_get.append(self.sqlmodel_get(**object.model_dump()))
        return objects_get


def main():
    pass


if __name__ == "__main__":
    main()
