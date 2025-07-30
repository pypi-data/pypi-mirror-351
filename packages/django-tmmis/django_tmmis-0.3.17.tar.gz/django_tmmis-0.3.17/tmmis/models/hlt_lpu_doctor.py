from .base_model import *


class HltLpuDoctor(BaseModel):
    """
    Медицинский персонал
    """

    id = models.AutoField(db_column="LPUDoctorID", primary_key=True)
    uuid = models.CharField(db_column="UGUID", max_length=36, unique=True, default=uuid4)
    pcod = models.CharField(db_column="PCOD", max_length=20)
    ot_v = models.CharField(db_column="OT_V", max_length=20)
    im_v = models.CharField(db_column="IM_V", max_length=20)
    d_ser = models.DateTimeField(db_column="D_SER")
    prvs = models.ForeignKey("OmsPrvs", db_column="rf_PRVSID", **FK_DEFAULT)
    fam_v = models.CharField(db_column="FAM_V", max_length=30)
    kv_kat = models.IntegerField(db_column="rf_KV_KATID")
    msg_text = models.CharField(db_column="MSG_Text", max_length=100)
    lpu = models.IntegerField(db_column="rf_LPUID")
    is_doctor = models.BooleanField(db_column="isDoctor")
    healing_room = models.IntegerField(db_column="rf_HealingRoomID")
    in_time = models.SmallIntegerField(db_column="inTime")
    dr = models.DateTimeField(db_column="DR")
    is_special = models.BooleanField(db_column="IsSpecial")
    prvd = models.IntegerField(db_column="rf_PRVDID")
    ss = models.CharField(db_column="SS", max_length=14)
    department = models.ForeignKey("OmsDepartment", db_column="rf_DepartmentID", **FK_DEFAULT)
    de_ser = models.DateTimeField(db_column="DE_SER")
    phone = models.CharField(db_column="Phone", max_length=25)

    class Meta:
        managed = False
        db_table = "hlt_LPUDoctor"
