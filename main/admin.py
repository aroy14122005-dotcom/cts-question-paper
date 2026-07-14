from django.contrib import admin
from .models import PDFUpload, SubjectPDF, Favorite
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse


@admin.action(description="🗑 Delete selected papers")
def delete_selected_papers(modeladmin, request, queryset):
    queryset.delete()

@admin.register(PDFUpload)
class PDFUploadAdmin(admin.ModelAdmin):

    actions = [
       "delete_selected_papers",
    ]
    
    list_display = (
        "id",
        "semester",
        "pdf_file",
    )

    list_filter = (
        "semester",
    )

    search_fields = (
        "pdf_file",
    )


@admin.register(SubjectPDF)
class SubjectPDFAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "department",
        "semester",
        "subject",
        "uploaded_by",
        "preview_pdf",
        "download_pdf",
        "uploaded_at",
    )

    list_filter = (
        "department",
        "semester",
        "uploaded_at",
    )

    list_display_links = (
        "id",
        "subject",
    )

    search_fields = (
        "subject",
        "department",
    )

    ordering = (
        "-uploaded_at",
    )

    readonly_fields = (
        "uploaded_at",
        "slug",
    )

    fieldsets = (
    (
        "📚 Paper Information",
        {
            "fields": (
                "department",
                "semester",
                "subject",
                "slug",
            )
        },
    ),
    (
        "📄 PDF",
        {
            "fields": (
                "pdf_file",
            )
        },
    ),
    (
        "👤 Upload Information",
        {
            "fields": (
                "uploaded_by",
                "uploaded_at",
            )
        },
    ),
)

    def preview_pdf(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank">📄 View PDF</a>',
                obj.pdf_file.url,
            )
        return "-"

    preview_pdf.short_description = "Preview"

    def download_pdf(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" download>⬇ Download</a>',
                obj.pdf_file.url,
            )
        return "-"

    download_pdf.short_description = "Download"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "paper",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user__username",
        "paper__subject",
        "paper__department",
    )

    ordering = (
        "-created_at",
    )


    admin.site.site_header = "CTS Question Paper Admin"
    admin.site.site_title = "CTS Admin"
    admin.site.index_title = "Welcome to CTS Question Paper Admin Panel"



    admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    ordering = (
        "username",
    )

admin.site.index_title = (
    f"""
    📄 Subject PDFs: {SubjectPDF.objects.count()} |
    📁 PDFs: {PDFUpload.objects.count()} |
    ❤️ Favorites: {Favorite.objects.count()} |
    👤 Users: {User.objects.count()}
    """
)