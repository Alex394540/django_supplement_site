from django.contrib import admin

from .models import *

admin.site.register(Drug)
admin.site.register(DrugForm)
admin.site.register(Manufacturer)
admin.site.register(Category)
admin.site.register(Buying)
admin.site.register(Selling)
admin.site.register(SiteConfig)
admin.site.register(GlobalChecker)
admin.site.register(Order)
admin.site.register(NotSentMail)
admin.site.register(Notification)