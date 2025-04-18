from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(BitaBoxUtilisateur)
admin.site.register(BitaBoxEntreprise)
admin.site.register(BitaBoxLead)
admin.site.register(BitaBoxNotification)
admin.site.register(BitaBoxNotification)

admin.site.site_header = "Admin BitaBox"
admin.site.site_title = "Dashboard BitaBox"
admin.site.index_title = "Welcome on Dashboard"