from rest_framework import routers
from .views import BlogImages, ImageListView

router = routers.DefaultRouter()
router.register(r'posts', BlogImages, basename='post')
router.register(r'images', ImageListView, basename='image')

urlpatterns = router.urls
