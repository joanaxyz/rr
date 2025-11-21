from django.contrib import admin
from django.utils.html import format_html
from .models import OwnerVerificationRequest


class OwnerVerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'state', 'created_at')
    list_filter = ('state', 'created_at')
    search_fields = ('user__username', 'user__email', 'govt_full_name')
    readonly_fields = (
        'government_id_front_display',
        'government_id_back_display',
        'business_license_display',
        'proof_of_ownership_display',
        'created_at',
        'updated_at',
    )
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Government ID', {
            'fields': ('govt_full_name', 'government_id_type', 'government_id_number')
        }),
        ('Business Information', {
            'fields': ('business_address', 'business_email', 'tax_id')
        }),
        ('Documents', {
            'fields': (
                'government_id_front_display',
                'government_id_back_display',
                'business_license_display',
                'proof_of_ownership_display',
            )
        }),
        ('Status', {
            'fields': ('state',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def government_id_front_display(self, obj):
        if obj.government_id_front:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 300px; max-height: 300px;" /></a>',
                obj.government_id_front,
                obj.government_id_front
            )
        return 'No image'
    government_id_front_display.short_description = 'Government ID Front'

    def government_id_back_display(self, obj):
        if obj.government_id_back:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 300px; max-height: 300px;" /></a>',
                obj.government_id_back,
                obj.government_id_back
            )
        return 'No image'
    government_id_back_display.short_description = 'Government ID Back'

    def business_license_display(self, obj):
        if obj.business_license:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 300px; max-height: 300px;" /></a>',
                obj.business_license,
                obj.business_license
            )
        return 'No image'
    business_license_display.short_description = 'Business License'

    def proof_of_ownership_display(self, obj):
        if obj.proof_of_ownership:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 300px; max-height: 300px;" /></a>',
                obj.proof_of_ownership,
                obj.proof_of_ownership
            )
        return 'No image'
    proof_of_ownership_display.short_description = 'Proof of Ownership'


admin.site.register(OwnerVerificationRequest, OwnerVerificationRequestAdmin)