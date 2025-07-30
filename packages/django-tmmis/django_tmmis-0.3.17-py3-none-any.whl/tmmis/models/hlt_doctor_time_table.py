from .base_model import *


class HltDoctorTimeTable(BaseModel):
    id = models.AutoField(db_column="DoctorTimeTableID", primary_key=True)
    begin_time = models.DateTimeField(db_column="Begin_Time")
    end_time = models.DateTimeField(db_column="End_Time")
    date = models.DateTimeField(db_column="Date")
    lpu_doctor = models.ForeignKey("HltLpuDoctor", db_column="rf_LPUDoctorID", **FK_DEFAULT)
    doc_busy_type_id = models.IntegerField(db_column="rf_DocBusyType")
    flag_access = models.IntegerField(db_column="FlagAccess")
    flags = models.IntegerField(db_column="FLAGS")
    uguid = models.CharField(db_column="UGUID", max_length=36)
    last_stub_num = models.IntegerField(db_column="LastStubNum")
    plan_ue = models.IntegerField(db_column="PlanUE")
    doc_prvd = models.ForeignKey("HltDocPrvd", db_column="rf_DocPRVDID", **FK_DEFAULT)
    healing_room = models.ForeignKey("HltHealingRoom", db_column="rf_HealingRoomID", **FK_DEFAULT)
    tt_source = models.IntegerField(db_column="TTSource")
    used_ue = models.IntegerField(db_column="UsedUE")
    is_katl_visit = models.BooleanField(db_column="IsKatlVisit")
    is_out_schedule = models.BooleanField(db_column="IsOutSchedule")
    comment_mobil_brigade = models.CharField(db_column="CommentMobilBrigade", max_length=1000)
    address_mobil_brigade_id = models.IntegerField(db_column="rf_AddressMobilBrigadeID")

    class Meta:
        managed = False
        db_table = "hlt_DoctorTimeTable"
