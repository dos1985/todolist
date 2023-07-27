from django.contrib import admin
from bot.models import TgUser

class TgUserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "related_user", "created", "updated")
    search_fields = ("user_id", "related_user__username")

admin.site.register(TgUser, TgUserAdmin)
