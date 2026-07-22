from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.http import HttpResponse

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

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="main/password_reset.html"
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="main/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="main/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="main/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    path("contact/", views.contact, name="contact"),
    path("delete-account/", views.delete_account, name="delete_account"),
    path("logout/", views.logout_user, name="logout"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("download/<slug:slug>/", views.download_pdf, name="download_pdf"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("test/", lambda request: HttpResponse("WORKING")),
]