from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.html import format_html

from .models import PDFUpload, SubjectPDF, Favorite


# ==========================================================
# PDF UPLOAD ACTION
# ==========================================================

@admin.action(
    description="🗑 Delete selected papers"
)
def delete_selected_papers(
    modeladmin,
    request,
    queryset
):

    for obj in queryset:

        if obj.pdf_file:

            try:
                obj.pdf_file.delete(
                    save=False
                )
            except Exception:
                pass

        obj.delete()


# ==========================================================
# PDFUpload ADMIN
# ==========================================================

@admin.register(PDFUpload)
class PDFUploadAdmin(admin.ModelAdmin):

    actions = [
        delete_selected_papers
    ]

    list_display = (
        "id",
        "semester",
        "subject",
        "pdf_file",
        "uploaded_at",
    )

    list_filter = (
        "semester",
        "subject",
        "uploaded_at",
    )

    search_fields = (
        "subject",
        "pdf_file",
    )

    readonly_fields = (
        "uploaded_at",
    )

    ordering = (
        "-uploaded_at",
    )


# ==========================================================
# SubjectPDF ADMIN
# ==========================================================

@admin.register(SubjectPDF)
class SubjectPDFAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "department",
        "semester",
        "subject",
        "uploaded_by",
        "download_count",
        "preview_pdf",
        "download_pdf",
        "uploaded_at",
    )

    list_display_links = (
        "id",
        "subject",
    )

    list_filter = (
        "department",
        "semester",
        "uploaded_at",
    )

    search_fields = (
        "subject",
        "department",
        "slug",
        "uploaded_by__username",
    )

    ordering = (
        "-uploaded_at",
    )

    readonly_fields = (
        "uploaded_at",
        "slug",
        "download_count",
        "uploaded_by",
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
            "📊 Statistics",
            {
                "fields": (
                    "download_count",
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

        if not obj.pdf_file:
            return "-"

        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">'
            '📄 View PDF'
            '</a>',
            obj.pdf_file.url,
        )

    preview_pdf.short_description = "Preview"

    def download_pdf(self, obj):

        if not obj.pdf_file:
            return "-"

        return format_html(
            '<a href="{}" download>'
            '⬇ Download'
            '</a>',
            obj.pdf_file.url,
        )

    download_pdf.short_description = "Download"


# ==========================================================
# FAVORITE ADMIN
# ==========================================================

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


# ==========================================================
# USER ADMIN
# ==========================================================

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


# ==========================================================
# GROUP ADMIN
# ==========================================================

admin.site.unregister(Group)


@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):

    list_display = (
        "name",
        "member_count",
        "member_list",
    )

    search_fields = (
        "name",
        "user__username",
    )

    def member_count(self, obj):

        return obj.user_set.count()

    member_count.short_description = "Members"

    def member_list(self, obj):

        users = obj.user_set.all()

        if not users.exists():
            return "-"

        return ", ".join(
            user.username
            for user in users
        )

    member_list.short_description = "Teachers"


# ==========================================================
# ADMIN SITE
# ==========================================================

admin.site.site_header = (
    "CTS Question Paper Admin"
)

admin.site.site_title = (
    "CTS Admin"
)

admin.site.index_title = (
    "📚 CTS Question Paper Management"
)