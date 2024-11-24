from django.urls import path
from . import views

app_name = 'exam'

urlpatterns = [
    path('create/', views.create_exam, name='create_exam'),
    path('<int:exam_id>/add-question/', views.add_question, name='add_question'),
    path('<int:exam_id>/', views.exam_details, name='exam_details'),
]
urlpatterns += [
    path('<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('<int:exam_id>/results/', views.exam_results, name='exam_results'),
]

urlpatterns += [
    path('performance-report/', views.performance_report, name='performance_report'),
]
urlpatterns += [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]


