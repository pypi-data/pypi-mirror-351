from .base_model import *


class AtfFileAttachment(BaseModel):
    id = models.AutoField(db_column="FileAttachmentID", primary_key=True)
    uuid = models.CharField(db_column="Guid", max_length=36, unique=True, default=uuid4)

    num = models.IntegerField(db_column="Num", default=0)
    description = models.TextField(db_column="Description", default="")
    path = models.CharField(db_column="Path", max_length=500)
    date_create = models.DateTimeField(db_column="DateCreate", default=timezone.now)
    create_username = models.CharField(db_column="CreateUserName", max_length=255, default="")
    create_user = models.ForeignKey("XUser", db_column="rf_CreateUserID", **FK_DEFAULT)
    file_info = models.ForeignKey(
        "AtfFileInfo",
        models.DO_NOTHING,
        related_name="attachments",
        db_column="rf_FileInfoID",
    )

    flags = models.IntegerField(db_column="Flags", default=0)

    class Meta:
        managed = False
        db_table = "atf_FileAttachment"
