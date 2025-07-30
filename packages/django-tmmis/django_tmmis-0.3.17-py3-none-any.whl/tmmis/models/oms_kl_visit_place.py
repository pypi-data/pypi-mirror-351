"""
Модель OmsKlVisitPlace - Место оказания медицинской помощи

Эта модель работает с таблицей oms_kl_VisitPlace, которая может иметь разную структуру
в различных базах данных. В некоторых базах отсутствуют поля ЕГИСЗ:
- CodeEGISZ, NameEGISZ - коды и названия ЕГИСЗ
- IsTAP, VisitPlaceGUID - дополнительные поля ЕГИСЗ

Для управления совместимостью используйте настройку в settings.py:
TMMIS_OMS_KL_VISIT_PLACE_HAS_EGISZ_FIELDS = True/False

Примеры использования:

1. В settings.py вашего проекта:
   # Для баз с полями ЕГИСЗ (новые базы)
   TMMIS_OMS_KL_VISIT_PLACE_HAS_EGISZ_FIELDS = True

   # Для баз без полей ЕГИСЗ (старые базы)
   TMMIS_OMS_KL_VISIT_PLACE_HAS_EGISZ_FIELDS = False

2. Использование в коде (одинаково для всех версий):
   place = OmsKlVisitPlace.objects.get(id=1)
   print(place.code_egisz)  # Всегда работает
   print(place.is_tap)      # Всегда работает

3. Фильтрация:
   places = OmsKlVisitPlace.objects.filter(code_egisz="123")  # Работает!
   places = OmsKlVisitPlace.objects.filter(is_tap=True)       # Работает!
"""

from django.conf import settings

from .base_model import *


class OmsKlVisitPlace(BaseModel):
    id = models.AutoField(db_column="kl_VisitPlaceID", primary_key=True)
    code = models.CharField(db_column="Code", max_length=50, default="не определено")
    name = models.CharField(db_column="Name", max_length=255, default="не определено")
    date_b = models.DateTimeField(db_column="Date_B", default="1900-01-01")
    date_e = models.DateTimeField(db_column="Date_E", default="2222-01-01")

    class Meta:
        managed = False
        db_table = "oms_kl_VisitPlace"


# Условное добавление полей ЕГИСЗ в зависимости от настроек
if getattr(settings, "TMMIS_OMS_KL_VISIT_PLACE_HAS_EGISZ_FIELDS", False):
    # Добавляем все поля ЕГИСЗ динамически
    OmsKlVisitPlace.add_to_class("code_egisz", models.CharField(db_column="CodeEGISZ", max_length=50, default=""))
    OmsKlVisitPlace.add_to_class("name_egisz", models.CharField(db_column="NameEGISZ", max_length=255, default=""))
    OmsKlVisitPlace.add_to_class("is_tap", models.BooleanField(db_column="IsTAP", default=False))
    OmsKlVisitPlace.add_to_class("guid", models.CharField(db_column="VisitPlaceGUID", max_length=36, default=uuid4))
else:
    # Добавляем заглушки для совместимости
    def _get_empty_string_field(self):
        return ""

    def _get_false_boolean_field(self):
        return False

    def _get_empty_guid_field(self):
        return "00000000-0000-0000-0000-000000000000"

    OmsKlVisitPlace.code_egisz = property(_get_empty_string_field)
    OmsKlVisitPlace.name_egisz = property(_get_empty_string_field)
    OmsKlVisitPlace.is_tap = property(_get_false_boolean_field)
    OmsKlVisitPlace.guid = property(_get_empty_guid_field)
