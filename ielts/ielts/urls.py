from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('speaking.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()
try:
    # Bu yerga o'zingiz xohlagan login va parolni yozing
    User.objects.create_superuser('nakata', 'nakata@example.com', 'nakata')
    print("Superuser muvaffaqiyatli yaratildi!")
except IntegrityError:
    print("Superuser allaqachon mavjud.")
except Exception as e:
    print(f"Xato: {e}")