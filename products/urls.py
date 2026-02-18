from django.urls import path
from . import views

urlpatterns = [
    path("pharmacy/dashboard/", views.pharmacy_dashboard, name="pharmacy_dashboard"),
    path("", views.product_list, name="product_list"),
    path("offer/", views.offer_view, name="offer"),
    path("add/<int:product_id>/", views.add_to_offer, name="add_to_offer"),
    path("send/", views.send_offer_to_pharmacy, name="send_offer_to_pharmacy"),
    path("pharmacy/inbox/", views.pharmacy_inbox, name="pharmacy_inbox"),
    path("pharmacy/offers/<int:offer_id>/", views.pharmacy_offer_detail, name="pharmacy_offer_detail"),
    path("pharmacy/offers/<int:offer_id>/approve/", views.pharmacy_approve_offer, name="pharmacy_approve_offer"),
    path("pharmacy/offers/<int:offer_id>/reject/", views.pharmacy_reject_offer, name="pharmacy_reject_offer"),
    path("pharmacy/offers/<int:offer_id>/discounts/", views.pharmacy_update_discounts, name="pharmacy_update_discounts"),
    path("pharmacy/offers/<int:offer_id>/invoice/", views.pharmacy_update_invoice, name="pharmacy_update_invoice"),
    path("pharmacy/offers/<int:offer_id>/invoice/revision-request/", views.pharmacy_request_invoice_revision, name="pharmacy_request_invoice_revision"),
    path("pharmacy/offers/<int:offer_id>/invoice/revision-approve/", views.pharmacy_approve_invoice_revision, name="pharmacy_approve_invoice_revision"),
    path("pharmacy/offers/<int:offer_id>/invoice/revision-reject/", views.pharmacy_reject_invoice_revision, name="pharmacy_reject_invoice_revision"),
    path("my-offers/", views.my_offers, name="my_offers"),
    path("my-offers/<int:offer_id>/", views.my_offer_detail, name="my_offer_detail"),
    path("offer/revise/<int:offer_id>/", views.revise_offer, name="revise_offer"),
    path("offer/history/<int:offer_id>/", views.view_offer_history, name="view_offer_history"),
    path("offer/item/<int:item_id>/delete/", views.delete_offer_item, name="delete_offer_item"),
    path("offer/item/<int:item_id>/update/", views.update_offer_item, name="update_offer_item"),
    # Filtrelenmiş teklif listeleri
    path("pharmacy/offers/<str:status>/", views.pharmacy_offers_by_status, name="pharmacy_offers_by_status"),
    path("my-offers/<str:status>/", views.my_offers_by_status, name="my_offers_by_status"),
    # Admin dashboard
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("favorites/products/", views.favorite_products, name="favorite_products"),
    path("favorites/products/toggle/<int:product_id>/", views.toggle_favorite_product, name="toggle_favorite_product"),
    path("favorites/drafts/", views.favorite_drafts, name="favorite_drafts"),
    path("favorites/drafts/toggle/<int:offer_id>/", views.toggle_favorite_draft, name="toggle_favorite_draft"),
    # Kullanıcı Yönetimi
    path("admin/users/", views.admin_users, name="admin_users"),
    path("admin/users/<int:user_id>/approve/", views.admin_user_approve, name="admin_user_approve"),
    path("admin/users/<int:user_id>/reject/", views.admin_user_reject, name="admin_user_reject"),
    path("admin/users/<int:user_id>/delete/", views.admin_user_delete, name="admin_user_delete"),
    path("admin/users/<int:user_id>/edit/", views.admin_user_edit, name="admin_user_edit"),
    # Yönetici Onay Sistemi
    path("offers/<int:offer_id>/manager-approve/", views.manager_approve_offer, name="manager_approve_offer"),
    path("offers/<int:offer_id>/manager-reject/", views.manager_reject_offer, name="manager_reject_offer"),
    # Yönetici Onay Sistemi
    path("offers/<int:offer_id>/manager-approve/", views.manager_approve_offer, name="manager_approve_offer"),
    path("offers/<int:offer_id>/manager-reject/", views.manager_reject_offer, name="manager_reject_offer"),

    # Bildirim Sistemi
    path("notifications/<int:notification_id>/mark-read/", views.mark_notification_read, name="mark_notification_read"),
    path("notifications/mark-all-read/", views.mark_all_notifications_read, name="mark_all_notifications_read"),
    path('offers/<int:offer_id>/assign-addresses/', views.assign_delivery_addresses, name='assign_delivery_addresses'),
    path('test-navbar/', views.test_navbar, name='test_navbar'),

    # Eczane Ürün Yönetimi
path('pharmacy/products/', views.pharmacy_product_management, name='pharmacy_product_management'),
path('pharmacy/products/add/', views.pharmacy_add_product, name='pharmacy_add_product'),
path('pharmacy/products/import-excel/', views.pharmacy_import_products_excel, name='pharmacy_import_products_excel'),
path('pharmacy/products/<int:product_id>/delete/', views.pharmacy_delete_product, name='pharmacy_delete_product'),
path('pharmacy/products/<int:product_id>/edit/', views.pharmacy_edit_product, name='pharmacy_edit_product'),
path('pharmacy/products/<int:product_id>/update-price/', views.pharmacy_update_product_price, name='pharmacy_update_product_price'),

# Dışa Aktarma
path('export/offers/', views.export_offers_excel, name='export_offers_excel'),
path('export/products/', views.export_products_excel, name='export_products_excel'),
path('export/staff/', views.export_staff_excel, name='export_staff_excel'),

path('export/offer/<int:offer_id>/excel/', views.export_offer_excel, name='export_offer_excel'),
path('export/offer/<int:offer_id>/pdf/', views.export_offer_pdf, name='export_offer_pdf'),

]
