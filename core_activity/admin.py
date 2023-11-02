from django.contrib import admin
from .models import Core, Core_registration
# Register your models here.


class CoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity_type', 'activity_related_to',
                    'status', 'pop', 'internet_id', 'start_date', 'end_date', 'Description', )
    search_fields = ('pop',)
    list_per_page = 100
    list_filter = ('pop',)
    ordering = ('start_date',)

    # permite editar o campo direto
    # list_editable = ('foto',)


class Core_registration_Admin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Core, CoreAdmin)
admin.site.register(Core_registration, Core_registration_Admin)
