from .base_model import *


class HltMedRecord(BaseModel):
    id = models.AutoField(db_column="MedRecordID", primary_key=True)
    uuid = models.CharField(db_column="Guid", max_length=36, unique=True, default=uuid4)
    confidentiality_code = models.CharField(db_column="ConfidentialityCode", max_length=50, default="")
    crc = models.TextField(db_column="CRC", default="")
    data = models.TextField(db_column="Data", default="")
    date = models.DateTimeField(db_column="Date", default=timezone.now)
    blank_template = models.ForeignKey("HltBlankTemplate", db_column="rf_BlankTemplateID", **FK_DEFAULT)
    lpu_doctor = models.ForeignKey("HltLpuDoctor", db_column="rf_LPUDoctorID", **FK_DEFAULT)
    visit_history = models.ForeignKey(
        "HltVisitHistory", models.DO_NOTHING, db_column="rf_VisitHistoryID", related_name="med_records", default=0
    )
    sign = models.TextField(db_column="Sign", default="Sign")
    event_data_time = models.DateTimeField(db_column="EventDataTime", default=timezone.now)
    person = models.ForeignKey("HltMkab", db_column="PersonGUID", to_field="uuid", **FK_DEFAULT)
    doc = models.CharField(
        db_column="rf_DOCGUID",
        max_length=36,
        default="00000000-0000-0000-0000-000000000000",
    )
    doc_type_def = models.CharField(
        db_column="rf_DocTypeDefGUID",
        max_length=36,
        default="00000000-0000-0000-0000-000000000000",
    )
    view_data = models.TextField(db_column="ViewData")
    create_username = models.CharField(db_column="CreateUserName", max_length=255, default="")
    edit_username = models.CharField(db_column="EditUserName", max_length=255, default="")
    create_user = models.ForeignKey("XUser", db_column="rf_CreateUserID", **FK_DEFAULT)
    edit_user = models.ForeignKey("XUser", db_column="rf_EditUserID", **FK_DEFAULT)
    desc = models.CharField(
        db_column="DescGuid",
        max_length=36,
        default="00000000-0000-0000-0000-000000000000",
    )
    create_date = models.DateTimeField(db_column="CreateDate", default=timezone.now)
    description = models.TextField(db_column="Description", default="")
    doc_prvd = models.CharField(
        db_column="rf_DocPrvdGuid",
        max_length=36,
        default="00000000-0000-0000-0000-000000000000",
    )
    # mkab = models.ForeignKey("HltMkab", db_column="rf_MKABGuid", to_field="uuid", **FK_DEFAULT)
    is_upload = models.BooleanField(db_column="isUpload", default=False)
    is_del = models.BooleanField(db_column="IsDel", default=False)

    flags = models.IntegerField(db_column="Flags", default=0)

    class Meta:
        managed = False
        db_table = "hlt_MedRecord"
