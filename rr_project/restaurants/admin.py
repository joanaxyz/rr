from django.contrib import admin
from .models import *
from django import forms
from owner_verification.supabase_utils import upload_to_supabase
import uuid

class RestaurantAdminForm(forms.ModelForm):
    image_file = forms.ImageField(required=False, label="Restaurant Image")
    
    class Meta:
        model = Restaurant
        fields = '__all__'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.cleaned_data.get('image_file'):
            image_file = self.cleaned_data['image_file']
            file_path = f"restaurants/{uuid.uuid4()}_{image_file.name}"
            image_url = upload_to_supabase(image_file, "files", file_path)
            if image_url:
                instance.image = image_url
        
        if commit:
            instance.save()
        return instance

class RestaurantAdmin(admin.ModelAdmin):
    form = RestaurantAdminForm
    list_display = ['name', 'email', 'phone_number', 'owner', 'created_at']
    search_fields = ['name', 'email']

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Table)
admin.site.register(Element)
admin.site.register(Tags)
admin.site.register(Review)
