from .base_model import *


class OmsDepartment(BaseModel):
    id = models.AutoField(db_column="DepartmentID", primary_key=True)
    uuid = models.CharField(db_column="GUIDDepartment", max_length=36, unique=True)

    code = models.CharField(db_column="DepartmentCODE", max_length=50)
    name = models.CharField(db_column="DepartmentNAME", max_length=255)
    type = models.ForeignKey("OmsKlDepartmentType", db_column="rf_kl_DepartmentTypeID", **FK_DEFAULT)
    lpu = models.ForeignKey("OmsLpu", models.DO_NOTHING, db_column="rf_LPUID")
    zav_pcod = models.CharField(db_column="ZAVPCOD", max_length=10)
    zav_fio = models.CharField(db_column="ZAVFIO", max_length=70)
    profile = models.ForeignKey("OmsKlDepartmentProfile", db_column="rf_kl_DepartmentProfileID", **FK_DEFAULT)
    code_department = models.IntegerField(db_column="Code_Department")
    n_otd = models.CharField(db_column="N_OTD", max_length=5)
    rem = models.CharField(db_column="Rem", max_length=255)
    age_group = models.ForeignKey("OmsKlAgeGroup", db_column="rf_kl_AgeGroupID", **FK_DEFAULT)
    date_b = models.DateTimeField(db_column="Date_B")
    date_e = models.DateTimeField(db_column="Date_E")
    code_kladr = models.CharField(db_column="CodeKLADR", max_length=10)
    fax = models.CharField(db_column="FAX", max_length=50)
    address = models.ForeignKey("KlaAddress", db_column="rf_AddressID", **FK_DEFAULT)
    tel = models.CharField(db_column="Tel", max_length=50)
    med_care_type = models.ForeignKey("OmsKlMedCareType", db_column="rf_kl_MedCareTypeID", **FK_DEFAULT)

    class Meta:
        managed = False
        db_table = "oms_Department"
