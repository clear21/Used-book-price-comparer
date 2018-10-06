from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.search_result, name='search_result'),  # url‚Æview‚ÌŒ‹‚Ñ‚Â‚¯
]