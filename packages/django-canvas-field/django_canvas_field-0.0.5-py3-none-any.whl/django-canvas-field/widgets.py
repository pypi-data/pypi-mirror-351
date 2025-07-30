from django.forms import widgets


class SignCanvasWidget(widgets.Textarea):
    template_name = 'canvas/sign_canvas.html'

