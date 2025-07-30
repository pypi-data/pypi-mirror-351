from .base_model import *


class OmsKlVisitResult(BaseModel):
    id = models.AutoField(db_column="kl_VisitResultID", primary_key=True)
    guid = models.CharField(db_column="VisitResultGUID", max_length=36)

    code = models.CharField(db_column="CODE", max_length=50)
    name = models.CharField(db_column="NAME", max_length=255)
    date_b = models.DateTimeField(db_column="Date_B")
    date_e = models.DateTimeField(db_column="Date_E")
    department_type = models.ForeignKey("OmsKlDepartmentType", db_column="rf_kl_DepartmentTypeID", **FK_DEFAULT)
    code_dd = models.CharField(db_column="CODE_DD", max_length=50)
    code_region = models.CharField(db_column="CODE_Region", max_length=50)
    code_federal = models.CharField(db_column="CODE_Federal", max_length=50)
    dd_service = models.ForeignKey("OmsKlDDService", db_column="rf_kl_DDServiceID", **FK_DEFAULT)

    class Meta:
        managed = False
        db_table = "oms_kl_VisitResult"
