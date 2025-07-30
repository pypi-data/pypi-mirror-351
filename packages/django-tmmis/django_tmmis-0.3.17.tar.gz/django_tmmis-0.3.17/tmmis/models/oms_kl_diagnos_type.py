from .base_model import *


class OmsKlDiagnosType(BaseModel):
    """
    Тип диагноза
    """

    id = models.AutoField(db_column="kl_DiagnosTypeID", primary_key=True)
    code = models.CharField(db_column="Code", max_length=50)
    date_b = models.DateTimeField(db_column="Date_B")
    date_e = models.DateTimeField(db_column="Date_E")
    guid_diagnos_type = models.CharField(db_column="GUIDDiagnosType", max_length=36)
    name = models.CharField(db_column="Name", max_length=255)
    department_type_id = models.ForeignKey("OmsKlDepartmentType", db_column="rf_kl_DepartmentTypeID", **FK_DEFAULT)
    code_egisz = models.IntegerField(db_column="CodeEgisz")
    description = models.CharField(db_column="Description", max_length=255)

    class Meta:
        managed = False
        db_table = "oms_kl_DiagnosType"
