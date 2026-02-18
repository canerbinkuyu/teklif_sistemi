from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),  # Dikkat: register_view olmalı
    path("register/pharmacist/", views.pharmacist_register, name="pharmacist_register"),
    path("awaiting-approval/", views.awaiting_approval, name="awaiting_approval"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("redirect/", views.redirect_after_login, name="redirect_after_login"),
    # path("password-change/", ForcedPasswordChangeView.as_view(), name="password_change"),  # YORUMA ALINDI
    path("profile/", views.profile_view, name="profile"),
     # Personel Davet Sistemi - YENİ
    path("invite-staff/", views.invite_staff, name="invite_staff"),
    path("register/staff/<str:token>/", views.staff_register, name="staff_register"),
    path("my-staff/", views.my_staff, name="my_staff"),
        # Eczane Personel Kaydı - YENİ
    path("register/pharmacy-staff/", views.pharmacy_staff_register, name="pharmacy_staff_register"),
    # Eczacı Personel Yönetimi - YENİ
    path("pharmacist/staff/", views.pharmacist_staff_list, name="pharmacist_staff_list"),
    path("pharmacist/staff/<int:user_id>/approve/", views.approve_pharmacy_staff, name="approve_pharmacy_staff"),
    path("pharmacist/staff/<int:user_id>/reject/", views.reject_pharmacy_staff, name="reject_pharmacy_staff"),
       # Yetki Yönetimi - YENİ
    path("staff/<int:user_id>/permissions/", views.edit_staff_permissions, name="edit_staff_permissions"),
    path("staff/<int:user_id>/toggle-status/", views.toggle_staff_status, name="toggle_staff_status"),
    # Adres Yönetimi - YENİ
    path("addresses/", views.address_list, name="address_list"),
    path("addresses/create/", views.address_create, name="address_create"),
    path("addresses/<int:address_id>/edit/", views.address_edit, name="address_edit"),
    path("addresses/<int:address_id>/delete/", views.address_delete, name="address_delete"),
    path("addresses/<int:address_id>/set-default/", views.address_set_default, name="address_set_default"),

]