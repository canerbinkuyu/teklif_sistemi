from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models


class Offer(models.Model):
    STATUS_CHOICES = (
        ("draft", "Taslak"),
        ("sent", "Eczaneye Gönderildi"),
        ("approved", "Onaylandı"),
        ("rejected", "Reddedildi"),
        ("revised", "Revize Edildi"),
    )

    OVERALL_DISCOUNT_TYPE_CHOICES = (
        ("none", "Yok"),
        ("percent", "%"),
        ("amount", "₺"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    sent_at = models.DateTimeField(null=True, blank=True)

    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.TextField(blank=True, null=True)

    # REVİZE SİSTEMİ
    original_offer = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revisions',
        help_text="Bu teklif bir revize ise, orijinal teklif"
    )
    revision_number = models.IntegerField(default=1, help_text="Revizyon numarası")
    revised_at = models.DateTimeField(null=True, blank=True, help_text="Revize edilme tarihi")
    revision_note = models.TextField(blank=True, null=True, help_text="Revize notu")

    # PERSONEL TAKIBI
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_offers',
        help_text="Onaylayan eczane personeli"
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_offers',
        help_text="Reddeden eczane personeli"
    )

    # YÖNETİCİ ONAY SİSTEMİ
    requires_manager_approval = models.BooleanField(
        default=False,
        help_text="Yönetici onayı gerekiyor mu? (≥50K teklifler)"
    )
    manager_approval_pending = models.BooleanField(
        default=False,
        help_text="Yönetici onayı bekliyor mu?"
    )
    approved_by_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manager_approved_offers',
        help_text="Onaylayan yönetici"
    )
    manager_approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Yönetici onay tarihi"
    )
    manager_rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Yönetici red nedeni"
    )

    # FATURA BİLGİLERİ
    invoice_number = models.CharField(max_length=100, blank=True, null=True, help_text="Fatura No")
    invoice_date = models.DateField(null=True, blank=True, help_text="Fatura Tarihi")
    delivery_deadline = models.DateField(null=True, blank=True, help_text="Termin Tarihi")

    # FATURA REVİZE TALEBI
    invoice_revision_pending = models.BooleanField(default=False, help_text="Revize talebi bekliyor")
    invoice_revision_approved = models.BooleanField(default=False, help_text="Yönetici onayladı")
    invoice_revision_reason = models.TextField(blank=True, null=True, help_text="Revize nedeni")
    invoice_revision_requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice_revision_requests',
    )

    # GENEL TOPLAM İSKONTO
    overall_discount_type = models.CharField(
        max_length=10,
        choices=OVERALL_DISCOUNT_TYPE_CHOICES,
        default="none"
    )
    overall_discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # -------------------------
    # İTEM BAZLI HESAPLAR (İskontosuz)
    # -------------------------
    def items_subtotal_net(self):
        """Tüm ürünlerin KDV hariç toplam (iskonto öncesi)"""
        return sum(item.gross_line_subtotal for item in self.items.all())

    def items_subtotal_gross(self):
        """Tüm ürünlerin KDV dahil toplam (iskonto öncesi)"""
        return sum(item.gross_total_price for item in self.items.all())

    # -------------------------
    # İTEM BAZLI HESAPLAR (İtem iskontoları uygulanmış)
    # -------------------------
    def items_net_after_item_discounts(self):
        """Tüm ürünlerin KDV hariç toplam (item iskontoları uygulanmış)"""
        return sum(item.line_subtotal for item in self.items.all())

    def items_vat_after_item_discounts(self):
        """Tüm ürünlerin KDV toplamı (item iskontoları uygulanmış)"""
        return sum(item.vat_amount for item in self.items.all())

    def items_gross_after_item_discounts(self):
        """Tüm ürünlerin KDV dahil toplam (item iskontoları uygulanmış)"""
        return sum(item.total_price for item in self.items.all())

    # -------------------------
    # GENEL İSKONTO HESAPLAR
    # -------------------------
    @property
    def overall_discount_amount(self):
        """
        Genel toplam iskonto tutarı.
        % ise: KDV hariç toplama (item iskontoları sonrası) yüzde uygular
        ₺ ise: sabit tutar
        """
        net_after_items = self.items_net_after_item_discounts()
        if self.overall_discount_type == "percent":
            return (net_after_items * self.overall_discount_value / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif self.overall_discount_type == "amount":
            # Genel ₺ iskonto, net toplama capped
            if self.overall_discount_value > net_after_items:
                return net_after_items
            return self.overall_discount_value
        return Decimal("0")

    @property
    def net_after_overall_discount(self):
        """Genel iskonto sonrası KDV hariç toplam"""
        return self.items_net_after_item_discounts() - self.overall_discount_amount

    @property
    def vat_after_overall_discount(self):
        """
        Genel iskonto sonrası KDV tutarı.
        Her ürün farklı KDV oranına sahip olabilir, bu yüzden
        oranı koruyarak hesaplıyoruz: her item'in oranı üzerinden.
        """
        net_after_items = self.items_net_after_item_discounts()
        if net_after_items == 0:
            return Decimal("0")

        # Her item için orantılı KDV hesapla
        total_vat = Decimal("0")
        for item in self.items.all():
            if net_after_items > 0:
                # İtem'in orantısı
                item_ratio = item.line_subtotal / net_after_items
                # İtem'in genel iskontodaki payı
                item_overall_discount = self.overall_discount_amount * item_ratio
                # İtem'in iskonto sonrası neti
                item_net_final = item.line_subtotal - item_overall_discount
                # KDV
                item_vat = (item_net_final * Decimal(str(item.vat_rate)) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                total_vat += item_vat

        return total_vat

    @property
    def final_total(self):
        """Son toplam: net_after_overall_discount + vat_after_overall_discount"""
        return self.net_after_overall_discount + self.vat_after_overall_discount
    
    @property
    def total_item_discounts(self):
        """Ürün iskontolarının toplamı"""
        return self.items_subtotal_net() - self.items_net_after_item_discounts()

    # -------------------------
    # ESKİ UYUMLU (template'ler için)
    # -------------------------
    def total_price(self):
        """Backward compat: item iskontoları sonrası KDV dahil toplam"""
        return self.items_gross_after_item_discounts()

    def gross_total_price(self):
        """Backward compat: iskontosuz KDV dahil toplam"""
        return self.items_subtotal_gross()

    # -------------------------
    # REVİZE SİSTEMİ
    # -------------------------
    def get_all_revisions(self):
        if self.original_offer:
            original = self.original_offer
        else:
            original = self
        revisions = [original] + list(original.revisions.all().order_by('revision_number'))
        return revisions

    def get_latest_revision(self):
        if self.original_offer:
            original = self.original_offer
        else:
            original = self
        latest = original.revisions.order_by('-revision_number').first()
        return latest if latest else original

    def is_latest(self):
        return self == self.get_latest_revision()

    def __str__(self):
        if self.revision_number > 1:
            return f"Teklif #{self.id} (Rev.{self.revision_number})"
        return f"Teklif #{self.id}"


class Product(models.Model):
    barcode = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.IntegerField(default=10)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    price_updated_at = models.DateTimeField(auto_now=True, verbose_name="Fiyat Güncelleme Tarihi")
   
    @property
    def price_without_vat(self):
        """KDV hariç fiyat: price / (1 + vat_rate/100)"""
        from decimal import Decimal, ROUND_HALF_UP
        return (self.price / (1 + Decimal(str(self.vat_rate)) / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def __str__(self):
        return self.name


class OfferItem(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ("none", "Yok"),
        ("percent", "%"),
        ("amount", "₺"),
    )

    note = models.TextField(blank=True, null=True)

    offer = models.ForeignKey("Offer", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.PositiveIntegerField()

    discount_type = models.CharField(
        max_length=10, choices=DISCOUNT_TYPE_CHOICES, default="none"
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # unit_price = KDV HARİÇ fiyat olarak kaydet
        self.unit_price = self.product.price_without_vat
        self.vat_rate = self.product.vat_rate
        super().save(*args, **kwargs)

    # -------------------------
    # KDV DAHİL BİRİM FIYAT
    # -------------------------
    @property
    def unit_price_with_vat(self):
        """KDV dahil birim fiyat (görüntüleme için)"""
        return (self.unit_price * (1 + Decimal(str(self.vat_rate)) / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # -------------------------
    # İSKONTO HESAPLAR
    # -------------------------
    @property
    def unit_discount_amount(self):
        """
        Birim başına iskonto tutarı.
        %  → birim fiyata yüzde
        ₺  → birim fiyata sabit tutar düşür
        """
        if self.discount_type == "percent":
            return (self.unit_price * self.discount_value / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if self.discount_type == "amount":
            # ₺ iskontu birim fiyata düşür, eksi olamaz
            if self.discount_value > self.unit_price:
                return self.unit_price
            return self.discount_value
        return Decimal("0")

    @property
    def discounted_unit_price(self):
        """İskontolu birim fiyat"""
        result = self.unit_price - self.unit_discount_amount
        return max(result, Decimal("0"))

    # -------------------------
    # İSKONTOLU (NET) HESAPLAR
    # -------------------------
    @property
    def line_subtotal(self):
        """İskontolu birim fiyat × adet (KDV hariç)"""
        return self.discounted_unit_price * self.quantity

    @property
    def discount_amount(self):
        """Satırın toplam iskonto tutarı"""
        return self.unit_discount_amount * self.quantity

    @property
    def vat_amount(self):
        """KDV tutarı (iskontolu tutar üzerinden)"""
        return (self.line_subtotal * Decimal(str(self.vat_rate)) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def total_price(self):
        """Satır toplam (iskontolu, KDV dahil)"""
        return self.line_subtotal + self.vat_amount

    # -------------------------
    # İSKONTOSUZ (GROSS) HESAPLAR
    # -------------------------
    @property
    def gross_line_subtotal(self):
        """Birim fiyat × adet (iskonto yok, KDV hariç)"""
        return self.unit_price * self.quantity

    @property
    def gross_vat_amount(self):
        """KDV (iskontosuz)"""
        return (self.gross_line_subtotal * Decimal(str(self.vat_rate)) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def gross_total_price(self):
        """Satır toplam (iskontosuz, KDV dahil)"""
        return self.gross_line_subtotal + self.gross_vat_amount

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    discount_type = models.CharField(max_length=20, default="none")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.TextField(blank=True, null=True)
    
    # YENİ ALAN - EKLE
    delivery_address = models.ForeignKey(
        'accounts.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offer_items',
        verbose_name='Teslimat Adresi'
    )


# ===========================
# FAVORİ SİSTEMİ
# ===========================
class FavoriteProduct(models.Model):
    """Firma kullanıcılarının favori ürünleri"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_products'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class FavoriteDraft(models.Model):
    """Firma kullanıcılarının favori teklif taslakları"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_drafts'
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True, help_text="Taslak notu")

    class Meta:
        unique_together = ('user', 'offer')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - Teklif #{self.offer.id}"


# ===========================
# AKTİVİTE LOG SİSTEMİ
# ===========================
class ActivityLog(models.Model):
    """Tüm kullanıcı aktivitelerinin kaydı"""
    
    ACTION_CHOICES = (
        # Teklif İşlemleri
        ('offer_created', 'Teklif Oluşturuldu'),
        ('offer_updated', 'Teklif Güncellendi'),
        ('offer_deleted', 'Teklif Silindi'),
        ('offer_sent', 'Teklif Gönderildi'),
        ('offer_sent_for_approval', 'Teklif Yönetici Onayına Gönderildi'),
        
        # Yönetici Onayları
        ('manager_approved_offer', 'Yönetici Teklifi Onayladı'),
        ('manager_rejected_offer', 'Yönetici Teklifi Reddetti'),
        
        # Eczane İşlemleri
        ('offer_approved', 'Teklif Onaylandı'),
        ('offer_rejected', 'Teklif Reddedildi'),
        ('discount_applied', 'İskonto Uygulandı'),
        ('discount_approval_requested', 'İskonto Onay Talebi'),
        
        # Fatura İşlemleri
        ('invoice_created', 'Fatura Oluşturuldu'),
        ('invoice_updated', 'Fatura Güncellendi'),
        ('invoice_revision_requested', 'Fatura Revize Talebi'),
        ('invoice_revision_approved', 'Fatura Revize Onaylandı'),
        ('invoice_revision_rejected', 'Fatura Revize Reddedildi'),
        
        # Revize İşlemleri
        ('offer_revised', 'Teklif Revize Edildi'),
        
        # Kullanıcı İşlemleri
        ('user_created', 'Kullanıcı Oluşturuldu'),
        ('user_approved', 'Kullanıcı Onaylandı'),
        ('user_permissions_changed', 'Kullanıcı Yetkileri Değiştirildi'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        help_text="İşlemi yapan kullanıcı"
    )
    
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text="Yapılan işlem"
    )
    
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activity_logs',
        help_text="İlgili teklif (varsa)"
    )
    
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='targeted_logs',
        help_text="İşlemin hedef kullanıcısı (varsa)"
    )
    
    description = models.TextField(
        help_text="İşlem detayı"
    )
    
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Ek bilgiler (JSON formatında)"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="İşlemin yapıldığı IP adresi"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="İşlem zamanı"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Aktivite Logu"
        verbose_name_plural = "Aktivite Logları"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['offer', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"


# ===========================
# BİLDİRİM SİSTEMİ
# ===========================
class Notification(models.Model):
    """Kullanıcılara gönderilen bildirimler"""
    
    TYPE_CHOICES = (
        ('info', 'Bilgi'),
        ('success', 'Başarılı'),
        ('warning', 'Uyarı'),
        ('error', 'Hata'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="Bildirimin alıcısı"
    )
    
    title = models.CharField(
        max_length=255,
        help_text="Bildirim başlığı"
    )
    
    message = models.TextField(
        help_text="Bildirim mesajı"
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='info',
        help_text="Bildirim tipi"
    )
    
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        help_text="İlgili teklif (varsa)"
    )
    
    link = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Yönlendirilecek link"
    )
    
    is_read = models.BooleanField(
        default=False,
        help_text="Okundu mu?"
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Okunma zamanı"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Oluşturulma zamanı"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bildirim"
        verbose_name_plural = "Bildirimler"
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        status = "✓" if self.is_read else "●"
        return f"{status} {self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Bildirimi okundu olarak işaretle"""
        if not self.is_read:
            self.is_read = True
            self.read_at = models.DateTimeField(auto_now=True)
            self.save()