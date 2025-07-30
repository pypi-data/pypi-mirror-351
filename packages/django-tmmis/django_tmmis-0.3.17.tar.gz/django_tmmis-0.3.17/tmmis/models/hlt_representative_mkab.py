from .base_model import *


class HltRepresentativeMkab(BaseModel):
    """
    Представители пациента
    """

    id = models.AutoField(db_column="RepresentativeMKABID", primary_key=True)
    guid = models.CharField(db_column="GUID", max_length=36)
    address_live_str = models.CharField(db_column="AddressLive", max_length=200)
    address_reg_str = models.CharField(db_column="AddressReg", max_length=200)
    bd = models.DateTimeField(db_column="BD")
    birth_place = models.CharField(db_column="Birthplace", max_length=200)
    family = models.CharField(db_column="FAMILY", max_length=40)
    flags = models.IntegerField(db_column="Flags")
    is_main = models.BooleanField(db_column="isMain")
    is_no_ot = models.BooleanField(db_column="isNoOT")
    n_pol = models.CharField(db_column="N_POL", max_length=50)
    name = models.CharField(db_column="NAME", max_length=40)
    ot = models.CharField(db_column="OT", max_length=40)
    other_contact_inf = models.CharField(db_column="OtherContactInf", max_length=255)
    phone = models.CharField(db_column="Phone", max_length=25)
    post = models.CharField(db_column="Post", max_length=255)
    address_live = models.ForeignKey("KlaAddress", **FK_DEFAULT, db_column="rf_AddressLiveID")
    address_reg = models.ForeignKey("KlaAddress", **FK_DEFAULT, db_column="rf_AddressRegID")
    sex_id = models.IntegerField(db_column="rf_kl_SexID")
    tip_oms = models.ForeignKey("OmsKlTipOms", **FK_DEFAULT, db_column="rf_kl_TipOMSID")
    mkab = models.ForeignKey("HltMkab", **FK_DEFAULT, db_column="rf_MKABID")
    not_work_doc_care_id = models.IntegerField(db_column="rf_NotWorkDocCareID")
    patient_mkab = models.ForeignKey("HltMkab", **FK_DEFAULT, db_column="rf_PatientMKABID")
    smo = models.ForeignKey("OmsSmo", **FK_DEFAULT, db_column="rf_SMOID")
    s_pol = models.CharField(db_column="S_POL", max_length=50)
    work = models.CharField(db_column="Work", max_length=200)
    ss = models.CharField(db_column="SS", max_length=14)
    date_doc = models.DateTimeField(db_column="DateDoc")
    doc_issued_by = models.CharField(db_column="DocIssuedBy", max_length=255)
    n_doc = models.CharField(db_column="N_Doc", max_length=15)
    type_doc = models.IntegerField(db_column="rf_TypeDocID")
    s_doc = models.CharField(db_column="S_Doc", max_length=10)
    is_legal_org = models.BooleanField(db_column="isLegalOrg")
    address_org = models.ForeignKey("KlaAddress", **FK_DEFAULT, db_column="rf_AddressOrgID")
    name_org = models.CharField(db_column="NameOrg", max_length=255)
    ogrn_org = models.CharField(db_column="OgrnOrg", max_length=15)
    s_doc_representative = models.CharField(db_column="S_DocRepresentative", max_length=50)
    n_doc_representative = models.CharField(db_column="N_DocRepresentative", max_length=50)
    type_doc_representative_id = models.IntegerField(db_column="rf_TypeDocRepresentativeID")
    date_doc_representative = models.DateTimeField(db_column="DateDocRepresentative")
    doc_representative_by = models.CharField(db_column="DocRepresentativeBy", max_length=255)
    inn = models.CharField(db_column="INN", max_length=12)
    spec_event_cert = models.IntegerField(db_column="rf_SpecEventCertID")
    patient = models.IntegerField(db_column="rf_PatientID")
    oksm = models.IntegerField(db_column="rf_OKSMID")
    vedom = models.IntegerField(db_column="rf_kl_VedomID")

    class Meta:
        managed = False
        db_table = "hlt_RepresentativeMKAB"
