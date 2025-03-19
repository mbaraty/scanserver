from django.contrib import admin

from scanapp.models import File


# Register your models here.
class FileAdmin(admin.ModelAdmin):
    list_display = ["date_created", "path", "hidden", "text_path"]

admin.site.register(File, FileAdmin)