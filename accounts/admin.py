from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Liste görünümünde gösterilecek alanlar
    list_display = [
        'username', 
        'email', 
        'role', 
        'is_manager', 
        'is_approved', 
        'is_active_user',
        'date_joined'
    ]
    
    # Filtreleme seçenekleri
    list_filter = [
        'role', 
        'is_manager', 
        'is_approved', 
        'is_active_user',
        'is_staff',
        'is_superuser'
    ]
    
    # Arama alanları
    search_fields = [
        'username', 
        'email', 
        'first_name', 
        'last_name',
        'company_name',
        'pharmacy_name'
    ]
    
    # Detay sayfasında gösterilecek alanlar (DÜZENLEME)
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('username', 'password', 'email', 'first_name', 'last_name')
        }),
        ('Rol ve Yetkiler', {
            'fields': (
                'role', 
                'is_manager', 
                'is_approved', 
                'is_active_user',
                'approved_by',
                'manager',
                'invited_by'
            )
        }),
        ('Sistem Yetkileri', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Firma Bilgileri', {
            'fields': (
                'company_name',
                'company_tax_number',
                'company_tax_office',
                'company_phone',
                'company_mobile',
                'company_address',
                'company_responsible_person',
                'company_responsible_email'
            ),
            'classes': ('collapse',)  # Başlangıçta kapalı
        }),
        ('Eczane Bilgileri', {
            'fields': (
                'pharmacy_name',
                'pharmacist_name',
                'pharmacy_tax_number',
                'pharmacy_tax_office',
                'pharmacy_phone',
                'pharmacy_mobile',
                'pharmacy_email',
                'pharmacy_address',
                'pharmacy_license_number'
            ),
            'classes': ('collapse',)  # Başlangıçta kapalı
        }),
        ('Firma Yetkileri', {
            'fields': (
                'can_create_offer',
                'can_edit_own_offer',
                'can_revise_offer',  # YENİ
                'can_edit_all_offers',
                'can_delete_own_offer',
                'can_delete_all_offers',
                'can_send_offer',
                'can_view_all_offers',
                'can_approve_high_value_offers',
                'can_invite_staff',
                'can_manage_staff_permissions',
                'can_activate_deactivate_staff',
                'can_promote_to_manager',
                'can_view_reports',
                'can_view_financial_data',
                'can_export_data'
            ),
            'classes': ('collapse',)
        }),
        ('Eczane Yetkileri', {
            'fields': (
                'can_approve_pharmacy_offers',
                'can_reject_pharmacy_offers',
                'can_approve_high_value_pharmacy_offers',
                'can_apply_discount',
                'can_apply_high_discount',
                'can_enter_invoice',
                'can_approve_invoice_revision',
                'can_edit_invoice',
                'can_approve_pharmacy_staff',
                'can_manage_pharmacy_staff',
                'can_update_product_prices'
            ),
            'classes': ('collapse',)
        }),
        ('Tarihler', {
            'fields': ('date_joined', 'last_login')
        }),
    )
    
    # Yeni kullanıcı ekleme formu (EKLEME)
    add_fieldsets = (
        ('Temel Bilgiler', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
        }),
        ('Rol ve Yetkiler', {
            'classes': ('wide',),
            'fields': ('role', 'is_manager', 'is_approved', 'is_active_user')
        }),
        ('Firma Bilgileri (Sadece Firma için)', {
            'classes': ('wide', 'collapse'),
            'fields': (
                'company_name',
                'company_tax_number',
                'company_tax_office',
                'company_phone',
                'company_mobile',
                'company_address',
                'company_responsible_person',
                'company_responsible_email'
            )
        }),
        ('Eczane Bilgileri (Sadece Eczane için)', {
            'classes': ('wide', 'collapse'),
            'fields': (
                'pharmacy_name',
                'pharmacist_name',
                'pharmacy_tax_number',
                'pharmacy_tax_office',
                'pharmacy_phone',
                'pharmacy_mobile',
                'pharmacy_email',
                'pharmacy_address',
                'pharmacy_license_number'
            )
        }),
        ('Firma Yetkileri (Sadece Firma için)', {
            'classes': ('wide', 'collapse'),
            'fields': (
                'can_create_offer',
                'can_edit_own_offer',
                'can_revise_offer',  # BUNU EKLEYIN (can_edit_own_offer'dan sonra)
                'can_revise_offer',  # YENİ
                'can_edit_all_offers',
                'can_delete_own_offer',
                'can_delete_all_offers',
                'can_send_offer',
                'can_view_all_offers',
                'can_approve_high_value_offers',
                'can_invite_staff',
                'can_manage_staff_permissions',
                'can_activate_deactivate_staff',
                'can_promote_to_manager',
                'can_view_reports',
                'can_view_financial_data',
                'can_export_data'
            )
        }),
        ('Eczane Yetkileri (Sadece Eczane için)', {
            'classes': ('wide', 'collapse'),
            'fields': (
                'can_approve_pharmacy_offers',
                'can_reject_pharmacy_offers',
                'can_approve_high_value_pharmacy_offers',
                'can_apply_discount',
                'can_apply_high_discount',
                'can_enter_invoice',
                'can_approve_invoice_revision',
                'can_edit_invoice',
                'can_approve_pharmacy_staff',
                'can_manage_pharmacy_staff',
                'can_update_product_prices'
            )
        }),
    )
    
    # Salt okunur alanlar
    readonly_fields = ('date_joined', 'last_login')
    
    # Düzenleme yapılabilir alanlar (liste görünümünde)
    list_editable = ['is_approved', 'is_active_user']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'address_type', 'city', 'is_default', 'is_active']
    list_filter = ['address_type', 'is_default', 'is_active', 'city']
    search_fields = ['title', 'user__username', 'user__company_name', 'address_line', 'city']
    list_editable = ['is_default', 'is_active']
    
    fieldsets = (
        ('Kullanıcı', {
            'fields': ('user',)
        }),
        ('Adres Bilgileri', {
            'fields': ('title', 'address_type', 'address_line', 'city', 'district', 'postal_code')
        }),
        ('İletişim Bilgileri', {
            'fields': ('contact_person', 'phone', 'email')
        }),
        ('Ek Bilgiler', {
            'fields': ('notes', 'is_default', 'is_active')
        }),
    )