from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import exceptions, filters, status, viewsets, mixins, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes

from .models import Country, Town, Shelter, Pet, Transaction, User

from .permissions import IsAdminPermissions

from .filters import PetFilter

from .serializers import UserSerializer, ConfirmationCodeSerializer, UserCreationSerializer
from .serializers import CountrySerializer, TownSerializer, ShelterSerializer, PetSerializer, TransactionSerializer


EMAIL_AUTH = 'authorization@teddyfood.fake'


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    """
    Receiving a JWT token in exchange for email and confirmation_code. 
    """

    serializer = ConfirmationCodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    email = serializer.data.get('email')
    confirmation_code = serializer.data.get('confirmation_code')
    user = get_object_or_404(User, email=email)
    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)
    return Response({'confirmation_code': 'Неверный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirm_code(request):
    """
    Sending confirmation_code to the transmitted email.
    Get or Creating an User object.
    """

    serializer = UserCreationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    username = serializer.data['username']
    user = User.objects.get_or_create(
        email=email,
        username=username,
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(subject='Yours confirmation code',
              message=f'confirmation_code: {confirmation_code}',
              from_email=EMAIL_AUTH,
              recipient_list=(email, ),
              fail_silently=False)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    1) [GET] Get list of users objects. [POST] Create user object. 'users/'
    2) [GET]Get user object by username. [PATCH] Patch user data by username.
    [DELETE] Delete user object by username. 'users/{username}/'
    3) [GET] Get your account details. [PATCH] Change your account details.
    'users/me/'
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminPermissions]
    lookup_field = 'username'

    @action(methods=['GET', 'PATCH'],
            detail=False,
            permission_classes=(IsAuthenticated, ),
            url_path='me')
    def me(self, request):
        user_profile = get_object_or_404(User, email=self.request.user.email)
        if request.method == 'GET':
            serializer = UserSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(user_profile,
                                    data=request.data,
                                    partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminPermissions]
    serializer_class = CountrySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        countries = Country.objects.all()
        return countries

#    def retrieve(self, request, *args, **kwargs):
#        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

#    def partial_update(self, request, *args, **kwargs):
#         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TownViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminPermissions]
    serializer_class = TownSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        towns = Town.objects.all()
        return towns


class SheltersViewSet(viewsets.ModelViewSet):
    queryset = Shelter.objects.all()
    permission_classes = [IsAdminPermissions]
    serializer_class = ShelterSerializer
    lookup_field = 'name'


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [IsAdminPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PetFilter


class PetViewSet(viewsets.ModelViewSet):
    """
    1) [GET] Get list of pets objects. [POST] Create pet object. 'pets/'
    2) [GET]Get pet object by pet_id. [PATCH] Patch pet data by pet_id.
    [DELETE] Delete pet object by pet_id. 'pets/{pet_id}/'
    3) [GET] Get favorite Pet account details. 'favorite/{town_id}/'
    """
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [IsAdminPermissions]
    lookup_field = 'pet_id'

    @action(methods=['GET'],
            detail=False,
            permission_classes=(AllowAny, ),
            url_path='favorite')
    def favorite(self, request):
        shelters = get_object_or_404(Town.objects.select_related(), town_id=request.data['town_id'])
        pets = get_object_or_404(shelters.pets.all()[0:10])
        serializer = PetSerializer(pets)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    1) [GET] Get list of transaction objects. [POST] Create transaction object. 'transactions/'
    2) [GET]Get transaction object by transaction_id. [PATCH] Patch transaction data by transaction_id.
    [DELETE] Delete transaction object by transaction_id. 'transactions/{transactions_id}/'
    3) [GET] Get transactions details selected by town. 'transactions/{town_id}'
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAdminPermissions]
    lookup_field = 'transaction_id'

    @action(methods=['GET'],
            detail=False,
            permission_classes=(AllowAny, ),
            url_path='transactions')
    def get_town_transactions(self, request):
        town = get_object_or_404(Town.objects.select_related(), town_id=request.data['town_id'])
        transactions = get_object_or_404(town.transactions.all()[0:10])
        serializer = TransactionSerializer(transactions)
        return Response(serializer.data, status=status.HTTP_200_OK)

