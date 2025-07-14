from django.urls import path
from . import views

app_name = 'charts'

urlpatterns = [
    path('', views.chart_view, name='chart_view'),
    path('data/', views.chart_data, name='chart_data'),
] 