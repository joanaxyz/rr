from django.contrib import admin
from .models import User, Admin, Customer

# Register your models here.
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Customer)