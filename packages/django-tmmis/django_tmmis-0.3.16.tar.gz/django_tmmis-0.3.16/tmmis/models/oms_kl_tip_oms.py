from .base_model import *


class OmsKlTipOms(BaseModel):
    """
    Классификатор типов документов, подтверждающих факт страхования по ОМС (F008)
    """

    id = models.AutoField(db_column="kl_TipOMSID", primary_key=True)
    date_b = models.DateTimeField(db_column="Date_B")
    date_e = models.DateTimeField(db_column="Date_E")
    doc_name = models.CharField(db_column="DOCNAME", max_length=254)
    id_doc = models.IntegerField(db_column="IDDOC")

    class Meta:
        managed = False
        db_table = "oms_kl_TipOMS"
