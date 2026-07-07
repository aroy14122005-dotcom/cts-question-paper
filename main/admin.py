from django.urls import path
from . import views
from django.contrib import admin
from .models import PDFUpload, SubjectPDF, Favorite

admin.site.register(PDFUpload)
admin.site.register(SubjectPDF)
admin.site.register(Favorite)

urlpatterns = [
    path('', views.login_page, name='login'),
    path('home/', views.home, name='home'),
    path('semester/<str:dept_name>/', views.semester, name='semester'),

    path('upload/<int:sem_no>/', views.upload_pdf, name='upload_pdf'),

    path('delete/<int:pdf_id>/', views.delete_pdf, name='delete_pdf'),

    path('semester/<str:dept_name>/subjects/', views.subject_page, name='subject_page'),
    path('semester/<str:dept_name>/<int:sem_no>/<str:subject_name>/subject-upload/', views.subject_upload, name='subject_upload'),
    path('subject-pdf/delete/<int:pdf_id>/', views.delete_subject_pdf, name='delete_subject_pdf'),
]