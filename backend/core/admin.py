from django.contrib import admin
from . import models as m

# Register your models here.
admin.site.register(m.Customer)
admin.site.register(m.FileEntry)
admin.site.register(m.Consumer)
admin.site.register(m.Payment)
