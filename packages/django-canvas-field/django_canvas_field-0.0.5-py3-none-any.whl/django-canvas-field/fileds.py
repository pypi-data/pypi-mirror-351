from django.db import models
from .widgets import SignCanvasWidget

class SignCanvasField(models.TextField):
    def formfield(self, **kwargs: object) -> any:
        return super().formfield(**{**kwargs, 'widget': SignCanvasWidget})

