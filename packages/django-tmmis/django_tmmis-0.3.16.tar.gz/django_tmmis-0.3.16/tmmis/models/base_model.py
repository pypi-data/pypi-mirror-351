# noinspection PyUnresolvedReferences
from uuid import UUID, uuid4

from django.db import models

# noinspection PyUnresolvedReferences
from django.utils import timezone

FK_DEFAULT = {"on_delete": models.DO_NOTHING, "related_name": "+", "default": 0}
NULL = {"blank": True, "null": True}


class BaseModel(models.Model):
    x_edition = models.IntegerField(db_column="x_Edition", default=1)
    x_status = models.SmallIntegerField(db_column="x_Status", default=1)

    class Meta:
        abstract = True
