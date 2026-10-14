from django.contrib import admin
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.admin import GroupAdmin
from django.contrib.contenttypes.models import ContentType
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


try:
    admin.site.unregister(Permission)
except admin.sites.NotRegistered:
    pass


try:
    admin.site.unregister(ContentType)
except admin.sites.NotRegistered:
    pass


try:
    admin.site.unregister(BlacklistedToken)
    admin.site.unregister(OutstandingToken)
except admin.sites.NotRegistered:
    pass


admin.site.site_header = "ArtHub Administration"
admin.site.site_title = "ArtHub Admin"
admin.site.index_title = "Добро пожаловать в панель управления ArtHub"