from django.contrib import admin
from .models import CustomUser
from .models import UserSubscription
from .models import Advertisement
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserSubscription)
admin.site.register(Advertisement)
