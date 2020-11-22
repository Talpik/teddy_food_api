from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _


class UserRoles(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class Gender(models.TextChoices):
    MALE = 'male'
    FEMALE = 'female'


class FamilyOfAnimal(models.TextChoices):
    CAT = 'cat'
    DOG = 'dog'
    SNAKE = 'snake'


class Currency(models.TextChoices):
    RUB = 'rub'
    USD = 'usd'
    EUR = 'eur'


class User(AbstractUser):
    """
    This is custom class for create User model, where email field instead
    username field.
    """

    username = models.CharField(_('username'),
                                max_length=30,
                                blank=True,
                                unique=True)
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(max_length=500, blank=True)
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=10,
        choices=UserRoles.choices,
        default=UserRoles.USER,
    )
    confirmation_code = models.CharField(max_length=10, default='FOOBAR')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', )

    @property
    def is_admin(self):
        """
        Function for quick change property 'role' of User model.
        """
        return (self.role == UserRoles.ADMIN or self.is_superuser
                or self.is_staff)

    @property
    def is_moderator(self):
        """
        Function for quick change property 'role' of User model.
        """
        return self.role == UserRoles.MODERATOR

    def get_full_name(self):
        """
        Function for concatinate full name of user, use firlst and last name.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()


class Country(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=300)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Town(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=300)
    country = models.ForeignKey(
        Country,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='towns'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Shelter(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=300)
    town = models.ForeignKey(
        Town,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='shelters'
    )
    adress = models.CharField(max_length=300)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Pet(models.Model):
    family = models.CharField(
        verbose_name='Род питомца',
        max_length=20,
        choices=FamilyOfAnimal.choices,
        default=None
    )
    name = models.CharField(max_length=200)
    birthday = models.DateTimeField('День рождения', db_index=True)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    gender = models.CharField(
        verbose_name='Пол питомца',
        max_length=10,
        choices=Gender.choices,
        default=Gender.MALE
    )
    slug = models.SlugField(unique=True, max_length=300)
    breed = models.CharField(
        verbose_name='Порода питомца',
        max_length=100,
        default='Без породы'
    )
    shelter = models.ForeignKey(
        Shelter,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='pets'
    )
    taken_home = models.BooleanField(default=False)
    in_favorites = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True
    )
    take_a_walk = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True
    )
    take_a_home = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True
    )
    visit_counter = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True
    )

    @property
    def rating(self):
        """
        Calculate rating of pet
        :return:
        """
        result = self.in_favorites * 0.3 + self.take_a_home * 0.2 + self.take_a_walk * 0.2 + self.visit_counter * 0.3
        return None if result is None else int(result)

    class Meta:
        ordering = ['in_favorites']

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=300)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Transaction(models.Model):
    USD_RATE = 76.12
    EURO_RATE = 89.54
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='transactions'
    )
    pet = models.ForeignKey(
        Pet,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='transactions'
    )
    service = models.ForeignKey(
        Service,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='transactions'
    )
    donation = models.FloatField(null=False, blank=True, db_index=True)
    currency = models.CharField(
        verbose_name='Код валюты',
        max_length=3,
        choices=Currency.choices,
        default=Currency.RUB
    )

    class Meta:
        ordering = ['donation']

    def __str__(self):
        """This method convert currency

        As an argument, the method takes a string with 3 three values:
        'rub', 'usd', 'eur'
        """

        conversion = {
            'rub': (1, 'руб'),
            'usd': (self.USD_RATE, 'USD'),
            'eur': (self.EURO_RATE, 'Euro')
        }
        exchange_rate, currency_code = conversion[self.currency]
        balance = self.donation / exchange_rate
        balance = round(balance, 2)
        return f"Sum of donation: {balance} {currency_code}"







