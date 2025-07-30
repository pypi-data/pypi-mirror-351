from .base_model import *


class HltDispResultType(BaseModel):
    """
    Тип результатов заключения
    """

    id = models.AutoField(db_column="disp_ResultTypeID", primary_key=True)
    code = models.CharField(db_column="Code", max_length=100, default="")
    name = models.TextField(db_column="Name")
    guid = models.CharField(db_column="Guid", max_length=36, unique=True, default=uuid4)
    date_begin = models.DateTimeField(db_column="DateBegin", default=timezone.now)
    date_end = models.DateTimeField(db_column="DateEnd", default=timezone.datetime(2222, 1, 1))
    flags = models.IntegerField(db_column="Flags", default=0)
    rf_disp_type_guid = models.CharField(
        db_column="rf_DispTypeGuid",
        max_length=36,
        default="00000000-0000-0000-0000-000000000000",
    )
    is_main = models.BooleanField(db_column="IsMain", default=False)
    is_show_ctrl = models.SmallIntegerField(db_column="IsShowCtrl", default=0)
    age_from = models.IntegerField(db_column="AgeFrom", default=0)
    age_to = models.IntegerField(db_column="AgeTo", default=0)
    sex_id = models.IntegerField(db_column="rf_kl_SexID", default=0)
    rf_result_type_display_id = models.IntegerField(db_column="rf_ResultTypeDisplayID", default=0)
    rf_disp_question_type_id = models.IntegerField(db_column="rf_disp_QuestionTypeID", default=0)
    rf_mkbid = models.IntegerField(db_column="rf_MKBID", default=0)
    rf_question_guid = models.CharField(
        db_column="rf_QuestionGuid",
        max_length=36,
        default="00000000-0000-0000-0000-000000000000",
    )

    class Meta:
        managed = False
        db_table = "hlt_disp_ResultType"
