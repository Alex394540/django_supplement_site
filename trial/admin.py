from django.contrib import admin

from .models import Drug, DrugForm, Manufacturer, Category, Buying, Selling

admin.site.register(Drug)
admin.site.register(DrugForm)
admin.site.register(Manufacturer)
admin.site.register(Category)
admin.site.register(Buying)
admin.site.register(Selling)