from .base_model import *


class LbrResearch(BaseModel):
    """
    Исследование
    """

    id = models.AutoField(db_column="ResearchID", primary_key=True)
    guid = models.CharField(db_column="GUID", max_length=36, unique=True)
    date_complete = models.DateTimeField(db_column="Date_Complete")
    flag = models.IntegerField(db_column="Flag")
    is_complete = models.BooleanField(db_column="isComplete")
    lab_doct_fio = models.CharField(db_column="LAB_DOCT_FIO", max_length=200)
    lab_doct_pcod = models.CharField(db_column="LAB_DOCT_PCOD", max_length=20)
    number = models.CharField(db_column="Number", max_length=100)
    doctor = models.ForeignKey("HltLpuDoctor", db_column="rf_LabDoctorID", **FK_DEFAULT)
    laboratory_research = models.ForeignKey(
        "LbrLaboratoryResearch",
        db_column="rf_LaboratoryResearchGUID",
        to_field="guid",
        **FK_DEFAULT,
    )
    medical_history_id = models.IntegerField(db_column="rf_MedicalHistoryID")
    prev_research_guid = models.CharField(db_column="rf_PrevResearchGUID", max_length=36)
    research_type = models.ForeignKey(
        "LbrResearchType",
        db_column="rf_ResearchTypeUGUID",
        to_field="uguid",
        **FK_DEFAULT,
    )
    tap = models.ForeignKey("HltTap", db_column="rf_TAPID", **FK_DEFAULT)
    doc_prvd = models.ForeignKey("HltDocPrvd", db_column="rf_DocPRVDID", **FK_DEFAULT)
    comment = models.TextField(db_column="Comment")
    is_performed = models.BooleanField(db_column="IsPerformed")
    date_performed = models.DateTimeField(db_column="DatePerformed")
    conclusion = models.TextField(db_column="Conclusion")
    performed_doc_prvd = models.ForeignKey("HltDocPrvd", db_column="rf_PerformedDocPRVDID", **FK_DEFAULT)
    is_canceled = models.BooleanField(db_column="isCanceled")
    study_uid = models.CharField(db_column="StudyUID", max_length=100)
    performed_doc_fio = models.CharField(db_column="PerformedDocFio", max_length=100)
    performed_doc_p_code = models.CharField(db_column="PerformedDocPCode", max_length=20)
    date_registred = models.DateTimeField(db_column="DateRegistred")
    date_receipt = models.DateTimeField(db_column="DateReceipt")
    is_issued = models.BooleanField(db_column="IsIssued")
    date_issued = models.DateTimeField(db_column="DateIssued")
    issued_by_doc_prvd = models.ForeignKey("HltDocPrvd", db_column="rf_IssuedByDocPRVDID", **FK_DEFAULT)
    issued_to_lpu = models.ForeignKey("OmsLpu", db_column="rf_IssuedToLPUID", **FK_DEFAULT)
    issued_to_person = models.CharField(db_column="IssuedToPerson", max_length=200)
    is_registred = models.BooleanField(db_column="IsRegistred")
    is_receipt = models.BooleanField(db_column="IsReceipt")
    consult_doctor_fio = models.CharField(db_column="ConsultDoctorFio", max_length=200)
    is_manual_data = models.BooleanField(db_column="IsManualData")
    is_iemk_data = models.BooleanField(db_column="IsIemkData")
    is_main_expert = models.BooleanField(db_column="IsMainExpert")
    performed_lpu_name = models.CharField(db_column="PerformedLpuName", max_length=250)
    performed_laboratory = models.ForeignKey(
        "LbrLaboratory",
        db_column="rf_PerformedLaboratoryGUID",
        to_field="uguid",
        **FK_DEFAULT,
    )
    performed_department = models.ForeignKey(
        "OmsDepartment",
        db_column="rf_PerformedDepartmentGUID",
        to_field="uuid",
        **FK_DEFAULT,
    )
    is_rejected = models.BooleanField(db_column="isRejected")
    clinical_diagnos = models.CharField(db_column="ClinicalDiagnos", max_length=2000)
    is_complete_early = models.BooleanField(db_column="IsCompleteEarly")
    lpu_complete_early_guid = models.CharField(db_column="rf_LpuCompleteEarlyGUID", max_length=36)
    lpu_other_complete_early_guid = models.CharField(db_column="rf_LpuOtherCompleteEarlyGUID", max_length=36)
    research_profile = models.ForeignKey("OmsKlResearchProfile", db_column="rf_kl_ResearchProfileID", **FK_DEFAULT)
    consult_doc_prvd = models.ForeignKey("HltDocPrvd", db_column="rf_ConsultDocPRVDID", **FK_DEFAULT)
    url = models.CharField(db_column="Url", max_length=1000)
    effective_dose = models.DecimalField(db_column="EffectiveDose", max_digits=10, decimal_places=4)
    date_end_performed = models.DateTimeField(db_column="DateEndPerformed")
    cancel_reason = models.CharField(db_column="CancelReason", max_length=500)
    cancel_doc_prvd = models.ForeignKey("HltDocPrvd", db_column="rf_CancelDocPRVDID", **FK_DEFAULT)
    rf_lpu_performed_guid = models.CharField(db_column="rf_LPUPerformedGUID", max_length=36)
    rf_lpu_other_performed_guid = models.CharField(db_column="rf_LPUOtherPerformedGUID", max_length=36)
    rf_lpu_complete_guid = models.CharField(db_column="rf_LPUCompleteGUID", max_length=36)
    rf_lpu_other_complete_guid = models.CharField(db_column="rf_LPUOtherCompleteGUID", max_length=36)
    lab_comment = models.CharField(db_column="LabComment", max_length=1000)
    second_opinion_status = models.IntegerField(db_column="SecondOpinionStatus")
    lpu_second_opinion = models.ForeignKey(
        "OmsLpu",
        db_column="rf_LPUSecondOpinionGUID",
        to_field="uuid",
        **FK_DEFAULT,
    )
    cancel_doc_fio = models.CharField(db_column="CancelDocFio", max_length=200)
    cancel_doc_p_code = models.CharField(db_column="CancelDocPCode", max_length=20)

    class Meta:
        managed = False
        db_table = "lbr_Research"
