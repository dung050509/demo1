from django.contrib import admin
from teatwitter.teacrawler.models import KOLMaster


@admin.register(KOLMaster)
class KOLMasterAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]
