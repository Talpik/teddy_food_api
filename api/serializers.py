from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator

from .models import Country, Town, Shelter, Pet, Transaction
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for view-class, who work with next end-points:
    1)'api/v1/users/', [GET, POST], permission=(AllowAny)
    2)'api/v1/users/{username}/', [GET, PATCH, DELETE], permission=(IsAdmin)
    3)'api/v1/users/me/', [GET, PATCH], permission=(IsOwner)
    """
    class Meta:
        model = User
        fields = (
            'bio',
            'first_name',
            'last_name',
            'username',
            'email',
            'role',
        )


class UserCreationSerializer(serializers.Serializer):
    """
    Serializer for view-class, who work with next end-points:
    'api/v1/auth/email/', [POST], permissions=(AllowAny)
    Sending confirmation_code to the transmitted email.
    """

    email = serializers.CharField()
    username = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )


class ConfirmationCodeSerializer(serializers.Serializer):
    """
    Serializer for view-class, who work with next end-points:
    'api/v1/auth/token/', [POST], permissions=(AllowAny)
    Receiving a JWT token in exchange for email and confirmation_code.
    """
    email = serializers.CharField()
    confirmation_code = serializers.CharField(allow_blank=False,
                                              write_only=True)

    class Meta:
        model = User
        fields = (
            'confirmation_code',
            'email',
        )


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        exclude = ('id',)


class CountryField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = CountrySerializer(value)
        return serializer.data


class TownSerializer(serializers.ModelSerializer):
    country = CountryField(
        slug_field='slug',
        queryset=Country.objects.all(),
        required=False
    )

    class Meta:
        model = Town
        fields = ('name', 'country')


class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = '__all__'


class PetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pet
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        exclude = ('id',)
