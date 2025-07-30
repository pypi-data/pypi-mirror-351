from .base_model import *


class OmsPrvs(models.Model):
    id = models.AutoField(db_column="PRVSID", primary_key=True)
    c_prvs = models.CharField(db_column="C_PRVS", max_length=100)
    prvs_name = models.CharField(db_column="PRVS_NAME", max_length=100)
    msg_text = models.CharField(db_column="MSG_TEXT", max_length=100)
    i_prvs = models.IntegerField(db_column="I_PRVS")
    date_beg = models.DateTimeField(db_column="Date_Beg")
    date_end = models.DateTimeField(db_column="Date_End")
    main_prvs = models.ForeignKey("self", db_column="rf_MainPRVSID", **FK_DEFAULT)
    prvs = models.ForeignKey("self", db_column="rf_PRVSID", **FK_DEFAULT)
    id_post_mz = models.CharField(db_column="IDPost_MZ", max_length=50)
    post_name = models.CharField(db_column="PostName", max_length=150)
    profit_type = models.ForeignKey("OmsKlProfitType", db_column="rf_kl_ProfitTypeID", **FK_DEFAULT)
    prvd = models.ForeignKey("OmsPrvd", db_column="rf_PRVDID", **FK_DEFAULT)

    class Meta:
        managed = False
        db_table = "oms_PRVS"
