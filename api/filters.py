from django_filters import rest_framework as filters

from .models import Pet


class PetFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='contains'
    )
    gender = filters.CharFilter(
        field_name='gender',
        lookup_expr='contains'
    )
    family = filters.CharFilter(
        field_name='family',
        lookup_expr='contains'
    )
    town = filters.CharFilter(
        field_name='town__slug',
        lookup_expr='contains'
    )
    country = filters.CharFilter(
        field_name='country__slug',
        lookup_expr='contains'
    )

    class Meta:
        model = Pet
        fields = ['name', 'gender', 'family', 'town', 'country']
