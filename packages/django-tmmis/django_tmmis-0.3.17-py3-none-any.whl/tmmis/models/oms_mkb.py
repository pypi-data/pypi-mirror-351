from .base_model import *


class OmsMkb(BaseModel):
    """
    Классификатор болезней МКБ-10
    """

    id = models.AutoField(db_column="MKBID", primary_key=True)
    ds = models.CharField(db_column="DS", max_length=10)
    name = models.CharField(db_column="NAME", max_length=255)
    date_b = models.DateField(db_column="Date_B")
    date_e = models.DateField(db_column="Date_E")
    rem = models.CharField(db_column="Rem", max_length=250)

    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "oms_MKB"
