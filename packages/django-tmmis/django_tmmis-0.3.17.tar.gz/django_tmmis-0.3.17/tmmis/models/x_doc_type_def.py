from .base_model import *


class XDocTypeDef(BaseModel):
    id = models.AutoField(db_column="DocTypeDefID", primary_key=True)
    name = models.CharField(db_column="Name", max_length=50)
    mnem_code = models.CharField(db_column="MnemCode", max_length=50)
    caption = models.CharField(db_column="Caption", max_length=50)
    description = models.CharField(db_column="Description", max_length=500)
    head_table = models.CharField(db_column="HeadTable", max_length=50, **NULL)
    pk_name = models.CharField(db_column="PK_Name", max_length=50, **NULL)
    tag_name = models.CharField(db_column="TagName", max_length=50, **NULL)
    to_string = models.IntegerField(db_column="ToString")
    theme_id = models.IntegerField(db_column="ThemeID")
    guid = models.CharField(db_column="GUID", max_length=36)
    type = models.IntegerField(db_column="Type")
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "x_DocTypeDef"
