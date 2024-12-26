from django.apps import AppConfig

class ImageTextAnalyserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'img_txt_anal'

    def ready(self):
        import img_txt_anal.signals