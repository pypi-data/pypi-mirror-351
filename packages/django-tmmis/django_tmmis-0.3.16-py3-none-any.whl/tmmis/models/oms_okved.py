from .base_model import *


class OmsOkved(BaseModel):
    """
    Код экономического вида деятельности по ОКВЭД
    """

    id = models.AutoField(db_column="OKVEDID", primary_key=True)
    uuid = models.CharField(db_column="UGUID", max_length=36, unique=True, default=uuid4)
    name = models.CharField(db_column="NAME", max_length=100)
    code = models.CharField(db_column="OKVED_CODE", max_length=10)
    date_in = models.DateTimeField(db_column="DATEIN")
    date_out = models.DateTimeField(db_column="DATEOUT")
    date_edit = models.DateTimeField(db_column="DATEEDIT")

    class Meta:
        managed = False
        db_table = "oms_OKVED"
