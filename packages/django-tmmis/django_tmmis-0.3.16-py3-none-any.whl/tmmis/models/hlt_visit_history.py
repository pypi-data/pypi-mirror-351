from .base_model import *


class HltVisitHistory(BaseModel):
    """
    Обращение
    """

    id = models.AutoField(db_column="VisitHistoryID", primary_key=True)
    uuid = models.CharField(db_column="GUID", max_length=36, unique=True, default=uuid4)
    date = models.DateTimeField(db_column="Date")
    is_complete = models.BooleanField(db_column="IsComplete")
    doctor_visit_table = models.ForeignKey("HltDoctorVisitTable", db_column="rf_DoctorVisitTableID", **FK_DEFAULT)
    lpu_doctor = models.IntegerField(db_column="rf_LPUDoctorID")
    mkab = models.ForeignKey("HltMkab", models.DO_NOTHING, db_column="rf_MKABID", related_name="visits")
    tap = models.ForeignKey("HltTap", models.DO_NOTHING, db_column="rf_TAPID", related_name="visits")
    begin_time = models.DateTimeField(db_column="BeginTime")
    fact_begin_time = models.DateTimeField(db_column="FactBeginTime")
    fact_end_time = models.DateTimeField(db_column="FactEndTime")
    doc_prvd = models.ForeignKey("HltDocPrvd", db_column="rf_DocPRVDID", **FK_DEFAULT)
    conclusion = models.TextField(db_column="Conclusion")
    date_conclusion = models.DateTimeField(db_column="DateConclusion")

    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "hlt_VisitHistory"
