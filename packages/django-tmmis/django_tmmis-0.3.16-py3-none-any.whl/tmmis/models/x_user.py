from .base_model import *


class XUser(BaseModel):
    id = models.AutoField(db_column="UserID", primary_key=True)
    uuid = models.CharField(db_column="GUID", max_length=36, unique=True)
    windows_name = models.CharField(db_column="WindowsName", max_length=500)
    general_login = models.CharField(db_column="GeneralLogin", max_length=50)
    general_password = models.CharField(db_column="GeneralPassword", max_length=50)
    auth_mode = models.SmallIntegerField(db_column="AuthMode")
    fio = models.CharField(db_column="FIO", max_length=50, blank=True, null=True)
    email = models.CharField(db_column="Email", max_length=256)

    class Meta:
        managed = False
        db_table = "x_User"
