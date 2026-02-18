from products.models import Notification


def notifications(request):
    """Her sayfada bildirimler için context"""
    if request.user.is_authenticated:
        # Önce QuerySet al, sonra slice yap
        all_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')
        
        # Unread count hesapla (slice öncesi)
        unread_count = all_notifications.filter(is_read=False).count()
        
        # Son 10 bildirimi al (slice)
        notifications_list = list(all_notifications[:10])
        
        return {
            'notifications': notifications_list,
            'unread_count': unread_count,
        }
    return {
        'notifications': [],
        'unread_count': 0,
    }