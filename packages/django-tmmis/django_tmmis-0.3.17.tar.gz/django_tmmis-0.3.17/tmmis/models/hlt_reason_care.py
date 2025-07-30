from .base_model import *


class HltReasonCare(BaseModel):
    """
    Причина выдачи док-та о врем. нетрудоспособности
    """

    id = models.AutoField(db_column="ReasonCareID", primary_key=True)
    cod = models.CharField(db_column="COD", max_length=6)
    name = models.CharField(db_column="NAME", max_length=50)
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")

    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "hlt_ReasonCare"
