from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
import koco_product_sqlmodel.fastapi.routes.catalog as rcat
import koco_product_sqlmodel.fastapi.routes.product_group as rpg
import koco_product_sqlmodel.fastapi.routes.family as rfam
import koco_product_sqlmodel.fastapi.routes.article as rart
import koco_product_sqlmodel.fastapi.routes.security as rsec
import koco_product_sqlmodel.fastapi.routes.application as rapp
import koco_product_sqlmodel.fastapi.routes.url as rurl
import koco_product_sqlmodel.fastapi.routes.spectable as rst
import koco_product_sqlmodel.fastapi.routes.search_object as rsearch
import koco_product_sqlmodel.fastapi.routes.changelog as rchangelog
import koco_product_sqlmodel.fastapi.routes.db_operations as rdb
import koco_product_sqlmodel.fastapi.routes.filedata as rfile
import koco_product_sqlmodel.fastapi.routes.import_excel as rxlsx

# import koco_product_sqlmodel.dbmodels.definition as mdef
import koco_product_sqlmodel.fastapi.routes.option as ropt
from fastapi.middleware.cors import CORSMiddleware


DESCRIPTION_STRING = """
API to KOCO MOTION Product database. Under heavy construction. 
"""

tags_metadata = [
    {
        "name": "Endpoints to CATALOG-data",
        "description": "Catalogs are collections of product groups of a distinct supplier.",
    },
    {
        "name": "Endpoints to PRODUCT GROUP-data",
        "description": "Product groups are collections of families of articles.",
    },
    {
        "name": "Endpoints to FAMILY-data",
        "description": "Families collect articles belonging to an article-family. They contain also additional information like description, or familiy spectables.",
    },
    {
        "name": "Endpoints to ARTICLE-data",
        "description": "Articles collect all specifications of an article as spectables. They contain also additional information like description, urls to spec-data...",
    },
    {
        "name": "Endpoints to APPLICATION-data",
        "description": "Applications are a collection of applications of a product family.",
    },
    {
        "name": "Endpoints to OPTION-data",
        "description": "Options collect the different options or features available with a product family.",
    },
    {
        "name": "Endpoints to URL-data",
        "description": "Urls point to additional data sources of parent objects (typically family or article) with a given *parent_id*.",
    },
    {
        "name": "Endpoints to SPECTABLEITEM-data",
        "description": "SpectableItems are members of a given spectable referenced by spec_table_id",
    },
    {
        "name": "Endpoints to SPECTABLE-data",
        "description": "Spectables collect spectableitems of parent objects (typically family or article) with a given *parent_id*.",
    },
    {
        "name": "Endpoints to generic object search methods",
        "description": "Search product groups, families or articles by field with a SQL-like condition",
    },
    {
        "name": "Endpoints to AUTHENTICATION data and methods",
        "description": "Almost all endpoints are protected and need authorization",
    },
    {
        "name": "Endpoints to CHANGELOG-data",
        "description": "The CHANGELOG saves all entity values to a json-field before an db-action like POST, PATCH or DELETE is performed.",
    },
    {
        "name": "Endpoints to DATABASE OPERATION data and methods",
        "description": "Methods to backup, restore, up- and download database-SQL-dumps",
    },
    {
        "name": "Endpoints to FILE-data",
        "description": "The cfiledata table contains all information to files stored along an db-entity. It will replace the curl-table in future.",
    },
    {
        "name": "Endpoints to IMPORT-functionality",
        "description": "All functionality available to import data from excel tables",
    },
    {"name": "ROOT", "description": "Redirect to static html data"},
]

app = FastAPI(
    version="0.1.4",
    title="koco_product_api",
    description=DESCRIPTION_STRING,
    openapi_tags=tags_metadata,
)
app.mount(
    path="/static",
    app=StaticFiles(directory="src/koco_product_sqlmodel/fastapi/static"),
    name="static",
)
FAVICON_PATH = "src/koco_product_sqlmodel/fastapi/static/img/favicon.ico"

origins = [
    "http://127.0.0.1:5173",
    "https://productdb.loehn.digital",
    "https://cat.koco-group.com",
    "https://srv-sdl",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001",
    "http://localhost:5173",
    "http://localhost:5000",
    "http://localhost:5001",
    "http://192.168.1.239:5000",
    "https://sdl.koco-group.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=("*", "GET", "POST", "PATCH", "DELETE"),
    allow_headers=("*"),
)

app.include_router(rcat.router, prefix="/catalogs")
app.include_router(rpg.router, prefix="/product_groups")
app.include_router(rfam.router, prefix="/families")
app.include_router(rart.route_article.router, prefix="/articles")
app.include_router(rapp.route_application.router, prefix="/applications")
app.include_router(ropt.route_option.router, prefix="/options")
app.include_router(rurl.route_url.router, prefix="/urls")
app.include_router(rst.route_spectable.router, prefix="/spectables")
app.include_router(rst.route_spectableitem.router, prefix="/spectableitems")
app.include_router(rchangelog.route_changelog.router, prefix="/changelog")
app.include_router(rdb.router, prefix="/database")
app.include_router(rfile.router, prefix="/filedata")
app.include_router(rxlsx.router, prefix="/import")
app.include_router(rsearch.router, prefix="/search")
app.include_router(rsec.router, prefix="/auth")


@app.get("/", tags=["ROOT"])
async def read_root():
    return RedirectResponse(url="/static/html/index.html")


@app.get("/favicon.ico", include_in_schema=False)
async def serve_favicon():
    return FileResponse(path=FAVICON_PATH)


def main():
    pass


if __name__ == "__main__":
    main()
