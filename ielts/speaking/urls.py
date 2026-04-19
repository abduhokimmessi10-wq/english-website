from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('practice/<int:part>/', views.practice_page, name='practice'),
    path('results/<int:session_id>/', views.results_page, name='results'),

    path('api/questions/<int:part>/', views.api_questions, name='api-questions'),
    path('api/session/start/', views.api_session_start, name='api-session-start'),
    path('api/session/<int:session_id>/complete/', views.api_session_complete, name='api-session-complete'),
    path('api/answer/submit/', views.api_submit_answer, name='api-submit-answer'),
    path('api/history/', views.api_history, name='api-history'),
]
