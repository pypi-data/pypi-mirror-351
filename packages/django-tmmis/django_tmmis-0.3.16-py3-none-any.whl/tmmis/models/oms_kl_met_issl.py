from .base_model import *


class OmsKlMetIssl(BaseModel):
    """
    Классификатор методов диагностического исследования (V029)
    """

    id = models.AutoField(db_column="kl_MetIsslID", primary_key=True)
    code = models.CharField(db_column="Code", max_length=10)
    name = models.CharField(db_column="Name", max_length=200)
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")
    description = models.TextField(db_column="Description")
    flags = models.IntegerField(db_column="Flags")
    guid = models.CharField(db_column="Guid", max_length=36)

    class Meta:
        managed = False
        db_table = "oms_kl_MetIssl"
