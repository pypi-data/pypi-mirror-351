from fastapi import Request, HTTPException, APIRouter, Depends, BackgroundTasks

import koco_product_sqlmodel.dbmodels.changelog as sqlc
import koco_product_sqlmodel.mdb_connect.changelog as mdb_change
import koco_product_sqlmodel.mdb_connect.generic_object_connect as mdb_gen
import koco_product_sqlmodel.fastapi.routes.security as rsec


class ChangelogRoute:
    def __init__(
        self,
        sqlmodel_db: sqlc.SQLModel,
        sqlmodel_post: sqlc.SQLModel,
        sqlmodel_get: sqlc.SQLModel,
        tags: list[str],
    ):
        self.router = APIRouter(
            dependencies=[Depends(rsec.get_current_active_user)],
            tags=tags,
        )
        self.sqlmodel_db = sqlmodel_db
        self.sqlmodel_post = sqlmodel_post
        self.sqlmodel_get = sqlmodel_get
        self.router.add_api_route(
            path="/",
            endpoint=self.get_objects,
            methods=["GET"],
            response_model=list[self.sqlmodel_get],
        )
        self.router.add_api_route(
            path="/count",
            endpoint=self.get_objects_count,
            methods=["GET"],
            response_model=dict[str, int],
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
            dependencies=[Depends(rsec.has_post_rights)],
            response_model=self.sqlmodel_get,
        )
        self.router.add_api_route(
            path="/{id}/",
            endpoint=self.delete_object,
            methods=["DELETE"],
            dependencies=[Depends(rsec.has_post_rights)],
        )
        self.router.add_api_route(
            path="/reset_changelog",
            methods=["GET"],
            endpoint=self.reset_changelog,
            dependencies=[Depends(rsec.has_post_rights)],
        )
        self.router.add_api_route(
            path="/init_changelog",
            methods=["GET"],
            endpoint=self.init_changelog,
            dependencies=[Depends(rsec.has_post_rights)],
        )

    def get_objects(
        self,
        entity_id: int | None = None,
        entity_type: str = None,
        parent_id: int | None = None,
        parent_type: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
        remove_last_change: bool = True,
    ) -> list[sqlc.CChangelogGet]:
        """
        GET list of changelog-objects from DB.
        Optional parameter:
        * *entity_id* - when specified a list of objects with provided entity_id will be provided
        * *entity_type* - when specified a list of objects with provided entity_type will be provided. Typically, *entity_id* and *entity_type* are used in combiniation. When *entity_id* and *entity_type* are provided the parameter *parent_id* and *parent_type* will be ignored
        * *parent_id*, *parent_type* - when both parameter are provided (and no *entity*-paramenter), all changes for child-nodes of the parent-entity are provided. Helpful for spectable-items or family-items
        * *skip*, *limit* - standard skip or limit values for pagination
        * *remove_last_change* - if set than the last change where the content is the same as in the object will be omitted. Default: true
        """
        return mdb_change.get_changes(
            entity_id=entity_id,
            entity_type=entity_type,
            parent_type=parent_type,
            parent_id=parent_id,
            skip=skip,
            limit=limit,
            remove_last_change=remove_last_change,
        )

    def get_objects_count(
        self,
        entity_id: int | None = None,
        entity_type: str = None,
        parent_id: int | None = None,
        parent_type: str | None = None,
        remove_last_change: bool = True,
    ) -> list[sqlc.CChangelogGet]:
        """
        Get count of changelog-objects from DB.
        Optional parameter:
        * *entity_id* - when specified the count of objects with provided entity_id will be provided
        * *entity_type* - when specified the count of objects with provided entity_type will be provided. Typically, *entity_id* and *entity_type* are used in combiniation. When *entity_id* and *entity_type* are provided the parameter *parent_id* and *parent_type* will be ignored
        * *parent_id*, *parent_type* - when both parameter are provided (and no *entity*-paramenter), the count of all changes for child-nodes of the parent-entity are provided. Helpful for spectable-items or family-items
        * *remove_last_change* - if set than the last change where the content is the same as in the object will be omitted. Default: true
        """
        return mdb_change.get_changes_count(
            entity_id=entity_id,
            entity_type=entity_type,
            parent_type=parent_type,
            parent_id=parent_id,
            remove_last_change=remove_last_change,
        )

    def get_object(self, id) -> sqlc.CChangelogGet:
        return mdb_change.get_change_by_id(id=id)

    async def post_object(
        self, object: sqlc.CChangelogPost, request: Request
    ) -> sqlc.SQLModel:
        object.user_id = await rsec.get_user_id_from_request(request=request)
        new_obj = mdb_gen.post_object(db_obj=self.sqlmodel_db(**object.model_dump()))
        return self.sqlmodel_get(**new_obj.model_dump())

    def delete_object(self, id: int) -> dict[str, bool]:
        """
        Delete an object item by cobject.id.
        """
        res = mdb_gen.delete_object(db_obj_type=self.sqlmodel_db, id=id)
        if res == None:
            raise HTTPException(status_code=404, detail="Object not found")
        return {"ok": True}

    def reset_changelog(self) -> dict[str, bool]:
        """
        Drop the changelog-table and create an empty new one
        """
        mdb_change.reset_changelog()
        return {"ok": True}

    async def init_changelog(
        self, request: Request, background_tasks: BackgroundTasks
    ) -> dict[str, bool]:
        """
        Init the changelog with actual product data of database. Use after reset of changelog.
        """
        user_id = await rsec.get_user_id_from_request(request=request)
        background_tasks.add_task(mdb_change.init_changelog, user_id=user_id)
        return {"ok": True}


route_changelog = ChangelogRoute(
    sqlmodel_db=sqlc.CChangelog,
    sqlmodel_get=sqlc.CChangelogGet,
    sqlmodel_post=sqlc.CChangelogPost,
    tags=["Endpoints to CHANGELOG-data"],
)


def main():
    pass


if __name__ == "__main__":
    main()
