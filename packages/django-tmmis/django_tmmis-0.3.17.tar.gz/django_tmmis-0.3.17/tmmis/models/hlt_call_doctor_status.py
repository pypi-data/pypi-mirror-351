from .base_model import *


class HltCallDoctorStatus(BaseModel):
    id = models.AutoField(db_column="CallDoctorStatusID", primary_key=True)
    uuid = models.CharField(db_column="Guid", max_length=36)
    code = models.CharField(db_column="CODE", max_length=50)
    name = models.CharField(db_column="NAME", max_length=50)

    class Meta:
        managed = False
        db_table = "hlt_CallDoctorStatus"
