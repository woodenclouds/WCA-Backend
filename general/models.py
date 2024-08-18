
from django.db import models
import uuid
from datetime import datetime, timedelta
from general.functions import *

class Mode(models.Model):
    readonly = models.BooleanField(default=False)
    maintenance = models.BooleanField(default=False)
    down = models.BooleanField(default=False)

    class Meta:
        db_table = "mode"
        verbose_name = "Mode"
        verbose_name_plural = "Mode"
        ordering = ("id",)

    def __str__(self):
        return str(self.id)


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auto_id = models.PositiveIntegerField(db_index=True, unique=True)
    creator = models.ForeignKey(
        "auth.User",
        related_name="creator_%(class)s_objects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    updater = models.ForeignKey(
        "auth.User",
        related_name="updater_%(class)s_objects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    date_added = models.DateTimeField(db_index=True, auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.auto_id:
            last_auto_id = self.__class__.objects.all().order_by('auto_id').last()
            if last_auto_id:
                self.auto_id = last_auto_id.auto_id + 1
            else:
                self.auto_id = 1
        super(BaseModel, self).save(*args, **kwargs)


class SlugBaseModel(models.Model):
    slug = models.SlugField(primary_key=True, max_length=128, blank=True)
    auto_id = models.PositiveIntegerField(db_index=True, unique=True)
    creator = models.ForeignKey(
        "auth.User",
        related_name="creator_%(class)s_objects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    updater = models.ForeignKey(
        "auth.User",
        related_name="updater_%(class)s_objects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    date_added = models.DateTimeField(db_index=True, auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True