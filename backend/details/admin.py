from details.models import Detail, DetailInStock, PlannedDetail, WareHouse
from django.contrib import admin


class DetailAdmin(admin.ModelAdmin):
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


class PlannedDetailAdmin(admin.ModelAdmin):
    search_fields = ['detail']


class DetailInStockAdmin(admin.ModelAdmin):
    search_fields = ['detail', 'warehouse']


class WareHouseAdmin(admin.ModelAdmin):
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(Detail, DetailAdmin)
admin.site.register(PlannedDetail, PlannedDetailAdmin)
admin.site.register(DetailInStock, DetailInStockAdmin)
admin.site.register(WareHouse, WareHouseAdmin)
