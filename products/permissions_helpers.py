"""
Yetkilendirme ve Aktivite Log Helper Fonksiyonları
"""
from django.utils import timezone
from decimal import Decimal


# ===========================
# YETKİ KONTROL FONKSİYONLARI
# ===========================

def check_offer_amount_threshold(offer, threshold=50000):
    """
    Teklif tutarının belirlenen eşiği aşıp aşmadığını kontrol eder
    
    Args:
        offer: Offer instance
        threshold: Eşik değeri (default: 50000 TL)
    
    Returns:
        bool: Eşiği aşıyorsa True
    """
    return offer.gross_total_price >= Decimal(str(threshold))


def can_user_send_offer(user, offer):
    """
    Kullanıcının teklifi gönderme yetkisi var mı kontrol eder
    
    Args:
        user: User instance
        offer: Offer instance
    
    Returns:
        tuple: (bool, str) - (Yetki var mı?, Hata mesajı)
    """
    # Teklif gönderme yetkisi yoksa
    if not user.can_send_offer:
        return False, "Teklif gönderme yetkiniz yok."
    
    # Yönetici ise direkt gönderebilir
    if user.is_manager:
        return True, ""
    
    # 50K üzeri teklifler yönetici onayına gider
    if check_offer_amount_threshold(offer):
        return False, "50.000 TL ve üzeri teklifler yönetici onayı gerektirir."
    
    return True, ""


def can_user_approve_offer(user, offer):
    """
    Kullanıcının teklifi onaylama yetkisi var mı kontrol eder (Eczane tarafı)
    
    Args:
        user: User instance
        offer: Offer instance
    
    Returns:
        tuple: (bool, str) - (Yetki var mı?, Hata mesajı)
    """
    # Onaylama yetkisi yoksa
    if not user.can_approve_pharmacy_offers:
        return False, "Teklif onaylama yetkiniz yok."
    
    # Eczacı ise direkt onaylayabilir
    if user.is_manager:
        return True, ""
    
    # 50K üzeri teklifler eczacı onayına gider
    if check_offer_amount_threshold(offer):
        return False, "50.000 TL ve üzeri teklifler eczacı onayı gerektirir."
    
    return True, ""


def can_user_apply_discount(user, discount_percentage):
    """
    Kullanıcının belirtilen oranda iskonto uygulama yetkisi var mı kontrol eder
    
    Args:
        user: User instance
        discount_percentage: İskonto yüzdesi
    
    Returns:
        tuple: (bool, str) - (Yetki var mı?, Hata mesajı)
    """
    # İskonto uygulama yetkisi yoksa
    if not user.can_apply_discount:
        return False, "İskonto uygulama yetkiniz yok."
    
    # Eczacı ise tüm iskontoları uygulayabilir
    if user.is_manager:
        return True, ""
    
    # %20 ve üzeri iskontolar eczacı onayı gerektirir
    if discount_percentage >= 20:
        return False, f"%{discount_percentage} iskonto eczacı onayı gerektirir. (Max %20)"
    
    return True, ""


def can_user_view_offer(user, offer):
    """
    Kullanıcının teklifi görüntüleme yetkisi var mı kontrol eder
    
    Args:
        user: User instance
        offer: Offer instance
    
    Returns:
        bool: Görüntüleyebilir mi?
    """
    # Superuser her şeyi görebilir
    if user.is_superuser:
        return True
    
    # Eczane kullanıcıları tüm teklifleri görebilir
    if user.role == 'eczane':
        return True
    
    # Firma yöneticisi tüm teklifleri görebilir
    if user.role == 'firma' and user.can_view_all_offers:
        return True
    
    # Firma personeli sadece kendi tekliflerini görebilir
    if user.role == 'firma':
        return offer.user == user
    
    return False


def can_user_edit_offer(user, offer):
    """
    Kullanıcının teklifi düzenleme yetkisi var mı kontrol eder
    
    Args:
        user: User instance
        offer: Offer instance
    
    Returns:
        tuple: (bool, str) - (Yetki var mı?, Hata mesajı)
    """
    # Sadece draft durumundaki teklifler düzenlenebilir
    if offer.status != 'draft':
        return False, "Sadece taslak teklifler düzenlenebilir."
    
    # Yönetici tüm teklifleri düzenleyebilir
    if user.is_manager and user.role == 'firma':
        return True, ""
    
    # Personel sadece kendi tekliflerini düzenleyebilir
    if offer.user == user and user.can_edit_own_offer:
        return True, ""
    
    return False, "Bu teklifi düzenleme yetkiniz yok."


def can_user_delete_offer(user, offer):
    """
    Kullanıcının teklifi silme yetkisi var mı kontrol eder
    
    Args:
        user: User instance
        offer: Offer instance
    
    Returns:
        tuple: (bool, str) - (Yetki var mı?, Hata mesajı)
    """
    # Sadece draft durumundaki teklifler silinebilir
    if offer.status != 'draft':
        return False, "Sadece taslak teklifler silinebilir."
    
    # Yönetici tüm teklifleri silebilir
    if user.is_manager and user.role == 'firma':
        return True, ""
    
    # Personel sadece kendi tekliflerini silebilir
    if offer.user == user and user.can_delete_own_offer:
        return True, ""
    
    return False, "Bu teklifi silme yetkiniz yok."


# ===========================
# AKTİVİTE LOG FONKSİYONLARI
# ===========================

def log_activity(user, action, description, offer=None, target_user=None, metadata=None, request=None):
    """
    Aktivite logu kaydeder
    
    Args:
        user: İşlemi yapan kullanıcı
        action: İşlem tipi (ActivityLog.ACTION_CHOICES'tan biri)
        description: İşlem açıklaması
        offer: İlgili teklif (opsiyonel)
        target_user: Hedef kullanıcı (opsiyonel)
        metadata: Ek bilgiler dict (opsiyonel)
        request: HTTP request (IP adresi için, opsiyonel)
    
    Returns:
        ActivityLog instance
    """
    from .models import ActivityLog
    
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
    
    log = ActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        offer=offer,
        target_user=target_user,
        metadata=metadata,
        ip_address=ip_address
    )
    
    return log


def create_notification(user, title, message, notification_type='info', offer=None, link=None):
    """
    Bildirim oluşturur
    
    Args:
        user: Bildirimi alacak kullanıcı
        title: Bildirim başlığı
        message: Bildirim mesajı
        notification_type: Bildirim tipi (info, success, warning, error)
        offer: İlgili teklif (opsiyonel)
        link: Yönlendirme linki (opsiyonel)
    
    Returns:
        Notification instance
    """
    from .models import Notification
    
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        offer=offer,
        link=link
    )
    
    return notification


def notify_manager_for_approval(offer):
    """
    Teklif için yöneticiye onay bildirimi gönderir
    
    Args:
        offer: Offer instance
    """
    # Firma personelinin yöneticisini bul
    manager = offer.user.manager
    
    if not manager:
        # Yönetici yoksa, firma rolündeki tüm yöneticilere gönder
        from accounts.models import User
        managers = User.objects.filter(role='firma', is_manager=True, is_approved=True)
        for mgr in managers:
            create_notification(
                user=mgr,
                title="Yönetici Onayı Gerekli",
                message=f"{offer.user.get_full_name()} tarafından {offer.gross_total_price:,.2f} TL tutarında teklif oluşturuldu ve onayınızı bekliyor.",
                notification_type='warning',
                offer=offer,
                link=f'/products/my-offers/{offer.id}/'
            )
    else:
        create_notification(
            user=manager,
            title="Yönetici Onayı Gerekli",
            message=f"{offer.user.get_full_name()} tarafından {offer.gross_total_price:,.2f} TL tutarında teklif oluşturuldu ve onayınızı bekliyor.",
            notification_type='warning',
            offer=offer,
            link=f'/products/my-offers/{offer.id}/'
        )


def notify_user_on_manager_approval(offer, approved):
    """
    Yönetici onayı/reddi sonrası personele bildirim gönderir
    
    Args:
        offer: Offer instance
        approved: Onaylandı mı? (bool)
    """
    if approved:
        create_notification(
            user=offer.user,
            title="Teklifiniz Onaylandı",
            message=f"#{offer.id} nolu teklifiniz yönetici tarafından onaylandı ve eczaneye gönderildi.",
            notification_type='success',
            offer=offer,
            link=f'/products/my-offers/{offer.id}/'
        )
    else:
        create_notification(
            user=offer.user,
            title="Teklifiniz Reddedildi",
            message=f"#{offer.id} nolu teklifiniz yönetici tarafından reddedildi. Sebep: {offer.manager_rejection_reason}",
            notification_type='error',
            offer=offer,
            link=f'/products/my-offers/{offer.id}/'
        )


def notify_on_offer_status_change(offer, old_status, new_status):
    """
    Teklif durumu değiştiğinde ilgili kişilere bildirim gönderir
    
    Args:
        offer: Offer instance
        old_status: Eski durum
        new_status: Yeni durum
    """
    # Eczane onayı
    if new_status == 'approved':
        create_notification(
            user=offer.user,
            title="Teklifiniz Onaylandı! 🎉",
            message=f"#{offer.id} nolu teklifiniz eczane tarafından onaylandı.",
            notification_type='success',
            offer=offer,
            link=f'/products/my-offers/{offer.id}/'
        )
    
    # Eczane reddi
    elif new_status == 'rejected':
        create_notification(
            user=offer.user,
            title="Teklifiniz Reddedildi",
            message=f"#{offer.id} nolu teklifiniz eczane tarafından reddedildi. Sebep: {offer.reject_reason or 'Belirtilmedi'}",
            notification_type='error',
            offer=offer,
            link=f'/products/my-offers/{offer.id}/'
        )