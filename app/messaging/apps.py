from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MessagingConfig(AppConfig):
    name = 'messaging'
    verbose_name = _('messaging')

    def ready(self):
        import messaging.signals
