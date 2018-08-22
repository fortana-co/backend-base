from django.contrib import admin

from db.users.models import StaffUser, PublicUser


class StaffUserAdmin(admin.ModelAdmin):
    exclude = ('password',)
    readonly_fields = ('password',)


class UserAdmin(admin.ModelAdmin):
    exclude = ('set_password_token', 'password', 'is_active', 'last_login', 'set_password_token_created')
    readonly_fields = ('set_password_token', 'password')


admin.site.register(StaffUser, StaffUserAdmin)
admin.site.register(PublicUser, UserAdmin)
