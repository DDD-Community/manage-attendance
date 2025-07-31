from django.contrib import admin
from django.utils.html import format_html
from .models import InviteCode

class InviteCodeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'code',
        'created_by',
        'invite_type',
        'is_used_icon',
        'is_onetimeuse_icon',
        'expire_time',
        'is_valid_icon',
    )

    @admin.display(description='Created By')
    def created_by(self, obj):
        return obj.created_by

    @admin.display(description='Invite Type')
    def invite_type(self, obj):
        return obj.get_invite_type_display()

    @admin.display(description='Used')
    def is_used_icon(self, obj):
        return format_html(
            '<span style="color:{};">&#10004;</span>' if obj.used else '<span style="color:#ccc;">&#10008;</span>',
            'green'
        )

    @admin.display(description='One-Time Use')
    def is_onetimeuse_icon(self, obj):
        return format_html(
            '<span style="color:{};">&#10004;</span>' if obj.one_time_use else '<span style="color:#ccc;">&#10008;</span>',
            'blue'
        )

    @admin.display(description='Valid')
    def is_valid_icon(self, obj):
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        valid = not obj.used and (obj.expire_time is None or obj.expire_time > now)
        return format_html(
            '<span style="color:{};">&#10004;</span>' if valid else '<span style="color:#ccc;">&#10008;</span>',
            'green'
        )

admin.site.register(InviteCode, InviteCodeAdmin)
