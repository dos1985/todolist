from django.contrib import admin

from goals.models import GoalCategory, GoalComment


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated")
    search_fields = ("title", "user")


admin.site.register(GoalCategory, GoalCategoryAdmin)

class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ("goal", "user", "text", "created")
    search_fields = ("goal__title", "user__username", "text")


admin.site.register(GoalComment, GoalCommentAdmin)