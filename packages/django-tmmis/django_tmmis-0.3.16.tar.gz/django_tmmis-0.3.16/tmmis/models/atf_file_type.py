from .base_model import *


class AtfFileType(BaseModel):
    """
    Тип прикрепленного документа
    """

    id = models.AutoField(db_column="FileTypeID", primary_key=True)
    uuid = models.CharField(db_column="Guid", max_length=36, unique=True, default=uuid4)

    code = models.CharField(db_column="Code", max_length=100, default="")
    name = models.TextField(db_column="Name")
    description = models.TextField(db_column="Description", default="")
    date_begin = models.DateTimeField(db_column="DateBegin", default=timezone.now)
    date_end = models.DateTimeField(db_column="DateEnd", default=timezone.datetime(2222, 1, 1))

    flags = models.IntegerField(db_column="Flags", default=0)

    class Meta:
        managed = False
        db_table = "atf_FileType"
