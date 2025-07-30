from .base_model import *


class LbrLaboratory(BaseModel):
    """
    Лаборатория
    """

    id = models.AutoField(db_column="LaboratoryID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    url = models.CharField(db_column="LaboratoryURL", max_length=4000)
    department = models.ForeignKey("OmsDepartment", db_column="rf_DepartmentID", **FK_DEFAULT)
    type = models.ForeignKey("LbrLaboratoryType", db_column="rf_LaboratoryTypeID", **FK_DEFAULT)
    name = models.CharField(db_column="LaboratoryName", max_length=255)
    kind = models.ForeignKey("LbrLaboratoryKind", db_column="rf_LaboratoryKindID", **FK_DEFAULT)
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")

    class Meta:
        managed = False
        db_table = "lbr_Laboratory"
