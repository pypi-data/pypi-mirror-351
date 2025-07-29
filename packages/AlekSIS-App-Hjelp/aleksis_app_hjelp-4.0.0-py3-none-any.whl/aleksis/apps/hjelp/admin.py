from django.contrib import admin

from .models import IssueCategory


class IssueCategoryAdmin(admin.ModelAdmin):
    """ModelAdmin for issue categories."""

    list_display = ("name", "icon", "parent", "placeholder", "free_text")


admin.site.register(IssueCategory, IssueCategoryAdmin)
