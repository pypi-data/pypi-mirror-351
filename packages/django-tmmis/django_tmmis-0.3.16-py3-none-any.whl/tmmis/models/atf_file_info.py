from .base_model import *


class AtfFileInfo(BaseModel):
    """
    Информация о прикрепленном документе
    """

    id = models.AutoField(db_column="FileInfoID", primary_key=True)
    uuid = models.CharField(db_column="Guid", max_length=36, unique=True, default=uuid4)

    date_doc = models.DateTimeField("Дата документа", db_column="DateDoc", default=timezone.now)
    desc_guid = models.CharField("Уникальный идентификатор источника", db_column="DescGuid", max_length=36)
    description = models.TextField("Описание", db_column="Description", default="")
    doctor_name = models.CharField("ФИО врача", db_column="DoctorName", max_length=255, default="")
    lpu_name = models.CharField("Наименование ЛПУ", db_column="LPUName", max_length=255, default="")
    desc_type = models.CharField("Тип документа источника", db_column="rf_DescTypeGuid", max_length=36)
    doctor_guid = models.CharField(
        "Врач",
        db_column="rf_DoctorGuid",
        max_length=36,
        default="00000000-0000-0000-0000-000000000000",
    )
    doctor_type = models.CharField(
        "Тип элемента БД, характеризующий доктора",
        db_column="rf_DoctorTypeGuid",
        max_length=36,
        default="00000000-0000-0000-0000-000000000000",
    )
    file_type = models.ForeignKey("AtfFileType", db_column="rf_FileTypeID", **FK_DEFAULT)
    lpu = models.ForeignKey("OmsLpu", to_field="uuid", db_column="rf_LPUGuid", **FK_DEFAULT)
    lpu_type = models.CharField(db_column="rf_LPUTypeGuid", max_length=36)

    flags = models.IntegerField(db_column="Flags", default=0)

    class Meta:
        managed = False
        db_table = "atf_FileInfo"
