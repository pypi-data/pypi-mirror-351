from .base_model import *


class HltBlankTemplate(BaseModel):
    id = models.AutoField(db_column="BlankTemplateID", primary_key=True)
    caption = models.CharField(db_column="Caption", max_length=250)
    code = models.CharField(db_column="Code", max_length=50)
    flags = models.IntegerField(db_column="Flags")
    guid = models.CharField(db_column="GUID", max_length=36)
    blank_template = models.ForeignKey("HltBlankTemplate", db_column="rf_BlankTemplateID", **FK_DEFAULT)
    template_edit = models.TextField(db_column="TemplateEdit")
    template_print = models.TextField(db_column="TemplatePrint")
    value = models.TextField(db_column="Value")
    validations = models.TextField(db_column="Validations")
    actual = models.BooleanField(db_column="Actual")
    comment = models.CharField(db_column="Comment", max_length=2000)
    source = models.CharField(db_column="Source", max_length=2000)
    author = models.CharField(db_column="Author", max_length=255)
    createdate = models.DateTimeField(db_column="CreateDate")
    rf_blank_template_type_id = models.IntegerField(db_column="rf_BlankTemplateTypeID")
    rf_context_id = models.IntegerField(db_column="rf_ContextID")
    version = models.CharField(db_column="Version", max_length=50)
    xml_data = models.TextField(db_column="XmlData")
    rf_med_record_type_guid = models.CharField(db_column="rf_MedRecordTypeGuid", max_length=36)

    class Meta:
        managed = False
        db_table = "hlt_BlankTemplate"
