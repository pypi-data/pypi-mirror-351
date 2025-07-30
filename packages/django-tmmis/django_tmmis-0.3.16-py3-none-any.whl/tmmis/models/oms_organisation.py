from .base_model import *


class OmsOrganisation(BaseModel):
    """
    Организации
    """

    id = models.AutoField(db_column="OrganisationID", primary_key=True)
    uuid = models.CharField(db_column="GUIDOrg", max_length=36, default=uuid4)
    fullname = models.CharField(db_column="FullName", max_length=200)
    shortname = models.CharField(db_column="ShortName", max_length=80)
    inn = models.CharField(db_column="INN", max_length=17)
    kpp = models.CharField(db_column="KPP", max_length=14)
    r_account = models.CharField(db_column="R_Account", max_length=25)
    bank = models.CharField(db_column="Bank", max_length=150)
    bik_bank = models.CharField(db_column="BIK_Bank", max_length=14)
    c_account = models.CharField(db_column="C_Account", max_length=25)
    ogrn = models.CharField(db_column="OGRN", max_length=15)
    c_okpo = models.CharField(db_column="C_OKPO", max_length=15)
    okato = models.ForeignKey("OmsOkato", models.DO_NOTHING, db_column="rf_OKATOID")
    okved = models.ForeignKey("OmsOkved", models.DO_NOTHING, db_column="rf_OKVEDID")
    address = models.CharField(db_column="Address", max_length=200)
    phone = models.CharField(db_column="Phone", max_length=40)
    fax = models.CharField(db_column="Fax", max_length=40)
    email = models.CharField(db_column="Email", max_length=40)
    fio_ruk = models.CharField(db_column="FIO_RUK", max_length=100)
    fio_bux = models.CharField(db_column="FIO_BUX", max_length=100)
    date_b = models.DateTimeField(db_column="Date_B")
    date_e = models.DateTimeField(db_column="Date_E")
    parent = models.ForeignKey("self", models.DO_NOTHING, db_column="rf_OrganisationParentID")
    code = models.CharField(db_column="Code", max_length=15)
    address_p = models.CharField(db_column="AdresP", max_length=250)
    docum = models.CharField(db_column="Docum", max_length=150)
    dop = models.CharField(db_column="Dop", max_length=250)
    fio_ruk_r = models.CharField(db_column="FIO_RUK_R", max_length=100)
    post = models.CharField(db_column="Post", max_length=150)
    rem = models.CharField(db_column="Rem", max_length=250)
    kla_address = models.ForeignKey("KlaAddress", models.DO_NOTHING, db_column="rf_AddressID")

    flags = models.IntegerField(db_column="FLAGS")

    class Meta:
        managed = False
        db_table = "oms_Organisation"
