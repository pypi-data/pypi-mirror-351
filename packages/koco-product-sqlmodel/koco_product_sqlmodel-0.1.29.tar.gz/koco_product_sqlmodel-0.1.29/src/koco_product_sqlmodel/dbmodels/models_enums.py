from enum import Enum
from sqlmodel import Enum as sqlm_enum

class StatusEnum(int, Enum):
    in_work = 1
    ready_for_review = 2
    released = 3


class OptionFeatureEnum(str, Enum):
    options = "Options"
    features = "Features"


class CUrlTypeEnum(str, Enum):
    photo = "photo"
    supplier_site = "supplier_site"
    drawing = "drawing"
    datasheet = "datasheet"
    speed_curves = "speed_curves"
    screw_option = "screw_option"
    step = "step"
    drawings_2D = "2D drawings"
    manual = "manual"
    software = "software"
    models_3D = "3D models"
    certifications = "certifications"
    drawings_3D = "3D drawings"
    catalog = "catalog"
    accessories = "accessories"
    firmware = "firmware"


class CDocumentType(str, Enum):
    photo = "photo"
    supplier_site = "supplier_site"
    drawing = "drawing"
    datasheet = "datasheet"
    speed_curves = "speed_curves"
    screw_option = "screw_option"
    step = "step"
    drawings_2D = "2D drawings"
    manual = "manual"
    software = "software"
    models_3D = "3D models"
    certifications = "certifications"
    drawings_3D = "3D drawings"
    catalog = "catalog"
    accessories = "accessories"
    firmware = "firmware"


class CUrlParentEnum(str, Enum):
    article = "article"
    family = "family"
    categorytree = "categorytree"


class SpectableTypeEnum(str, Enum):
    singlecol = "singlecol"
    multicol = "multicol"
    overview = "overview"
    free = "free"


class SpectableParentEnum(str, Enum):
    article = "article"
    family = "family"
    product_group = "product_group"
    catalog = "catalog"


class CUserRoleIdEnum(int, Enum):
    admin = 1
    editor = 2
    reader = 3

class CFiledataVisibility(int, Enum):
    nowhere = 0
    everywhere = 1
    only_web = 2
    only_catalog = 3



def main():
    pass


if __name__ == "__main__":
    main()
