from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('home/', views.home, name='home'),
    path('semester/<str:dept_name>/', views.semester, name='semester'),

    path('upload/<int:sem_no>/', views.upload_pdf, name='upload_pdf'),

    path('delete/<int:pdf_id>/', views.delete_pdf, name='delete_pdf'),

    path('semester/<str:dept_name>/subjects/', views.subject_page, name='subject_page'),
    path('semester/<str:dept_name>/<int:sem_no>/<str:subject_name>/subject-upload/', views.subject_upload, name='subject_upload'),
    path('subject-pdf/delete/<int:pdf_id>/', views.delete_subject_pdf, name='delete_subject_pdf'),
    path("search/", views.search_page, name="search"),
    path("search-api/", views.search_api, name="search_api"),
    path("paper/<int:pdf_id>/", views.paper_detail, name="paper_detail"),
    path("favorites/", views.favorites, name="favorites"),
    path("favorite/add/<int:paper_id>/", views.add_favorite, name="add_favorite"),
    path("favorite/remove/<int:paper_id>/", views.remove_favorite, name="remove_favorite"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("change-password/", views.CustomPasswordChangeView.as_view(), name="change_password"),
    path("contact/", views.contact, name="contact"),
    path("logout/", views.logout_user, name="logout"),
]