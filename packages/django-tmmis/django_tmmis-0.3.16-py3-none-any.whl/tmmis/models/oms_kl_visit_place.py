"""
Модель OmsKlVisitPlace - Место оказания медицинской помощи

Эта модель работает с таблицей oms_kl_VisitPlace, которая может иметь разную структуру
в различных базах данных. В некоторых базах отсутствуют поля CodeEGISZ и NameEGISZ.

Для управления совместимостью используйте настройку в settings.py:
TMMIS_OMS_KL_VISIT_PLACE_HAS_EGISZ_FIELDS = True/False

Примеры использования:

1. В settings.py вашего проекта:
   # Для баз с полями ЕГИСЗ
   TMMIS_OMS_KL_VISIT_PLACE_HAS_EGISZ_FIELDS = True

   # Для баз без полей ЕГИСЗ
   TMMIS_OMS_KL_VISIT_PLACE_HAS_EGISZ_FIELDS = False

2. Использование в коде (одинаково для всех версий):
   place = OmsKlVisitPlace.objects.get(id=1)
   print(place.code_egisz)  # Всегда работает

3. Фильтрация:
   places = OmsKlVisitPlace.objects.filter(code_egisz="123")  # Работает!
"""

from django.conf import settings

from .base_model import *


class OmsKlVisitPlace(BaseModel):
    id = models.AutoField(db_column="kl_VisitPlaceID", primary_key=True)
    code = models.CharField(db_column="Code", max_length=50, default="не определено")
    name = models.CharField(db_column="Name", max_length=255, default="не определено")
    date_b = models.DateTimeField(db_column="Date_B", default="1900-01-01")
    date_e = models.DateTimeField(db_column="Date_E", default="2222-01-01")

    # Поля ЕГИСЗ - добавляются условно в зависимости от настроек
    is_tap = models.BooleanField(db_column="IsTAP", default=False)
    guid = models.CharField(db_column="VisitPlaceGUID", max_length=36, default=uuid4)

    class Meta:
        managed = False
        db_table = "oms_kl_VisitPlace"


# Условное добавление полей ЕГИСЗ в зависимости от настроек
if getattr(settings, "TMMIS_OMS_KL_VISIT_PLACE_HAS_EGISZ_FIELDS", False):
    # Добавляем поля ЕГИСЗ динамически
    OmsKlVisitPlace.add_to_class("code_egisz", models.CharField(db_column="CodeEGISZ", max_length=50, default=""))
    OmsKlVisitPlace.add_to_class("name_egisz", models.CharField(db_column="NameEGISZ", max_length=255, default=""))
else:
    # Добавляем заглушки для совместимости
    def _get_empty_egisz_field(self):
        return ""

    OmsKlVisitPlace.code_egisz = property(_get_empty_egisz_field)
    OmsKlVisitPlace.name_egisz = property(_get_empty_egisz_field)
