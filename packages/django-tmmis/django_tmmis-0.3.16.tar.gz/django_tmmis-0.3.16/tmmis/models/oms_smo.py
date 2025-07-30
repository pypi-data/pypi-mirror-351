from .base_model import *


class OmsSmo(BaseModel):
    """
    Страховые медицинские организации (СМО)
    """

    id = models.AutoField(db_column="SMOID", primary_key=True)
    okato = models.ForeignKey("OmsOkato", models.DO_NOTHING, db_column="rf_OKATOID")
    q_ogrn = models.CharField(db_column="Q_OGRN", max_length=15)
    q_name = models.CharField(db_column="Q_NAME", max_length=150)
    fam_ruk = models.CharField(db_column="FAM_RUK", max_length=40)
    im_ruk = models.CharField(db_column="IM_RUK", max_length=40)
    ot_ruk = models.CharField(db_column="OT_RUK", max_length=40)
    fam_bux = models.CharField(db_column="FAM_BUX", max_length=40)
    im_bux = models.CharField(db_column="IM_BUX", max_length=40)
    ot_bux = models.CharField(db_column="OT_BUX", max_length=40)
    tel = models.CharField(db_column="TEL", max_length=40)
    fax = models.CharField(db_column="FAX", max_length=40)
    e_mail = models.CharField(db_column="E_MAIL", max_length=50)
    date_b = models.DateTimeField(db_column="DATE_B")
    date_e = models.DateTimeField(db_column="DATE_E")
    address = models.CharField(db_column="ADRES", max_length=200)
    post_idp = models.DecimalField(db_column="POST_IDP", max_digits=6, decimal_places=0)
    okpo = models.CharField(db_column="OKPO", max_length=8)
    cod = models.CharField(db_column="COD", max_length=6)
    organisation = models.ForeignKey("OmsOrganisation", models.DO_NOTHING, db_column="rf_OrganisationID")
    other_ter_flag = models.BooleanField(db_column="OtherTerFlag")
    code_cmo = models.IntegerField(db_column="Code_CMO")
    smo_cod = models.CharField(max_length=7, db_column="smocod")
    profit_type = models.ForeignKey("OmsKlProfitType", models.DO_NOTHING, db_column="rf_kl_ProfitTypeID")
    address_fact = models.CharField(db_column="ADRESF", max_length=200)
    inn = models.CharField(db_column="INN", max_length=17)
    kpp = models.DecimalField(db_column="KPP", max_digits=9, decimal_places=0)
    post_idpf = models.DecimalField(db_column="POST_IDPF", max_digits=6, decimal_places=0)
    q_namef = models.CharField(db_column="Q_NAMEF", max_length=255)
    rem = models.CharField(db_column="Rem", max_length=255)

    flags = models.IntegerField(db_column="FLAGS")

    class Meta:
        managed = False
        db_table = "oms_SMO"
