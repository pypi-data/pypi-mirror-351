from .base_model import *


class HltDispResultTypeValue(BaseModel):
    """
    Значения типов результата
    """

    id = models.AutoField(db_column="disp_ResultTypeValueID", primary_key=True)
    code = models.CharField(db_column="Code", max_length=100)
    name = models.TextField(db_column="Name")
    guid = models.CharField(db_column="Guid", max_length=36, unique=True, default=uuid4)
    date_begin = models.DateTimeField(db_column="DateBegin", default=timezone.now)
    date_end = models.DateTimeField(db_column="DateEnd", default=timezone.datetime(2222, 1, 1))
    flags = models.IntegerField(db_column="Flags", default=0)
    rf_disp_type_guid = models.CharField(
        db_column="rf_DispTypeGuid",
        max_length=36,
        default="00000000-0000-0000-0000-000000000000",
    )
    result_type = models.ForeignKey(
        "HltDispResultType",
        models.DO_NOTHING,
        to_field="guid",
        db_column="rf_ResultTypeGuid",
        max_length=36,
    )
    rf_variant_guid = models.CharField(
        db_column="rf_VariantGuid",
        max_length=36,
        default="00000000-0000-0000-0000-000000000000",
    )
    point = models.DecimalField(db_column="Point", max_digits=18, decimal_places=2, default="0.0")

    class Meta:
        managed = False
        db_table = "hlt_disp_ResultTypeValue"
