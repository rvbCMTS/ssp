from django.urls import path
from .views import index, register_exam_form, api_save_new_exam, yearly_reports, ssm_plots, data_cleaning,\
    api_save_clean_data

app_name = 'fluoro_times'
urlpatterns = [
    path('', index, name='index'),
    path('registrera_us/', register_exam_form, name='register'),
    path('ssm_plottar/', ssm_plots, name='ssm-plots'),
    path('arsrapporter/', yearly_reports, name='yearly-reports'),
    path('datastad/', data_cleaning, name='data-clean'),
    path('api/save_new_exam/', api_save_new_exam, name='save_exam'),
    path('api/save_clean_data/', api_save_clean_data, name='save_clean_data'),
]
