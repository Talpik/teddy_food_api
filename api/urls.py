from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import UserViewSet, get_jwt_token, send_confirm_code
from .views import CountryViewSet, TownViewSet, SheltersViewSet, PetViewSet, TransactionViewSet

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'countries', CountryViewSet, basename='country')
router_v1.register(r'towns', TownViewSet, basename='town')
router_v1.register(r'shelters', SheltersViewSet, basename='shelter')
router_v1.register(r'pets', PetViewSet, basename='pet')
router_v1.register(r'transactions', TransactionViewSet, basename='transaction')

v1_auth_patterns = [
    path('token/', get_jwt_token, name='get_token'),
    path('email/', send_confirm_code, name='send_email'),
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(v1_auth_patterns)),
]

