from .base_model import *


class OmsPrvd(BaseModel):
    """
    В: Должности
    """

    id = models.AutoField(db_column="PRVDID", primary_key=True)
    name = models.CharField(db_column="NAME", max_length=100)
    c_prvd = models.CharField(db_column="C_PRVD", max_length=50)
    msg_text = models.CharField(db_column="MSG_TEXT", max_length=100)
    date_b = models.DateTimeField(db_column="Date_B")
    date_e = models.DateTimeField(db_column="Date_E")
    profit_type = models.ForeignKey("OmsKlProfitType", models.DO_NOTHING, db_column="rf_kl_ProfitTypeID")

    class Meta:
        managed = False
        db_table = "oms_PRVD"
