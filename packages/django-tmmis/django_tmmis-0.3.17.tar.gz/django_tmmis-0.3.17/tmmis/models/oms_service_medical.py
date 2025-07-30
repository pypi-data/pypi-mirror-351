from .base_model import *


class OmsServiceMedical(BaseModel):
    id = models.AutoField(db_column="ServiceMedicalID", primary_key=True)
    code = models.CharField(db_column="ServiceMedicalCode", max_length=50)
    name = models.CharField(db_column="ServiceMedicalName", max_length=500)
    visit_type_id = models.IntegerField(db_column="rf_kl_VisitTypeID")
    dd_service = models.ForeignKey("OmsKlDDService", db_column="rf_kl_DDServiceID", **FK_DEFAULT)
    med_care_type = models.ForeignKey("OmsKlMedCareType", db_column="rf_kl_MedCareTypeID", **FK_DEFAULT)
    med_care_unit_id = models.IntegerField(db_column="rf_kl_MedCareUnitID")
    operation_type_id = models.IntegerField(db_column="rf_kl_OperationTypeID")
    nom_service_id = models.IntegerField(db_column="rf_kl_NomServiceID")
    age_group = models.ForeignKey("OmsKlAgeGroup", db_column="rf_kl_AgeGroupID", **FK_DEFAULT)
    department_type = models.ForeignKey("OmsKlDepartmentType", db_column="rf_kl_DepartmentTypeID", **FK_DEFAULT)
    department_profile = models.ForeignKey(
        "OmsKlDepartmentProfile", db_column="rf_kl_DepartmentProfileID", **FK_DEFAULT
    )
    uuid = models.CharField(db_column="GUIDSM", max_length=36)
    date_b = models.DateTimeField(db_column="Date_B")
    date_e = models.DateTimeField(db_column="Date_E")
    id_serv = models.CharField(db_column="IDServ", max_length=40)
    prvd = models.ForeignKey("OmsPrvd", db_column="rf_PRVDID", **FK_DEFAULT)
    prvs = models.ForeignKey("OmsPrvs", db_column="rf_PRVSID", **FK_DEFAULT)
    service_medical = models.ForeignKey("OmsServiceMedical", db_column="rf_ServiceMedicalID", **FK_DEFAULT)
    doc = models.CharField(db_column="DOC", max_length=255)
    med_care_licence_id = models.IntegerField(db_column="rf_kl_MedCareLicenceID")
    sex_id = models.IntegerField(db_column="rf_kl_SexID")
    standart_cure_id = models.IntegerField(db_column="rf_sc_StandartCureID")
    fcode_usl = models.CharField(db_column="FCode_Usl", max_length=50)
    info = models.TextField(db_column="Info")
    flags = models.IntegerField(db_column="Flags")
    is_complex = models.BooleanField(db_column="isComplex")
    metod_hmp_id = models.IntegerField(db_column="rf_kl_MetodHMPID")
    action_teeth_id = models.IntegerField(db_column="rf_kl_ActionTeethID")
    profit_type_id = models.IntegerField(db_column="rf_kl_ProfitTypeID")
    is_dental_tech = models.BooleanField(db_column="isDentalTech")
    service_life = models.IntegerField(db_column="ServiceLife")
    warranty = models.IntegerField(db_column="Warranty")

    class Meta:
        managed = False
        db_table = "Oms_ServiceMedical"
