from .base_model import *


class OmsTypedoc(BaseModel):
    """
    П: Типы документов, удостоверяющих личность
    """

    id = models.AutoField(db_column="TYPEDOCID", primary_key=True)
    c_doc = models.BigIntegerField(db_column="C_DOC")
    name_pfr = models.CharField(db_column="NAME_PFR", max_length=20)
    name = models.CharField(db_column="NAME", max_length=100)
    date_b = models.DateTimeField(db_column="Date_B")
    date_e = models.DateTimeField(db_column="Date_E")
    doc_num = models.CharField(db_column="DocNum", max_length=20)
    doc_ser = models.CharField(db_column="DocSer", max_length=10)
    code_egisz = models.CharField(db_column="CodeEgisz", max_length=150)

    class Meta:
        managed = False
        db_table = "oms_TYPEDOC"
