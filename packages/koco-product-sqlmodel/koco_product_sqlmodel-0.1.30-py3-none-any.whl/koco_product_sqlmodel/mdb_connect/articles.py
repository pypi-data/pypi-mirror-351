from koco_product_sqlmodel.mdb_connect.init_db_con import mdb_engine
from sqlmodel import Session, select
from koco_product_sqlmodel.dbmodels.definition import (
    CApplication,
    CArticle,
    CArticleGet,
    CArticlePost,
    CCatalog,
    CFamily,
    COption,
    CProductGroup,
    CUrl,
)
import logging

logger = logging.getLogger("mdb_connect")


def create_article(article: CArticle) -> CArticle:
    if not article:
        return
    with Session(mdb_engine) as session:
        session.add(article)
        session.commit()
        statement = (
            select(CArticle)
            .where(CArticle.article == article.article)
            .where(CArticle.family_id == article.family_id)
        )
        return session.exec(statement=statement).one_or_none()

def update_article_DB(id: int | None, art_post: CArticlePost) -> CArticle | None:
    if id == None:
        return
    with Session(mdb_engine) as session:
        statement = select(CArticle).where(CArticle.id == id)
        art = session.exec(statement=statement).one_or_none()
        if art == None:
            return
        art_data = art_post.model_dump(exclude_unset=True)
        art = art.sqlmodel_update(art_data)
        session.add(art)
        session.commit()
        session.refresh(art)
    return art

def collect_article(article_id: int = 1) -> dict:
    """Refactored version on collect article. Returns no dict with SQLModels or lists of SQLModels"""
    with Session(mdb_engine) as session:
        statement = (
            select(CArticle, CFamily, CProductGroup, CCatalog)
            .join(CFamily, CFamily.id == CArticle.family_id)
            .join(CProductGroup, CProductGroup.id == CFamily.product_group_id)
            .join(CCatalog, CCatalog.id == CProductGroup.catalog_id)
            .where(CArticle.id == article_id)
        )
        article, fam, pg, cat = session.exec(statement).one_or_none()
        logger.debug(
            f"Collected article {cat.supplier}/{pg.product_group}/{fam.family}/{article.article}/id={article.id}"
        )
        breadcrumb = {
            "article": article.article,
            "family": fam.family,
            "family_id": fam.id,
            "product_group": pg.product_group,
            "product_group_id": pg.id,
            "supplier": cat.supplier,
            "catalog_id": cat.id,
        }
        if not article.description:
            article.description = fam.type
        statement = (
            select(CUrl)
            .where(CUrl.parent_id == article_id)
            .where(CUrl.parent == "article")
        )
        urls = session.exec(statement).all()
        statement = (
            select(CUrl).where(CUrl.parent_id == fam.id).where(CUrl.parent == "family")
        )
        urls += session.exec(statement)
        image_url: str = None
        photos = []
        if urls:
            photos = [fu for fu in urls if fu.type.lower() == "photo"]
        if photos != []:
            image_url = photos[0].KOCO_url

        statement = (
            select(CApplication.application)
            .where(CApplication.family_id == fam.id)
            .order_by(CApplication.id)
        )
        applications = session.exec(statement).all()
        statement = (
            select(COption)
            .where(COption.family_id == fam.id)
            .where(COption.type == "Options")
            .order_by(COption.id)
        )
        options = session.exec(statement).all()
        statement = (
            select(COption)
            .where(COption.family_id == fam.id)
            .where(COption.type == "Features")
            .order_by(COption.id)
        )
        features = session.exec(statement).all()
    return article, breadcrumb, urls, image_url, applications, options, features


def get_articles_db(family_id: int) -> list[CArticleGet]:
    if family_id == None:
        statement = select(CArticle)
    else:
        statement = select(CArticle).where(CArticle.family_id == family_id)
    with Session(mdb_engine) as session:
        return session.exec(statement=statement).all()


def get_article_db_by_id(id: int) -> CArticle:
    if id == None:
        return
    statement = select(CArticle).where(CArticle.id == id)
    with Session(mdb_engine) as session:
        return session.exec(statement=statement).one_or_none()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
