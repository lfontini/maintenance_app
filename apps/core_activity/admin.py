from django.contrib import admin
from .models import Core, Troubleshooting_registration
# Register your models here.


class CoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity_type', 'activity_related_to',
                    'status', 'pop', 'internet_id', 'start_date', 'end_date', 'Description', )
    search_fields = ('pop',)
    list_per_page = 100
    list_filter = ('pop',)
    ordering = ('start_date',)

    # permite editar o campo direto
    list_editable = ('activity_type', 'activity_related_to',
                     'status', 'pop', 'internet_id', 'start_date', 'end_date', 'Description', )


class Troubleshooting_registration_Admin(admin.ModelAdmin):
    list_display = ('core_quickbase_id', 'date', 'circuito',)


admin.site.register(Core, CoreAdmin)
admin.site.register(Troubleshooting_registration,
                    Troubleshooting_registration_Admin)
