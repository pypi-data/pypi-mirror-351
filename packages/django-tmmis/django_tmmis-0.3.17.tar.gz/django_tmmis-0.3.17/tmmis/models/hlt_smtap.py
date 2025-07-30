import datetime

from .base_model import *


class HltSmTap(BaseModel):
    id = models.AutoField(db_column="SMTAPID", primary_key=True)
    tap = models.ForeignKey("HltTap", db_column="rf_TAPID", **FK_DEFAULT)
    reg_s = models.SmallIntegerField(db_column="REG_S", default=0)
    uuid = models.CharField(db_column="SMTAPGuid", max_length=36, unique=True, default=uuid4)
    is_fake = models.BooleanField(db_column="IsFake", default=0)
    lpu_doctor = models.ForeignKey("HltLpuDoctor", db_column="rf_LPUDoctorID", **FK_DEFAULT)
    count = models.DecimalField(db_column="Count", max_digits=9, decimal_places=2, default=0)
    date_p = models.DateTimeField(db_column="DATE_P", default=timezone.now)
    doctor_visit_table = models.ForeignKey("HltDoctorVisitTable", db_column="rf_DoctorVisitTableID", **FK_DEFAULT)
    flags = models.IntegerField(db_column="FLAGS", default=0)
    lpu = models.ForeignKey("OmsLpu", db_column="rf_LPUID", **FK_DEFAULT)
    mkb = models.ForeignKey("OmsMkb", db_column="rf_MKBID", **FK_DEFAULT)
    description = models.CharField(db_column="Description", max_length=1000, default="")
    service_medical = models.ForeignKey("OmsServiceMedical", db_column="rf_omsServiceMedicalID", **FK_DEFAULT)
    tariff_id = models.IntegerField(db_column="rf_TariffID", default=0)
    department = models.ForeignKey("OmsDepartment", db_column="rf_DepartmentID", **FK_DEFAULT)
    create_user_name = models.CharField(db_column="CreateUserName", max_length=255, default="не определено")
    edit_user_name = models.CharField(db_column="EditUserName", max_length=255, default="не определено")
    flag_bill = models.BooleanField(db_column="FlagBill", default=0)
    flag_complete = models.BooleanField(db_column="FlagComplete", default=0)
    flag_pay = models.BooleanField(db_column="FlagPay", default=0)
    flag_statist = models.BooleanField(db_column="FlagStatist", default=0)
    create_user = models.ForeignKey("XUser", db_column="rf_CreateUserID", **FK_DEFAULT)
    edit_user = models.ForeignKey("XUser", db_column="rf_EditUserID", **FK_DEFAULT)
    invoice_id = models.IntegerField(db_column="rf_InvoiceID", default=0)
    doc_prvd = models.ForeignKey("HltDocPrvd", db_column="rf_DocPRVDID", **FK_DEFAULT)
    sum_opl = models.DecimalField(db_column="Sum_Opl", max_digits=18, decimal_places=2, default=0)
    sum_v = models.DecimalField(db_column="Sum_V", max_digits=18, decimal_places=2, default=0)
    date_e = models.DateTimeField(db_column="DATE_E", default=timezone.now)
    visit_place = models.ForeignKey("OmsKlVisitPlace", db_column="rf_kl_VisitPlaceID", **FK_DEFAULT)
    lpu_doctor_sid = models.IntegerField(db_column="rf_LPUDoctor_SID", default=0)
    bill_service_id = models.IntegerField(db_column="rf_BillServiceID", default=0)
    root_sm_tap = models.ForeignKey("HltSmTap", db_column="rf_RootSMTAPID", **FK_DEFAULT)
    operation_id = models.IntegerField(db_column="rf_OperationID", default=0)
    teeth_id = models.IntegerField(db_column="rf_kl_TeethID", default=0)
    action_teeth_id = models.IntegerField(db_column="rf_kl_ActionTeethID", default=0)
    usl_profit_type_id = models.IntegerField(db_column="rf_usl_ProfitTypeID", default=0)
    date_warranty = models.DateTimeField(db_column="DateWarranty", default=datetime.date(2222, 1, 1))
    is_fail_warranty = models.BooleanField(db_column="IsFailWarranty", default=0)
    assistant_doc_prvd_id = models.IntegerField(db_column="rf_AssistantDocPRVDID", default=0)
    nom_service_id = models.IntegerField(db_column="rf_kl_NomServiceID", default=0)
    dogovor_paying_id = models.IntegerField(db_column="rf_DogovorPayingID", default=0)

    class Meta:
        managed = False
        db_table = "hlt_SMTAP"
