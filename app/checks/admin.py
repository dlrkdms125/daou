
from django.contrib import admin
from .models import CheckRecord, PersonalLink

@admin.register(CheckRecord)
class CheckRecordAdmin(admin.ModelAdmin):
    list_display = ("date","time","item","server","user","ip","appeal_done","status")
    search_fields = ("user","server","item","ip")

@admin.register(PersonalLink)
class PersonalLinkAdmin(admin.ModelAdmin):
    list_display = ("uuid","user_key")
    search_fields = ("user_key",)
