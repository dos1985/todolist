from django.contrib import admin
from django.db import transaction

from goals.models import GoalCategory, GoalComment, Goal, Board


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated")
    search_fields = ("title", "user")


admin.site.register(GoalCategory, GoalCategoryAdmin)

class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ("goal", "user", "text", "created")
    search_fields = ("goal__title", "user__username", "text")


admin.site.register(GoalComment, GoalCommentAdmin)

class BoardAdmin(admin.ModelAdmin):
    list_display = ("title", "created", "updated", "is_deleted")
    search_fields = ("title",)


admin.site.register(Board, BoardAdmin)

class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "description", "is_deleted")
    search_fields = ("title", "user__username", "description")


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs.filter(is_deleted=False)
    #
    # def delete_model(self, request, obj):
    #     with transaction.atomic():
    #         # Удаление всех связанных комментариев
    #         GoalComment.objects.filter(goal=obj).delete()
    #         # Помечаем цель как удаленную
    #         obj.is_deleted = True
    #         obj.save()



admin.site.register(Goal, GoalAdmin)