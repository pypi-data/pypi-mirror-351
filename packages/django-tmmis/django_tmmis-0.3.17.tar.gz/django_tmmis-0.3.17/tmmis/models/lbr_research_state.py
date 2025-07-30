from .base_model import *


class LbrResearchState(BaseModel):
    """
    Состояние обследования
    """

    id = models.AutoField(db_column="ResearchStateID", primary_key=True)
    description = models.TextField(db_column="Description")
    enum_name = models.CharField(db_column="EnumName", max_length=50)

    class Meta:
        managed = False
        db_table = "lbr_ResearchState"
