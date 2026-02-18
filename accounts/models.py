from django.contrib.auth.models import AbstractUser
from django.db import models

"""
Bu kodu accounts/models.py dosyasına ekleyin
User modelinden ÖNCE tanımlayın
"""

class Address(models.Model):
    """Firma adresleri - birden fazla yerleşke"""
    
    ADDRESS_TYPES = [
        ('headquarter', 'Merkez'),
        ('branch', 'Şube'),
        ('warehouse', 'Depo'),
        ('other', 'Diğer'),
    ]
    
    user = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        related_name='addresses',
        verbose_name='Firma'
    )
    
    # Adres bilgileri
    title = models.CharField(max_length=200, verbose_name='Adres Başlığı')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPES, default='branch', verbose_name='Adres Tipi')
    address_line = models.TextField(verbose_name='Adres')
    city = models.CharField(max_length=100, verbose_name='İl')
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name='İlçe')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='Posta Kodu')
    
    # İletişim bilgileri
    contact_person = models.CharField(max_length=200, blank=True, null=True, verbose_name='İletişim Kişisi')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefon')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    
    # Ek bilgiler
    notes = models.TextField(blank=True, null=True, verbose_name='Notlar')
    is_default = models.BooleanField(default=False, verbose_name='Varsayılan Adres')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Adres'
        verbose_name_plural = 'Adresler'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_address_type_display()})"
    
    def save(self, *args, **kwargs):
        # Eğer bu adres varsayılan yapılıyorsa, diğerlerini kaldır
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        
        # Eğer kullanıcının hiç adresi yoksa, ilk adres otomatik varsayılan olsun
        if not self.pk and not Address.objects.filter(user=self.user).exists():
            self.is_default = True
        
        super().save(*args, **kwargs)


class User(AbstractUser):
    ROLE_CHOICES = (
        ("eczane", "Eczane"),
        ("firma", "Firma"),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="firma",
    )

    is_approved = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=True)
    
    # Kullanıcıyı onaylayan kişi
    approved_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_users',
        verbose_name="Onaylayan",
        help_text="Bu kullanıcıyı kim onayladı?"
    )
    
    # Aktiflik durumu (sadece admin değiştirebilir)
    is_active_user = models.BooleanField(
        default=True,
        verbose_name="Aktif mi?",
        help_text="Pasif kullanıcılar sisteme giremez"
    )
    
    # Davetiye sistemi için
    invitation_token = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Davetiye Token",
        help_text="Personel kaydı için özel token"
    )
    
    invitation_expires = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Davetiye Geçerlilik",
        help_text="Davetiye linkinin son kullanma tarihi"
    )
    
    invited_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_users',
        verbose_name="Davet Eden",
        help_text="Bu personeli kim davet etti?"
    )

    # ===========================
    # FİRMA PROFİL BİLGİLERİ
    # ===========================
    company_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Firma Tam Ünvanı"
    )
    company_tax_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Vergi No"
    )
    company_tax_office = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Vergi Dairesi"
    )
    company_address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Firma Adresi"
    )
    company_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Sabit Telefon"
    )
    company_mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Mobil Telefon"
    )
    company_responsible_person = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Yetkili Kişi"
    )
    company_responsible_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Yetkili Email"
    )

    # ===========================
    # ECZANE PROFİL BİLGİLERİ
    # ===========================
    pharmacy_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Eczane Adı"
    )
    pharmacist_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Eczacı Adı Soyadı"
    )
    pharmacy_tax_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Vergi No"
    )
    pharmacy_tax_office = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Vergi Dairesi"
    )
    pharmacy_address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Eczane Adresi"
    )
    pharmacy_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Sabit Telefon"
    )
    pharmacy_mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Mobil Telefon"
    )
    pharmacy_license_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Ruhsat No"
    )
    pharmacy_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Eczane Email",
        help_text="Personel bu email ile kayıt olabilir"
    )

    # ===========================
    # YETKİLENDİRME SİSTEMİ
    # ===========================
    is_manager = models.BooleanField(
        default=False,
        verbose_name="Yönetici mi?",
        help_text="Firma için: Firma Yöneticisi | Eczane için: Eczacı"
    )
    
    # ===== FİRMA YETKİLERİ =====
    # Teklif İşlemleri
    can_create_offer = models.BooleanField(default=True, verbose_name="Teklif oluşturabilir")
    can_revise_offer = models.BooleanField(default=False,verbose_name="Teklif Revize Edebilir")
    can_edit_own_offer = models.BooleanField(default=True, verbose_name="Kendi tekliflerini düzenleyebilir")
    can_edit_all_offers = models.BooleanField(default=False, verbose_name="Tüm teklifleri düzenleyebilir")
    can_delete_own_offer = models.BooleanField(default=True, verbose_name="Kendi tekliflerini silebilir")
    can_delete_all_offers = models.BooleanField(default=False, verbose_name="Tüm teklifleri silebilir")
    can_send_offer = models.BooleanField(default=True, verbose_name="Teklif gönderebilir")
    can_view_all_offers = models.BooleanField(default=False, verbose_name="Tüm teklifleri görebilir")
    can_approve_high_value_offers = models.BooleanField(default=False, verbose_name="50K+ teklifleri onaylayabilir")
    
    # Personel Yönetimi (sadece yöneticiler)
    can_invite_staff = models.BooleanField(default=False, verbose_name="Personel davet edebilir")
    can_manage_staff_permissions = models.BooleanField(default=False, verbose_name="Personel yetkilerini düzenleyebilir")
    can_activate_deactivate_staff = models.BooleanField(default=False, verbose_name="Personeli aktif/pasif yapabilir")
    can_promote_to_manager = models.BooleanField(default=False, verbose_name="Personeli yönetici yapabilir")
    
    # Raporlar ve Analiz
    can_view_reports = models.BooleanField(default=False, verbose_name="Raporları görebilir")
    can_view_financial_data = models.BooleanField(default=False, verbose_name="Finansal verileri görebilir")
    can_export_data = models.BooleanField(default=False, verbose_name="Veri dışa aktarabilir")
    
    # ===== ECZANE YETKİLERİ =====
    # Teklif İşlemleri
    can_approve_pharmacy_offers = models.BooleanField(default=True, verbose_name="Teklif onaylayabilir")
    can_reject_pharmacy_offers = models.BooleanField(default=True, verbose_name="Teklif reddedebilir")
    can_approve_high_value_pharmacy_offers = models.BooleanField(default=False, verbose_name="50K+ teklifleri onaylayabilir")
    can_update_product_prices = models.BooleanField(default=False, verbose_name="Ürün Fiyatlarını Güncelleyebilir")
    # Ürün Yönetimi
    can_manage_products = models.BooleanField(
        default=False, 
        verbose_name="Ürün Yönetebilir (Ekle/Düzenle)"
    )

    # İskonto Yönetimi
    can_apply_discount = models.BooleanField(default=True, verbose_name="İskonto uygulayabilir")
    can_apply_high_discount = models.BooleanField(default=False, verbose_name="%20+ iskonto uygulayabilir")
    
    # Fatura İşlemleri
    can_enter_invoice = models.BooleanField(default=True, verbose_name="Fatura bilgisi girebilir")
    can_approve_invoice_revision = models.BooleanField(default=False, verbose_name="Fatura revize onaylayabilir")
    can_edit_invoice = models.BooleanField(default=False, verbose_name="Fatura düzenleyebilir")
    
    # Personel Yönetimi
    can_approve_pharmacy_staff = models.BooleanField(default=False, verbose_name="Personel onaylayabilir")
    can_manage_pharmacy_staff = models.BooleanField(default=False, verbose_name="Personel yönetebilir")
    kvkk_accepted = models.BooleanField(
    default=False,
    verbose_name="KVKK Onayı"
    )
    kvkk_accepted_at = models.DateTimeField(
    null=True,
    blank=True,
    verbose_name="KVKK Onay Tarihi"
    )

    # Yönetici atama (hangi yöneticiye bağlı)
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members',
        verbose_name="Bağlı Olduğu Yönetici",
        help_text="Bu personelin bağlı olduğu yönetici"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def save(self, *args, **kwargs):
        """Yönetici ise tüm yetkileri otomatik ver"""
        if self.is_manager:
            # Firma yöneticisi
            if self.role == 'firma':
                self.can_create_offer = True
                self.can_edit_own_offer = True
                self.can_edit_all_offers = True
                self.can_delete_own_offer = True
                self.can_delete_all_offers = True
                self.can_send_offer = True
                self.can_view_all_offers = True
                self.can_approve_high_value_offers = True
                self.can_invite_staff = True
                self.can_manage_staff_permissions = True
                self.can_activate_deactivate_staff = True
                self.can_promote_to_manager = True
                self.can_view_reports = True
                self.can_view_financial_data = True
                self.can_export_data = True
            
            # Eczacı (eczane yöneticisi)
            elif self.role == 'eczane':
                self.can_approve_pharmacy_offers = True
                self.can_reject_pharmacy_offers = True
                self.can_approve_high_value_pharmacy_offers = True
                self.can_apply_discount = True
                self.can_apply_high_discount = True
                self.can_enter_invoice = True
                self.can_approve_invoice_revision = True
                self.can_edit_invoice = True
                self.can_approve_pharmacy_staff = True
                self.can_manage_pharmacy_staff = True
        
        super().save(*args, **kwargs)
