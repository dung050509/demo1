from django.urls import path

from teatwitter.teacrawler.api.views import save_chart, upload_image
app_name = "teacrawler_api_chart"
urlpatterns = [
    path('chart', save_chart, name='save_chart'),
    path('upload-image', upload_image, name='upload_image'),
]
