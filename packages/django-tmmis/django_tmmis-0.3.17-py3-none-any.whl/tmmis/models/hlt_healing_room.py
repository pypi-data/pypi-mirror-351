from .base_model import *


class HltHealingRoom(BaseModel):
    """
    Кабинет
    """

    id = models.AutoField(db_column="HealingRoomID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36)
    num = models.CharField(db_column="Num", max_length=50)
    comment = models.CharField(db_column="Comment", max_length=50)
    flat = models.IntegerField(db_column="Flat")
    in_time = models.IntegerField(db_column="InTime")
    department = models.ForeignKey("OmsDepartment", db_column="rf_DepartmentID", **FK_DEFAULT)
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")
    date_actualization = models.DateTimeField(db_column="DateActualization")
    oid = models.CharField(db_column="OID", max_length=50)

    class Meta:
        managed = False
        db_table = "hlt_HealingRoom"
