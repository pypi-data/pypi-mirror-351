from .base_model import *


class XDocElemDef(BaseModel):
    id = models.AutoField(db_column="DocElemDefID", primary_key=True)
    type_def = models.ForeignKey("XDocTypeDef", db_column="DocTypeDefID", **FK_DEFAULT)
    name = models.CharField(db_column="Name", max_length=50)
    mnem_code = models.CharField(db_column="MnemCode", max_length=50)
    caption = models.CharField(db_column="Caption", max_length=500)
    description = models.CharField(db_column="Description", max_length=500)
    elem_type = models.IntegerField(db_column="ElemType")
    value_type = models.IntegerField(db_column="ValueType")
    value_size = models.IntegerField(db_column="ValueSize")
    value_scale = models.IntegerField(db_column="ValueScale")
    field_name = models.CharField(db_column="FieldName", max_length=2500)
    linked_doc_type_def_id = models.IntegerField(db_column="LinkedDocTypeDefID")
    linked_doc_elem_def_id = models.IntegerField(db_column="LinkedDocElemDefID")
    access_def = models.IntegerField(db_column="AccessDef", **NULL)
    tag_name = models.CharField(db_column="TagName", max_length=50)
    delete_mode = models.IntegerField(db_column="DeleteMode", **NULL)
    show_mode = models.IntegerField(db_column="ShowMode", **NULL)
    srv_doc_elem_def_id = models.IntegerField(db_column="SRVDocElemDefID")
    guid = models.CharField(db_column="GUID", max_length=36)
    pos = models.IntegerField(db_column="Pos")
    outputformat = models.CharField(db_column="OutputFormat", max_length=50)
    flags = models.IntegerField(db_column="Flags")
    category_name = models.CharField(db_column="CategoryName", max_length=50)
    sql_data_type = models.CharField(db_column="SqlDataType", max_length=50)

    class Meta:
        managed = False
        db_table = "x_DocElemDef"
