from .base_model import *


class LbrResearchType(BaseModel):
    """
    Классификатор исследований
    """

    id = models.AutoField(db_column="ResearchTypeID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    code = models.CharField(db_column="Code", max_length=50)
    period = models.IntegerField(db_column="Period")
    report = models.TextField(db_column="Report")
    name = models.CharField(db_column="ResearchName", max_length=8000)
    bio_mid = models.IntegerField(db_column="rf_BioMID")
    type = models.ForeignKey("LbrLaboratoryType", db_column="rf_LaboratoryTypeID", **FK_DEFAULT)
    research_type_kind = models.ForeignKey("LbrResearchTypeKind", db_column="rf_ResearchTypeKindID", **FK_DEFAULT)
    service_medical = models.ForeignKey("OmsServiceMedical", db_column="rf_ServiceMedicalID", **FK_DEFAULT)
    flags = models.IntegerField(db_column="Flags")
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")
    nom_service = models.ForeignKey("OmsKlNomService", db_column="rf_kl_NomServiceID", **FK_DEFAULT)
    is_complex = models.BooleanField(db_column="IsComplex")
    norm_duration = models.IntegerField(db_column="NormDuration")
    met_issl = models.ForeignKey("OmsKlMetIssl", db_column="rf_kl_MetIsslID", **FK_DEFAULT)
    component = models.CharField(db_column="Component", max_length=500)
    localization = models.CharField(db_column="Localization", max_length=500)
    body_area = models.CharField(db_column="BodyArea", max_length=500)
    rf_diagnostic_type_guid = models.CharField(db_column="rf_DiagnosticTypeGUID", max_length=36)

    class Meta:
        managed = False
        db_table = "lbr_ResearchType"
