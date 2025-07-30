from .base_model import *


class OmsOkato(BaseModel):
    """
    Коды территорий по ОКАТО
    """

    id = models.AutoField(db_column="OKATOID", primary_key=True)
    c_okato = models.CharField(db_column="C_OKATO", max_length=15)
    msg_text = models.CharField(db_column="MSG_TEXT", max_length=250)
    o_name = models.CharField(db_column="O_NAME", max_length=250)
    c_pfr = models.DecimalField(db_column="C_PFR", max_digits=5, decimal_places=0)
    fok_name = models.CharField(db_column="FOK_NAME", max_length=60)
    pfr_code = models.IntegerField(db_column="PFRcode")
    date_b = models.DateTimeField(db_column="Date_B")
    date_e = models.DateTimeField(db_column="Date_E")

    class Meta:
        managed = False
        db_table = "oms_OKATO"
