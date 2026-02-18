from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.forms import PasswordChangeForm

# Bu kısmı daha sağlam yapmak için form yerine view’de set edeceğiz (aşağıda)
