import datetime

from .base_model import *


class HltMkbTap(BaseModel):
    """
    Диагнозы ТАП
    """

    id = models.AutoField(db_column="MKB_TAPID", primary_key=True)
    mkb = models.ForeignKey("OmsMkb", db_column="rf_MKBID", **FK_DEFAULT)
    tap = models.ForeignKey("HltTap", db_column="rf_TAPID", **FK_DEFAULT)
    is_main = models.BooleanField(db_column="isMain", default=False)
    comments = models.CharField(db_column="Comments", max_length=4096, default="")
    flags = models.IntegerField(db_column="FLAGS", default=0)
    registration_end_reason_id = models.IntegerField(db_column="rf_kl_RegistrationEndReasonID", default=0)
    disease_type = models.ForeignKey("OmsKlDiseaseType", db_column="rf_kl_DiseaseTypeID", **FK_DEFAULT)
    trauma_type_id = models.IntegerField(db_column="rf_kl_TraumaTypeID", default=0)
    disp_reg_state_id = models.IntegerField(db_column="rf_kl_DispRegStateID", default=0)
    # doc_guid = models.UUIDField(db_column="rf_DocGUID", max_length=3636, **NULL)
    # doc_type_def_guid = models.UUIDField(db_column="rf_DocTypeDefGUID", max_length=36, **NULL)
    diagnos_type = models.ForeignKey("OmsKlDiagnosType", db_column="rf_kl_DiagnosTypeID", **FK_DEFAULT)
    mkb_external_id = models.IntegerField(db_column="rf_MKBExternalID", default=0)
    guid = models.CharField(db_column="GUID", max_length=36, default=uuid4)
    date = models.DateTimeField(db_column="Date", default=datetime.date(1900, 1, 1))
    clinical_diagnos = models.CharField(db_column="ClinicalDiagnos", max_length=2000, default="")

    # Эти поля есть в схеме БД Белгородской МИС, но нет, к примеру, в Челябинске
    # is_final = models.BooleanField(db_column="IsFinal", default=False)
    # doc_prvd = models.ForeignKey("HltDocPrvd", db_column="rf_DocPRVDID", **FK_DEFAULT)

    class Meta:
        managed = False
        db_table = "hlt_mkb_tap"
