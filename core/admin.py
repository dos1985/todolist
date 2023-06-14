from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib import admin



class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'role', 'is_superuser')
    list_filter = ('role',)
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'role')}),
        ('Permissions', {'fields': ('is_superuser',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'role')}
        ),
    )

admin.site.unregister(Group)


# class CustomAdminSite(admin.AdminSite):
#     def each_context(self, request):
#         context = super().each_context(request)
#         context['admin_stylesheet'] = settings.STATIC_URL + 'admin.css'
#         return context
#
#
# admin_site = CustomAdminSite()
# admin_site.register(User, UserAdmin)
