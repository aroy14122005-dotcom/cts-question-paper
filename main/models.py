from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

import os


class PDFUpload(models.Model):
    """
    Legacy PDF model.

    বর্তমানে নতুন upload-এর জন্য SubjectPDF ব্যবহার করা হচ্ছে।
    পুরোনো database record থাকলে এই model রাখা হয়েছে।
    """

    semester = models.IntegerField()

    subject = models.CharField(
        max_length=150,
        default="General"
    )

    pdf_file = models.FileField(
        upload_to="pdfs/"
    )

    uploaded_at = models.DateTimeField(
        default=timezone.now
    )

    def __str__(self):
        return os.path.basename(
            self.pdf_file.name
        )


class SubjectPDF(models.Model):

    department = models.CharField(
        max_length=100
    )

    semester = models.IntegerField()

    subject = models.CharField(
        max_length=150
    )

    pdf_file = models.FileField(
        upload_to="subject_pdfs/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    download_count = models.PositiveIntegerField(
        default=0
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_papers"
    )

    slug = models.SlugField(
        max_length=200,
        blank=True,
        unique=True
    )

    def save(self, *args, **kwargs):

        # ==================================================
        # FIRST SAVE
        # ==================================================

        if not self.pk:

            # First save creates the database ID.
            super().save(*args, **kwargs)

            # Create base slug.
            base_slug = slugify(
                f"{self.department}-semester-{self.semester}-{self.subject}"
            )

            # Add primary key to guarantee uniqueness.
            self.slug = f"{base_slug}-{self.pk}"

            # Save only slug.
            super().save(
                update_fields=["slug"]
            )

            return

        # ==================================================
        # EXISTING OBJECT
        # ==================================================

        if not self.slug:

            base_slug = slugify(
                f"{self.department}-semester-{self.semester}-{self.subject}"
            )

            self.slug = f"{base_slug}-{self.pk}"

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.department} - "
            f"Sem {self.semester} - "
            f"{self.subject}"
        )


class Favorite(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    paper = models.ForeignKey(
        SubjectPDF,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["user", "paper"],
                name="unique_user_favorite_paper"
            )
        ]

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.paper.subject}"
        )