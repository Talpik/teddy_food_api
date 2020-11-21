from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()
models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
