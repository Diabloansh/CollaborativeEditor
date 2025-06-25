from django.apps import AppConfig

# Configuration class for the 'hello' application
class HelloConfig(AppConfig):
    # Specifies the default type of primary key field to use for models in this app
    default_auto_field = 'django.db.models.BigAutoField'

    # Name of the app, used by Django for app management
    name = 'hello'
