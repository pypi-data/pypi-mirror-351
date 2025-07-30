from .base_model import *


class HltPolisMkab(BaseModel):
    """
    Полиса пациентов
    """

    id = models.AutoField(db_column="PolisMKABID", primary_key=True)
    date_pol_begin = models.DateTimeField(db_column="DatePolBegin")
    date_pol_end = models.DateTimeField(db_column="DatePolEnd")
    guid = models.CharField(db_column="GUID", max_length=36)
    is_active = models.BooleanField(db_column="isActive")
    s_pol = models.CharField(db_column="S_POL", max_length=50)
    n_pol = models.CharField(db_column="N_POL", max_length=50)
    profit_type = models.ForeignKey("OmsKlProfitType", db_column="rf_kl_ProfitTypeID", **FK_DEFAULT)
    tip_oms = models.ForeignKey("OmsKlTipOms", db_column="rf_kl_TipOMSID", **FK_DEFAULT)
    mkab = models.ForeignKey("HltMkab", db_column="rf_MKABID", **FK_DEFAULT)
    smo = models.ForeignKey("OmsLpu", db_column="rf_SMOID", **FK_DEFAULT)
    dogovor_id = models.IntegerField(db_column="rf_DOGOVORID")
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "hlt_polismkab"
