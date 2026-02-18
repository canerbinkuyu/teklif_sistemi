from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
import pandas as pd

from .models import Product, Offer, OfferItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("barcode", "name", "price", "vat_rate")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel),
                name="products_product_import_excel",
            ),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        if request.method == "POST":
            excel_file = request.FILES.get("excel_file")
            if not excel_file:
                self.message_user(request, "Lütfen bir Excel dosyası seçin.", level="error")
                return redirect(".")

            df = pd.read_excel(excel_file)

            # Zorunlu kolon kontrolü
            required_cols = {"name", "price", "vat_rate"}
            if not required_cols.issubset(set(df.columns)):
                self.message_user(
                    request,
                    f"Excel sütunları eksik. Zorunlu sütunlar: {required_cols}",
                    level="error",
                )
                return redirect(".")

            created_count = 0
            updated_count = 0

            for _, row in df.iterrows():
                name = str(row["name"]).strip()

                product, created = Product.objects.update_or_create(
                    name=name,
                    defaults={
                        "price": row["price"],
                        "vat_rate": int(row["vat_rate"]),
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.message_user(
                request,
                f"Excel yükleme tamamlandı. "
                f"Yeni eklenen: {created_count}, Güncellenen: {updated_count}"
            )

            return redirect("../")  # Product listesine döner

        return render(request, "admin/import_excel.html")

    change_list_template = "admin/products/product/change_list.html"


# OfferItem Inline - Teklif içinde ürünleri göstermek için
class OfferItemInline(admin.TabularInline):
    model = OfferItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price", "vat_rate", "discount_type", "discount_value", "note", "get_total")
    can_delete = False
    
    fields = ("product", "quantity", "unit_price", "discount_type", "discount_value", "vat_rate", "note", "get_total")
    
    def get_total(self, obj):
        """Satır toplamı"""
        if obj.id:
            return f"{obj.total_price:.2f} ₺"
        return "-"
    get_total.short_description = "Toplam"
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    inlines = [OfferItemInline]
    list_display = ("get_offer_number", "user", "status", "created_at", "sent_at", "item_count", "total_amount")
    list_filter = ("status", "created_at", "sent_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "id")
    readonly_fields = ("created_at", "sent_at", "approved_at", "rejected_at", "revised_at")
    
    fieldsets = (
        ("Teklif Bilgileri", {
            "fields": ("user", "status", "original_offer", "revision_number")
        }),
        ("Tarihler", {
            "fields": ("created_at", "sent_at", "approved_at", "rejected_at", "revised_at")
        }),
        ("Revizyon", {
            "fields": ("revision_note",),
            "classes": ("collapse",)
        }),
        ("Red Bilgileri", {
            "fields": ("reject_reason",),
            "classes": ("collapse",)
        }),
    )
    
    def get_offer_number(self, obj):
        """Teklif numarasını göster"""
        if obj.original_offer:
            base_id = obj.original_offer.id
        else:
            base_id = obj.id
        
        if obj.revision_number > 1:
            return f"#{base_id} (Rev.{obj.revision_number})"
        return f"#{base_id}"
    get_offer_number.short_description = "Teklif No"
    
    def item_count(self, obj):
        """Ürün sayısı"""
        return obj.items.count()
    item_count.short_description = "Ürün Sayısı"
    
    def total_amount(self, obj):
        """Toplam tutar"""
        return f"{obj.total_price():.2f} ₺"
    total_amount.short_description = "Toplam Tutar"
    
    def has_add_permission(self, request):
        """Eczane kullanıcıları teklif ekleyemez"""
        if hasattr(request.user, 'role') and request.user.role == 'eczane':
            return False
        return super().has_add_permission(request)
    
    def has_change_permission(self, request, obj=None):
        """Eczane kullanıcıları teklif düzenleyemez"""
        if hasattr(request.user, 'role') and request.user.role == 'eczane':
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Eczane kullanıcıları teklif silemez"""
        if hasattr(request.user, 'role') and request.user.role == 'eczane':
            return False
        return super().has_delete_permission(request, obj)
    
    def has_view_permission(self, request, obj=None):
        """Sadece süper admin görebilir"""
        return request.user.is_superuser


# OfferItem'i admin'den gizle (sadece Offer içinde inline olarak göster)
# @admin.register(OfferItem)
# class OfferItemAdmin(admin.ModelAdmin):
#     list_display = ("offer", "product", "quantity", "unit_price", "vat_rate")