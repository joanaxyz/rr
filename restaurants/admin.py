from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from .models import *
from django import forms
from owner_verification.supabase_utils import upload_to_supabase
import uuid
import json

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

class RestaurantCreationRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'status', 'created_at', 'action_buttons']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'user__username', 'user__email', 'email']
    readonly_fields = ['user', 'name', 'email', 'phone_number', 'description', 
                      'street_number', 'street_name', 'street_block', 'city', 'postal_code',
                      'price_min', 'price_max', 'max_guest_count', 'opening_time', 'closing_time',
                      'operating_days', 'image', 'proof_of_ownership', 'custom_tags', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'status', 'created_at', 'updated_at', 'admin_notes')
        }),
        ('Restaurant Details', {
            'fields': ('name', 'email', 'phone_number', 'description', 'image')
        }),
        ('Address', {
            'fields': ('street_number', 'street_name', 'street_block', 'city', 'postal_code')
        }),
        ('Operating Information', {
            'fields': ('opening_time', 'closing_time', 'operating_days', 'max_guest_count')
        }),
        ('Pricing', {
            'fields': ('price_min', 'price_max')
        }),
        ('Tags', {
            'fields': ('custom_tags',)
        }),
        ('Proof of Ownership', {
            'fields': ('proof_of_ownership',)
        }),
    )
    
    def action_buttons(self, obj):
        if obj.status == 'PENDING':
            return format_html(
                '<a class="button" href="{}" style="background-color: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px;">Accept</a>'
                '<a class="button" href="{}" style="background-color: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Reject</a>',
                f'/admin/restaurants/restaurantcreationrequest/{obj.id}/accept/',
                f'/admin/restaurants/restaurantcreationrequest/{obj.id}/reject/'
            )
        return obj.get_status_display()
    action_buttons.short_description = 'Actions'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:request_id>/accept/', self.accept_request, name='restaurantcreationrequest_accept'),
            path('<int:request_id>/reject/', self.reject_request, name='restaurantcreationrequest_reject'),
        ]
        return custom_urls + urls
    
    def accept_request(self, request, request_id):
        """Accept the restaurant creation request and create the restaurant"""
        restaurant_request = RestaurantCreationRequest.objects.get(id=request_id)
        
        if restaurant_request.status != 'PENDING':
            messages.error(request, 'This request has already been processed.')
            return redirect('admin:restaurants_restaurantcreationrequest_changelist')
        
        try:
            # Get the owner
            from accounts.models import Owner
            owner, _ = Owner.objects.get_or_create(user=restaurant_request.user)
            
            # Create the restaurant
            restaurant = Restaurant.objects.create(
                name=restaurant_request.name,
                email=restaurant_request.email,
                phone_number=restaurant_request.phone_number,
                description=restaurant_request.description,
                street_number=restaurant_request.street_number,
                street_name=restaurant_request.street_name,
                street_block=restaurant_request.street_block,
                city=restaurant_request.city,
                postal_code=restaurant_request.postal_code,
                price_min=restaurant_request.price_min,
                price_max=restaurant_request.price_max,
                max_guest_count=restaurant_request.max_guest_count,
                opening_time=restaurant_request.opening_time,
                closing_time=restaurant_request.closing_time,
                operating_days=restaurant_request.operating_days,
                image=restaurant_request.image,
                owner=owner
            )
            
            # Handle cuisines and tags from admin_notes (stored as JSON)
            if restaurant_request.admin_notes:
                try:
                    data = json.loads(restaurant_request.admin_notes)
                    cuisine_ids = data.get('cuisine_ids', [])
                    tag_ids = data.get('tag_ids', [])
                    
                    if cuisine_ids:
                        cuisines = Cuisine.objects.filter(id__in=cuisine_ids)
                        restaurant.cuisines.set(cuisines)
                    
                    if tag_ids:
                        tags = Tags.objects.filter(id__in=tag_ids)
                        restaurant.tags.set(tags)
                except:
                    pass
            
            # Handle custom tags
            if restaurant_request.custom_tags:
                custom_tags_list = [tag.strip() for tag in restaurant_request.custom_tags.split(',') if tag.strip()]
                for tag_name in custom_tags_list:
                    tag, created = Tags.objects.get_or_create(tag=tag_name)
                    restaurant.tags.add(tag)
            
            # Update request status
            restaurant_request.status = 'ACCEPTED'
            restaurant_request.admin_notes = f"Restaurant created with ID: {restaurant.id}"
            restaurant_request.save()
            
            messages.success(request, f'Restaurant "{restaurant.name}" has been created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating restaurant: {str(e)}')
        
        return redirect('admin:restaurants_restaurantcreationrequest_changelist')
    
    def reject_request(self, request, request_id):
        """Reject the restaurant creation request"""
        restaurant_request = RestaurantCreationRequest.objects.get(id=request_id)
        
        if restaurant_request.status != 'PENDING':
            messages.error(request, 'This request has already been processed.')
            return redirect('admin:restaurants_restaurantcreationrequest_changelist')
        
        if request.method == 'POST':
            admin_notes = request.POST.get('admin_notes', '')
            restaurant_request.status = 'REJECTED'
            restaurant_request.admin_notes = admin_notes
            restaurant_request.save()
            messages.success(request, f'Restaurant request "{restaurant_request.name}" has been rejected.')
            return redirect('admin:restaurants_restaurantcreationrequest_changelist')
        
        # Show rejection form
        from django.template.response import TemplateResponse
        context = {
            'restaurant_request': restaurant_request,
            'opts': self.model._meta,
            'has_view_permission': True,
            'has_add_permission': False,
            'has_change_permission': True,
            'has_delete_permission': False,
        }
        return TemplateResponse(request, 'admin/restaurants/restaurantcreationrequest/reject_form.html', context)

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Table)
admin.site.register(Element)
admin.site.register(Tags)
admin.site.register(Review)
admin.site.register(RestaurantCreationRequest, RestaurantCreationRequestAdmin)
