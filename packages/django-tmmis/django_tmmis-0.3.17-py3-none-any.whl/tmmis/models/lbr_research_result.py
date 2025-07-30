from .base_model import *


class LbrResearchResult(BaseModel):
    """
    Результаты исследования
    """

    id = models.AutoField(db_column="ResearchResultID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    caption = models.CharField(db_column="Caption", max_length=200)
    date_complete = models.DateTimeField(db_column="DateComplete")
    ext_link = models.CharField(db_column="ExtLink", max_length=4000)
    href = models.CharField(db_column="HRef", max_length=100)
    l_ref = models.CharField(db_column="LRef", max_length=100)
    r_boolean = models.BooleanField(db_column="rBoolean")
    r_datetime = models.DateTimeField(db_column="rDateTime")
    r_decimal = models.DecimalField(db_column="rDecimal", max_digits=18, decimal_places=2)
    required_param = models.BooleanField(db_column="RequiredParam")
    research = models.ForeignKey(
        "LbrResearch", db_column="rf_ResearchGUID", to_field="guid", max_length=36, **FK_DEFAULT
    )
    research_param_value_type = models.ForeignKey(
        "LbrResearchParamValueType", db_column="rf_ResearchParamValueTypeID", **FK_DEFAULT
    )
    research_type_param = models.ForeignKey(
        "LbrResearchTypeParam", db_column="rf_ResearchTypeParamUGUID", to_field="uguid", **FK_DEFAULT
    )
    r_integer = models.IntegerField(db_column="rInteger")
    r_string = models.TextField(db_column="rString")
    test_note = models.TextField(db_column="TestNote")
    unit = models.CharField(db_column="Unit", max_length=100)
    value = models.TextField(db_column="Value")
    is_addition = models.BooleanField(db_column="IsAddition")
    r_guid = models.CharField(db_column="rGUID", max_length=36)
    is_deviation = models.BooleanField(db_column="IsDeviation")

    class Meta:
        managed = False
        db_table = "lbr_ResearchResult"
