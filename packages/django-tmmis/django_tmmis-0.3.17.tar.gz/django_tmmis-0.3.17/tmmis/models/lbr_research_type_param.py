from .base_model import *


class LbrResearchTypeParam(BaseModel):
    """
    Параметры типа исследования
    """

    id = models.AutoField(db_column="ResearchTypeParamID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    code = models.CharField(db_column="Code", max_length=50)
    code_lis = models.CharField(db_column="CodeLis", max_length=50)
    flags = models.IntegerField(db_column="Flags")
    group_name = models.CharField(db_column="GroupName", max_length=200)
    max_normal_value = models.DecimalField(db_column="MaxNormalValue", max_digits=11, decimal_places=7)
    maxvalue = models.DecimalField(db_column="MaxValue", max_digits=11, decimal_places=7)
    min_normal_value = models.DecimalField(db_column="MinNormalValue", max_digits=11, decimal_places=7)
    minvalue = models.DecimalField(db_column="MinValue", max_digits=11, decimal_places=7)
    param_name = models.CharField(db_column="ParamName", max_length=255)
    param_unit = models.CharField(db_column="ParamUnit", max_length=200)
    required_param = models.BooleanField(db_column="RequiredParam")
    bio_m_id = models.IntegerField(db_column="rf_BioMID")
    microbe_id = models.IntegerField(db_column="rf_MicrobeID")
    research_param_value_type = models.ForeignKey(
        "LbrResearchParamValueType", db_column="rf_ResearchParamValueTypeID", **FK_DEFAULT
    )
    research_type = models.ForeignKey(
        "LbrResearchType", db_column="rf_ResearchTypeUGUID", to_field="uguid", **FK_DEFAULT
    )
    service_medical = models.ForeignKey("OmsServiceMedical", db_column="rf_ServiceMedicalID", **FK_DEFAULT)
    shortname = models.CharField(db_column="ShortName", max_length=212)
    template_param_name = models.CharField(db_column="TemplateParamName", max_length=200)
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")

    class Meta:
        managed = False
        db_table = "lbr_ResearchTypeParam"
