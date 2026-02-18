from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.shortcuts import get_object_or_404
from accounts.models import User
from decimal import Decimal
from accounts.models import Address
import openpyxl

def register_view(request):
    
    """Detaylı kayıt - Firma/Eczane sahibi için"""
    
    if request.method == "POST":
        # Temel bilgiler
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        role = request.POST.get("role", "").strip()
        
        # Doğrulama
        if not all([username, email, password, first_name, last_name, role]):
            messages.error(request, "Tüm zorunlu alanları doldurun.")
            return render(request, "accounts/register.html")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten kullanılıyor.")
            return render(request, "accounts/register.html")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu email zaten kayıtlı.")
            return render(request, "accounts/register.html")
        
        if len(password) < 8:
            messages.error(request, "Şifre en az 8 karakter olmalıdır.")
            return render(request, "accounts/register.html")
        
        # Kullanıcıyı oluştur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_manager=True,  # İlk kullanıcı yönetici olur
            is_approved=False  # Admin onayı bekleyecek
        )
        # KVKK onayı
        if request.POST.get('kvkk_accepted'):
            user.kvkk_accepted = True
            user.kvkk_accepted_at = timezone.now()
            user.save()
        
        # Firma bilgileri
        if role == 'firma':
            user.company_name = request.POST.get("company_name", "").strip()
            user.company_tax_number = request.POST.get("company_tax_number", "").strip()
            user.company_tax_office = request.POST.get("company_tax_office", "").strip()
            user.company_phone = request.POST.get("company_phone", "").strip()
            user.company_mobile = request.POST.get("company_mobile", "").strip()
            user.company_address = request.POST.get("company_address", "").strip()
            user.company_responsible_person = request.POST.get("company_responsible_person", "").strip()
            user.company_responsible_email = request.POST.get("company_responsible_email", "").strip()
            
            # Firma bilgileri kontrolü
            if not all([user.company_name, user.company_tax_number, user.company_tax_office, 
                       user.company_mobile, user.company_address]):
                user.delete()
                messages.error(request, "Firma bilgilerini eksiksiz doldurun.")
                return render(request, "accounts/register.html")
        
        # Eczane bilgileri
        elif role == 'eczane':
            user.pharmacy_name = request.POST.get("pharmacy_name", "").strip()
            user.pharmacist_name = request.POST.get("pharmacist_name", "").strip()
            user.pharmacy_tax_number = request.POST.get("pharmacy_tax_number", "").strip()
            user.pharmacy_tax_office = request.POST.get("pharmacy_tax_office", "").strip()
            user.pharmacy_phone = request.POST.get("pharmacy_phone", "").strip()
            user.pharmacy_mobile = request.POST.get("pharmacy_mobile", "").strip()
            user.pharmacy_email = request.POST.get("pharmacy_email", "").strip()
            user.pharmacy_address = request.POST.get("pharmacy_address", "").strip()
            user.pharmacy_license_number = request.POST.get("pharmacy_license_number", "").strip()
            
            # Eczane bilgileri kontrolü
            if not all([user.pharmacy_name, user.pharmacist_name, user.pharmacy_tax_number, 
                       user.pharmacy_tax_office, user.pharmacy_mobile, user.pharmacy_email, 
                       user.pharmacy_address]):
                user.delete()
                messages.error(request, "Eczane bilgilerini eksiksiz doldurun.")
                return render(request, "accounts/register.html")
        
        user.save()
        
        messages.success(
            request, 
            f"Kayıt başarılı! {user.get_full_name()}, admin onayından sonra sisteme giriş yapabilirsiniz."
        )
        return redirect("awaiting_approval")
    
    return render(request, "accounts/register.html")

def pharmacist_register(request):
    """Eczacı kayıt sayfası - sadece eczacı bilgileri"""
    
    if request.method == "POST":
        # Temel bilgiler
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        
        # Eczane bilgileri
        pharmacy_name = request.POST.get("pharmacy_name", "").strip()
        pharmacist_name = request.POST.get("pharmacist_name", "").strip()
        pharmacy_tax_number = request.POST.get("pharmacy_tax_number", "").strip()
        pharmacy_tax_office = request.POST.get("pharmacy_tax_office", "").strip()
        pharmacy_phone = request.POST.get("pharmacy_phone", "").strip()
        pharmacy_mobile = request.POST.get("pharmacy_mobile", "").strip()
        pharmacy_email = request.POST.get("pharmacy_email", "").strip()
        pharmacy_address = request.POST.get("pharmacy_address", "").strip()
        pharmacy_license_number = request.POST.get("pharmacy_license_number", "").strip()
        
        # Doğrulama
        if not all([username, email, password, first_name, last_name, pharmacy_name]):
            messages.error(request, "Zorunlu alanları doldurun.")
            return render(request, "accounts/pharmacist_register.html")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten kullanılıyor.")
            return render(request, "accounts/pharmacist_register.html")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu email zaten kayıtlı.")
            return render(request, "accounts/pharmacist_register.html")
        
        if len(password) < 8:
            messages.error(request, "Şifre en az 8 karakter olmalıdır.")
            return render(request, "accounts/pharmacist_register.html")
        
        # Eczacı oluştur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='eczane',
            is_manager=True,
            is_approved=False,
            pharmacy_name=pharmacy_name,
            pharmacist_name=pharmacist_name,
            pharmacy_tax_number=pharmacy_tax_number,
            pharmacy_tax_office=pharmacy_tax_office,
            pharmacy_phone=pharmacy_phone,
            pharmacy_mobile=pharmacy_mobile,
            pharmacy_email=pharmacy_email,
            pharmacy_address=pharmacy_address,
            pharmacy_license_number=pharmacy_license_number,
        )
        # KVKK onayı
        if request.POST.get('kvkk_accepted'):
            user.kvkk_accepted = True
            user.kvkk_accepted_at = timezone.now()
            user.save()
        
        messages.success(request, "Kayıt başarılı! Admin onayından sonra sisteme giriş yapabilirsiniz.")
        return redirect("awaiting_approval")
    
    return render(request, "accounts/pharmacist_register.html")


def awaiting_approval(request):
    """Onay bekleme sayfası"""
    return render(request, "accounts/awaiting_approval.html")


def login_view(request):
    """Giriş sayfası"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Admin/Superuser için onay kontrolü yapma
            if not user.is_superuser and not user.is_staff:
                if not user.is_approved:
                    messages.error(request, "Hesabınız henüz onaylanmamış. Lütfen admin onayını bekleyin.")
                    return render(request, "accounts/login.html")
                # Pasif kullanıcı kontrolü
                if not user.is_active_user:
                    messages.error(request, "Hesabınız pasif durumda. Yöneticinizle iletişime geçin.")
                    return render(request, "accounts/login.html")
            
            login(request, user)
            return redirect("redirect_after_login")
        else:
            messages.error(request, "Kullanıcı adı veya şifre hatalı.")
    
    return render(request, "accounts/login.html")


def user_logout(request):
    """Çıkış"""
    logout(request)
    messages.success(request, "Başarıyla çıkış yaptınız.")
    return redirect("login")


def redirect_after_login(request):
    """Giriş sonrası yönlendirme"""
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.user.is_superuser:
        return redirect("admin_dashboard")
    
    if request.user.role == "eczane":
        return redirect("pharmacy_inbox")  # veya "pharmacy_offer_detail" gibi mevcut bir URL
    elif request.user.role == "firma":
        return redirect("my_offers")
    
    return redirect("product_list")


def profile_view(request):
    """Profil sayfası"""
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":
        user = request.user
        
        # Temel bilgiler
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.email = request.POST.get("email", "").strip()
        
        # Firma bilgileri
        if user.role == "firma":
            user.company_name = request.POST.get("company_name", "").strip()
            user.company_tax_number = request.POST.get("company_tax_number", "").strip()
            user.company_tax_office = request.POST.get("company_tax_office", "").strip()
            user.company_phone = request.POST.get("company_phone", "").strip()
            user.company_mobile = request.POST.get("company_mobile", "").strip()
            user.company_address = request.POST.get("company_address", "").strip()
            user.company_responsible_person = request.POST.get("company_responsible_person", "").strip()
            user.company_responsible_email = request.POST.get("company_responsible_email", "").strip()
        
        # Eczane bilgileri
        elif user.role == "eczane":
            user.pharmacy_name = request.POST.get("pharmacy_name", "").strip()
            user.pharmacist_name = request.POST.get("pharmacist_name", "").strip()
            user.pharmacy_tax_number = request.POST.get("pharmacy_tax_number", "").strip()
            user.pharmacy_tax_office = request.POST.get("pharmacy_tax_office", "").strip()
            user.pharmacy_phone = request.POST.get("pharmacy_phone", "").strip()
            user.pharmacy_mobile = request.POST.get("pharmacy_mobile", "").strip()
            user.pharmacy_email = request.POST.get("pharmacy_email", "").strip()
            user.pharmacy_address = request.POST.get("pharmacy_address", "").strip()
            user.pharmacy_license_number = request.POST.get("pharmacy_license_number", "").strip()
        
        user.save()
        messages.success(request, "Profil bilgileriniz güncellendi.")
    
    return render(request, "accounts/profile.html")
"""
Bu kodları accounts/views.py dosyasının SONUNA ekleyin
"""

import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required


@login_required
def invite_staff(request):
    """Yönetici personel davet eder"""
    
    # Sadece yöneticiler davet edebilir
    if not request.user.is_manager or not request.user.can_invite_staff:
        messages.error(request, "Personel davet etme yetkiniz yok.")
        return redirect("my_offers")
    
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        
        # Doğrulama
        if not email:
            messages.error(request, "Email adresi gereklidir.")
            return render(request, "accounts/invite_staff.html")
        
        # Email kullanılıyor mu?
        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu email zaten kayıtlı.")
            return render(request, "accounts/invite_staff.html")
        
        # Token oluştur (benzersiz)
        token = secrets.token_urlsafe(32)
        
        # Geçerlilik süresi (7 gün)
        expires = timezone.now() + timedelta(days=7)
        
        # Davetiye kaydı oluştur (kullanıcı henüz yok, sadece token)
        invited_user = User.objects.create(
            username=f"temp_{token[:8]}",  # Geçici username
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=request.user.role,  # Yönetici ile aynı rol
            is_manager=False,  # Personel
            is_approved=True,  # Otomatik onaylı (yönetici davet etti)
            manager=request.user,  # Bağlı olduğu yönetici
            invited_by=request.user,
            invitation_token=token,
            invitation_expires=expires,
            is_active=False  # Kayıt tamamlanana kadar pasif
        )
        
        # Davetiye linki
        invite_link = request.build_absolute_uri(
            f"/accounts/register/staff/{token}/"
        )
        
        messages.success(
            request, 
            f"Davetiye oluşturuldu! Davetiye Linki: {invite_link}"
        )
        
        # TODO: Email gönderme (şimdilik ekranda göster)
        # send_mail(
        #     subject=f"{request.user.company_name} - Personel Davetiyesi",
        #     message=f"Merhaba {first_name}, {invite_link} adresinden kaydınızı tamamlayabilirsiniz.",
        #     from_email="noreply@teklif.com",
        #     recipient_list=[email]
        # )
        
        return render(request, "accounts/invite_success.html", {
            "invite_link": invite_link,
            "email": email
        })
    
    return render(request, "accounts/invite_staff.html")


def staff_register(request, token):
    """Token ile personel kaydı"""
    
    # Token geçerli mi?
    try:
        invited_user = User.objects.get(
            invitation_token=token,
            invitation_expires__gt=timezone.now(),
            is_active=False
        )
    except User.DoesNotExist:
        messages.error(request, "Davetiye geçersiz veya süresi dolmuş.")
        return redirect("login")
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        
        # Doğrulama
        if not username or not password:
            messages.error(request, "Kullanıcı adı ve şifre gereklidir.")
            return render(request, "accounts/staff_register.html", {"user": invited_user})
        
        if User.objects.filter(username=username).exclude(id=invited_user.id).exists():
            messages.error(request, "Bu kullanıcı adı zaten kullanılıyor.")
            return render(request, "accounts/staff_register.html", {"user": invited_user})
        
        if len(password) < 8:
            messages.error(request, "Şifre en az 8 karakter olmalıdır.")
            return render(request, "accounts/staff_register.html", {"user": invited_user})
        
        # Kullanıcıyı tamamla
        invited_user.username = username
        invited_user.set_password(password)
        invited_user.is_active = True  # Aktif et
        invited_user.invitation_token = None  # Token'ı temizle
        invited_user.save()
        
        messages.success(
            request,
            f"Kayıt tamamlandı! Artık sisteme giriş yapabilirsiniz."
        )
        return redirect("login")
    
    return render(request, "accounts/staff_register.html", {"user": invited_user})


@login_required
def my_staff(request):
    """Yönetici kendi personelini görür"""
    
    if not request.user.is_manager:
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        return redirect("my_offers")
    
    # Davet edilen personeller
    staff = User.objects.filter(
        manager=request.user
    ).order_by('-date_joined')
    
    # Bekleyen davetiyeler (kayıt tamamlanmamış)
    pending_invites = staff.filter(is_active=False, invitation_expires__gt=timezone.now())
    
    # Aktif personel
    active_staff = staff.filter(is_active=True)
    
    return render(request, "accounts/my_staff.html", {
        "active_staff": active_staff,
        "pending_invites": pending_invites
    })
"""
Bu kodu accounts/views.py dosyasının SONUNA ekleyin
"""

def pharmacy_staff_register(request):
    """Eczane personeli eczane email'i ile kayıt olur"""
    
    if request.method == "POST":
        # Temel bilgiler
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        pharmacy_email = request.POST.get("pharmacy_email", "").strip()
        
        # Doğrulama
        if not all([username, email, password, first_name, last_name, pharmacy_email]):
            messages.error(request, "Tüm alanları doldurun.")
            return render(request, "accounts/pharmacy_staff_register.html")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten kullanılıyor.")
            return render(request, "accounts/pharmacy_staff_register.html")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu email zaten kayıtlı.")
            return render(request, "accounts/pharmacy_staff_register.html")
        
        if len(password) < 8:
            messages.error(request, "Şifre en az 8 karakter olmalıdır.")
            return render(request, "accounts/pharmacy_staff_register.html")
        
        # Eczane email'i ile kayıtlı eczacı var mı?
        try:
            pharmacist = User.objects.get(
                pharmacy_email=pharmacy_email,
                role='eczane',
                is_manager=True,
                is_approved=True
            )
        except User.DoesNotExist:
            messages.error(
                request, 
                f"'{pharmacy_email}' adresine kayıtlı onaylı eczane bulunamadı. Eczane email adresini kontrol edin."
            )
            return render(request, "accounts/pharmacy_staff_register.html")
        
        # Personeli oluştur (pasif olarak)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='eczane',
            is_manager=False,
            is_approved=False,  # Eczacı onayı bekleyecek
            manager=pharmacist,  # Bağlı olduğu eczacı
            pharmacy_name=pharmacist.pharmacy_name,  # Eczane bilgilerini kopyala
            pharmacy_tax_number=pharmacist.pharmacy_tax_number,
            pharmacy_tax_office=pharmacist.pharmacy_tax_office,
            pharmacy_phone=pharmacist.pharmacy_phone,
            pharmacy_mobile=pharmacist.pharmacy_mobile,
            pharmacy_email=pharmacist.pharmacy_email,
            pharmacy_address=pharmacist.pharmacy_address,
        )
        # KVKK onayı
        if request.POST.get('kvkk_accepted'):
            user.kvkk_accepted = True
            user.kvkk_accepted_at = timezone.now()
            user.save()

        messages.success(
            request,
            f"Kayıt başarılı! {pharmacist.pharmacy_name} eczacısının onayından sonra sisteme giriş yapabilirsiniz."
        )
        return redirect("awaiting_approval")
    
    return render(request, "accounts/pharmacy_staff_register.html")


@login_required
def pharmacist_staff_list(request):
    """Eczacı kendi personelini görür ve onaylar"""
    
    # GEÇICI - YETKİ KONTROLÜ KALDIRILDI
    # if not request.user.is_manager or request.user.role != 'eczane':
    #     messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
    #     return redirect("pharmacy_inbox")
    
    # Bağlı personeller
    staff = User.objects.filter(
        manager=request.user,
        role='eczane'
    ).order_by('-date_joined')
    
    # Onay bekleyenler
    pending_staff = staff.filter(is_approved=False)
    
    # Onaylı personel
    approved_staff = staff.filter(is_approved=True)
    
    return render(request, "accounts/pharmacist_staff_list.html", {
        "pending_staff": pending_staff,
        "approved_staff": approved_staff
    })


@login_required
def approve_pharmacy_staff(request, user_id):
    """Eczacı personeli onaylar"""
    
    if not request.user.is_manager or request.user.role != 'eczane':
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect("pharmacy_dashboard")
    
    user = get_object_or_404(User, id=user_id)
    
    # Sadece kendi personelini onaylayabilir
    if user.manager != request.user:
        messages.error(request, "Bu personel size bağlı değil.")
        return redirect("pharmacist_staff_list")
    
    user.is_approved = True
    user.approved_by = request.user
    user.save()
    
    messages.success(request, f"{user.get_full_name()} başarıyla onaylandı.")
    return redirect("pharmacist_staff_list")


@login_required
def reject_pharmacy_staff(request, user_id):
    """Eczacı personel kaydını reddeder/siler"""
    
    if not request.user.is_manager or request.user.role != 'eczane':
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect("pharmacy_dashboard")
    
    user = get_object_or_404(User, id=user_id)
    
    # Sadece kendi personelini silebilir
    if user.manager != request.user:
        messages.error(request, "Bu personel size bağlı değil.")
        return redirect("pharmacist_staff_list")
    
    username = user.username
    user.delete()
    
    messages.warning(request, f"{username} kaydı silindi.")
    return redirect("pharmacist_staff_list")

"""
Bu kodları accounts/views.py dosyasının SONUNA ekleyin
"""

@login_required
def edit_staff_permissions(request, user_id):
    """Yönetici personel yetkilerini düzenler"""
    
    # Sadece yöneticiler düzenleyebilir
    if not request.user.is_manager:
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect("my_staff" if request.user.role == 'firma' else "pharmacist_staff_list")
    
    staff = get_object_or_404(User, id=user_id)
    
    # Sadece kendi personelini düzenleyebilir
    if staff.manager != request.user:
        messages.error(request, "Bu personel size bağlı değil.")
        return redirect("my_staff" if request.user.role == 'firma' else "pharmacist_staff_list")
    
    # Yöneticiler düzenlenemez
    if staff.is_manager:
        messages.error(request, "Yöneticilerin yetkileri düzenlenemez.")
        return redirect("my_staff" if request.user.role == 'firma' else "pharmacist_staff_list")
    
    if request.method == "POST":
        # Aktiflik durumu
        staff.is_active_user = request.POST.get("is_active_user") == "on"
        
        if request.user.role == 'firma':
            # Firma yetkileri
            staff.can_create_offer = request.POST.get("can_create_offer") == "on"
            staff.can_edit_own_offer = request.POST.get("can_edit_own_offer") == "on"
            staff.can_revise_offer = request.POST.get("can_revise_offer") == "on"  # YENİ
            staff.can_edit_all_offers = request.POST.get("can_edit_all_offers") == "on"
            staff.can_delete_own_offer = request.POST.get("can_delete_own_offer") == "on"
            staff.can_delete_all_offers = request.POST.get("can_delete_all_offers") == "on"
            staff.can_send_offer = request.POST.get("can_send_offer") == "on"
            staff.can_view_all_offers = request.POST.get("can_view_all_offers") == "on"
            staff.can_approve_high_value_offers = request.POST.get("can_approve_high_value_offers") == "on"
            staff.can_invite_staff = request.POST.get("can_invite_staff") == "on"
            staff.can_manage_staff_permissions = request.POST.get("can_manage_staff_permissions") == "on"
            staff.can_activate_deactivate_staff = request.POST.get("can_activate_deactivate_staff") == "on"
            staff.can_promote_to_manager = request.POST.get("can_promote_to_manager") == "on"
            staff.can_view_reports = request.POST.get("can_view_reports") == "on"
            staff.can_view_financial_data = request.POST.get("can_view_financial_data") == "on"
            staff.can_export_data = request.POST.get("can_export_data") == "on"
        
        elif request.user.role == 'eczane':
            # Eczane yetkileri
            staff.can_approve_pharmacy_offers = request.POST.get("can_approve_pharmacy_offers") == "on"
            staff.can_reject_pharmacy_offers = request.POST.get("can_reject_pharmacy_offers") == "on"
            staff.can_approve_high_value_pharmacy_offers = request.POST.get("can_approve_high_value_pharmacy_offers") == "on"
            staff.can_apply_discount = request.POST.get("can_apply_discount") == "on"
            staff.can_apply_high_discount = request.POST.get("can_apply_high_discount") == "on"
            staff.can_enter_invoice = request.POST.get("can_enter_invoice") == "on"
            staff.can_approve_invoice_revision = request.POST.get("can_approve_invoice_revision") == "on"
            staff.can_edit_invoice = request.POST.get("can_edit_invoice") == "on"
            staff.can_approve_pharmacy_staff = request.POST.get("can_approve_pharmacy_staff") == "on"
            staff.can_manage_pharmacy_staff = request.POST.get("can_manage_pharmacy_staff") == "on"
            staff.can_manage_pharmacy_staff = request.POST.get("can_manage_pharmacy_staff") == "on"
            staff.can_update_product_prices = request.POST.get("can_update_product_prices") == "on"  # YENİ
        
        staff.save()
        
        messages.success(request, f"{staff.get_full_name()} yetkiler güncellendi.")
        return redirect("my_staff" if request.user.role == 'firma' else "pharmacist_staff_list")
    
    return render(request, "accounts/edit_staff_permissions.html", {
        "staff": staff
    })


@login_required
def toggle_staff_status(request, user_id):
    """Personeli aktif/pasif yap"""
    
    if not request.user.is_manager:
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect("my_staff" if request.user.role == 'firma' else "pharmacist_staff_list")
    
    staff = get_object_or_404(User, id=user_id)
    
    # Sadece kendi personelini düzenleyebilir
    if staff.manager != request.user:
        messages.error(request, "Bu personel size bağlı değil.")
        return redirect("my_staff" if request.user.role == 'firma' else "pharmacist_staff_list")
    
    # Durumu değiştir
    staff.is_active_user = not staff.is_active_user
    staff.save()
    
    status_text = "aktif" if staff.is_active_user else "pasif"
    messages.success(request, f"{staff.get_full_name()} {status_text} yapıldı.")
    
    return redirect(request.META.get('HTTP_REFERER', 'my_staff'))

"""
Bu kodu products/views.py dosyasına ekleyin veya mevcut admin_dashboard'ı güncelleyin
"""

@login_required
def admin_dashboard(request):
    """Admin/Superadmin dashboard - Tüm sistem istatistikleri"""
    
    # Sadece admin ve superadmin erişebilir
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        return redirect("redirect_after_login")
    
    # Kullanıcı istatistikleri
    total_users = User.objects.count()
    firma_users = User.objects.filter(role='firma').count()
    eczane_users = User.objects.filter(role='eczane').count()
    pending_approvals = User.objects.filter(is_approved=False).count()
    
    # Firma yöneticileri ve personelleri
    firma_managers = User.objects.filter(role='firma', is_manager=True).count()
    firma_staff = User.objects.filter(role='firma', is_manager=False).count()
    
    # Eczane eczacıları ve personelleri
    eczane_managers = User.objects.filter(role='eczane', is_manager=True).count()
    eczane_staff = User.objects.filter(role='eczane', is_manager=False).count()
    
    # Teklif istatistikleri
    total_offers = Offer.objects.count()
    sent_offers = Offer.objects.filter(status='sent').count()
    approved_offers = Offer.objects.filter(status='approved').count()
    rejected_offers = Offer.objects.filter(status='rejected').count()
    
    # Yüksek tutarlı teklifler
    from decimal import Decimal
    high_value_offers = Offer.objects.filter(gross_total_price__gte=Decimal('50000')).count()
    
    # Bekleyen onaylar (firma tarafı)
    pending_manager_approvals = Offer.objects.filter(manager_approval_pending=True).count()
    
    # Son aktiviteler (opsiyonel)
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_offers = Offer.objects.order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'firma_users': firma_users,
        'eczane_users': eczane_users,
        'pending_approvals': pending_approvals,
        'firma_managers': firma_managers,
        'firma_staff': firma_staff,
        'eczane_managers': eczane_managers,
        'eczane_staff': eczane_staff,
        'total_offers': total_offers,
        'sent_offers': sent_offers,
        'approved_offers': approved_offers,
        'rejected_offers': rejected_offers,
        'high_value_offers': high_value_offers,
        'pending_manager_approvals': pending_manager_approvals,
        'recent_users': recent_users,
        'recent_offers': recent_offers,
    }
    
    return render(request, 'admin/admin_dashboard.html', context)

"""
Bu kodları accounts/views.py dosyasının SONUNA ekleyin
"""

from accounts.models import Address

@login_required
def address_list(request):
    """Kullanıcının adreslerini listele"""
    
    # Sadece firma kullanıcıları adres ekleyebilir
    if request.user.role != 'firma':
        messages.error(request, "Sadece firma kullanıcıları adres yönetebilir.")
        return redirect('profile')
    
    addresses = Address.objects.filter(user=request.user)
    
    return render(request, 'accounts/address_list.html', {
        'addresses': addresses
    })


@login_required
def address_create(request):
    """Yeni adres ekle"""
    
    if request.user.role != 'firma':
        messages.error(request, "Sadece firma kullanıcıları adres ekleyebilir.")
        return redirect('profile')
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        address_type = request.POST.get('address_type', 'branch')
        address_line = request.POST.get('address_line', '').strip()
        city = request.POST.get('city', '').strip()
        district = request.POST.get('district', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        contact_person = request.POST.get('contact_person', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        notes = request.POST.get('notes', '').strip()
        is_default = request.POST.get('is_default') == 'on'
        
        # Doğrulama
        if not title or not address_line or not city:
            messages.error(request, "Adres başlığı, adres ve il alanları zorunludur.")
            return render(request, 'accounts/address_form.html')
        
        # Adres oluştur
        address = Address.objects.create(
            user=request.user,
            title=title,
            address_type=address_type,
            address_line=address_line,
            city=city,
            district=district,
            postal_code=postal_code,
            contact_person=contact_person,
            phone=phone,
            email=email,
            notes=notes,
            is_default=is_default
        )
        
        messages.success(request, f"{title} adresi eklendi.")
        return redirect('address_list')
    
    return render(request, 'accounts/address_form.html')


@login_required
def address_edit(request, address_id):
    """Adresi düzenle"""
    
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.title = request.POST.get('title', '').strip()
        address.address_type = request.POST.get('address_type', 'branch')
        address.address_line = request.POST.get('address_line', '').strip()
        address.city = request.POST.get('city', '').strip()
        address.district = request.POST.get('district', '').strip()
        address.postal_code = request.POST.get('postal_code', '').strip()
        address.contact_person = request.POST.get('contact_person', '').strip()
        address.phone = request.POST.get('phone', '').strip()
        address.email = request.POST.get('email', '').strip()
        address.notes = request.POST.get('notes', '').strip()
        address.is_default = request.POST.get('is_default') == 'on'
        
        # Doğrulama
        if not address.title or not address.address_line or not address.city:
            messages.error(request, "Adres başlığı, adres ve il alanları zorunludur.")
            return render(request, 'accounts/address_form.html', {'address': address})
        
        address.save()
        
        messages.success(request, f"{address.title} adresi güncellendi.")
        return redirect('address_list')
    
    return render(request, 'accounts/address_form.html', {'address': address})


@login_required
def address_delete(request, address_id):
    """Adresi sil"""
    
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        title = address.title
        address.delete()
        messages.success(request, f"{title} adresi silindi.")
    
    return redirect('address_list')


@login_required
def address_set_default(request, address_id):
    """Adresi varsayılan yap"""
    
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Diğer varsayılanları kaldır
    Address.objects.filter(user=request.user).update(is_default=False)
    
    # Bu adresi varsayılan yap
    address.is_default = True
    address.save()
    
    messages.success(request, f"{address.title} varsayılan adres yapıldı.")
    return redirect('address_list')

"""
Bu kodları products/views.py dosyasının SONUNA ekleyin
"""

from django.core.files.storage import FileSystemStorage
import openpyxl
from decimal import Decimal

@login_required
def pharmacy_product_management(request):
    """Eczane ürün yönetimi - sadece eczacı veya yetkili personel"""
    
    # Sadece eczane kullanıcıları
    if request.user.role != 'eczane':
        messages.error(request, "Bu sayfaya sadece eczane kullanıcıları erişebilir.")
        return redirect('redirect_after_login')
    
    # Yetki kontrolü
    if not request.user.is_manager and not request.user.can_manage_products:
        messages.error(request, "Ürün yönetimi yetkiniz yok.")
        return redirect('pharmacy_dashboard')
    
    products = Product.objects.all().order_by('-created_at')
    
    return render(request, 'products/pharmacy_product_management.html', {
        'products': products,
        'can_add': True,
        'can_delete': request.user.is_superuser or request.user.is_staff,
    })


@login_required
def pharmacy_add_product(request):
    """Tek ürün ekleme"""
    
    # Yetki kontrolü
    if request.user.role != 'eczane':
        messages.error(request, "Bu sayfaya sadece eczane kullanıcıları erişebilir.")
        return redirect('redirect_after_login')
    
    if not request.user.is_manager and not request.user.can_manage_products:
        messages.error(request, "Ürün ekleme yetkiniz yok.")
        return redirect('pharmacy_dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        barcode = request.POST.get('barcode', '').strip()
        unit_price_str = request.POST.get('unit_price', '0').replace(',', '.')
        vat_rate_str = request.POST.get('vat_rate', '10').replace(',', '.')
        
        try:
            unit_price = Decimal(unit_price_str)
            vat_rate = Decimal(vat_rate_str)
        except:
            messages.error(request, "Geçersiz fiyat veya KDV oranı.")
            return render(request, 'products/pharmacy_add_product.html')
        
        if not name:
            messages.error(request, "Ürün adı zorunludur.")
            return render(request, 'products/pharmacy_add_product.html')
        
        # Ürün oluştur
        Product.objects.create(
            name=name,
            barcode=barcode,
            unit_price=unit_price,
            vat_rate=vat_rate
        )
        
        messages.success(request, f"{name} ürünü eklendi.")
        return redirect('pharmacy_product_management')
    
    return render(request, 'products/pharmacy_add_product.html')


@login_required
def pharmacy_import_products_excel(request):
    """Excel ile toplu ürün ekleme"""
    
    # Yetki kontrolü
    if request.user.role != 'eczane':
        messages.error(request, "Bu sayfaya sadece eczane kullanıcıları erişebilir.")
        return redirect('redirect_after_login')
    
    if not request.user.is_manager and not request.user.can_manage_products:
        messages.error(request, "Ürün ekleme yetkiniz yok.")
        return redirect('pharmacy_dashboard')
    
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        try:
            # Excel dosyasını oku
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            
            added_count = 0
            error_count = 0
            
            # Satırları oku (başlık satırını atla)
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row[0]:  # Ürün adı boşsa atla
                    continue
                
                try:
                    name = str(row[0]).strip()
                    barcode = str(row[1]).strip() if row[1] else ''
                    unit_price = Decimal(str(row[2]).replace(',', '.')) if row[2] else Decimal('0')
                    vat_rate = Decimal(str(row[3]).replace(',', '.')) if row[3] else Decimal('10')
                    
                    Product.objects.create(
                        name=name,
                        barcode=barcode,
                        unit_price=unit_price,
                        vat_rate=vat_rate
                    )
                    added_count += 1
                except Exception as e:
                    error_count += 1
                    continue
            
            if added_count > 0:
                messages.success(request, f"{added_count} ürün başarıyla eklendi.")
            if error_count > 0:
                messages.warning(request, f"{error_count} ürün eklenirken hata oluştu.")
            
            return redirect('pharmacy_product_management')
            
        except Exception as e:
            messages.error(request, f"Excel dosyası işlenirken hata: {str(e)}")
    
    return render(request, 'products/pharmacy_import_excel.html')


@login_required
def pharmacy_delete_product(request, product_id):
    """Ürün silme - sadece admin"""
    
    # Sadece admin silebilir
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, "Ürün silme yetkiniz yok. Sadece admin silebilir.")
        return redirect('pharmacy_product_management')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"{name} ürünü silindi.")
    
    return redirect('pharmacy_product_management')