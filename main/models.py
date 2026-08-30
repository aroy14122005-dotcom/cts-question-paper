from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

import os


# ==========================================================
# LEGACY PDF MODEL
# ==========================================================

class PDFUpload(models.Model):

    """
    Legacy PDF model.

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


# ==========================================================
# OLD SUBJECT PDF MODEL
# ==========================================================

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

            super().save(*args, **kwargs)

            base_slug = slugify(
                f"{self.department}-semester-{self.semester}-{self.subject}"
            )

            self.slug = f"{base_slug}-{self.pk}"

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


# ==========================================================
# PREVIOUS YEAR QUESTION PAPER
# ==========================================================
#
# Semester 1–6 এর Previous Year Question Papers
#
# এই model-এর data Browse Subjects-এর data থেকে
# সম্পূর্ণ আলাদা থাকবে।
# ==========================================================

class PreviousYearPaper(models.Model):

    department = models.CharField(
        max_length=100
    )

    semester = models.IntegerField()

    subject = models.CharField(
        max_length=150
    )

    pdf_file = models.FileField(
        upload_to="previous_year_papers/"
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
        related_name="uploaded_previous_year_papers"
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

            super().save(*args, **kwargs)

            base_slug = slugify(
                f"{self.department}-semester-{self.semester}-{self.subject}-pyq"
            )

            self.slug = f"{base_slug}-{self.pk}"

            super().save(
                update_fields=["slug"]
            )

            return

        # ==================================================
        # EXISTING OBJECT
        # ==================================================

        if not self.slug:

            base_slug = slugify(
                f"{self.department}-semester-{self.semester}-{self.subject}-pyq"
            )

            self.slug = f"{base_slug}-{self.pk}"

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.department} - "
            f"Sem {self.semester} - "
            f"{self.subject}"
        )


# ==========================================================
# SUBJECT MATERIAL
# ==========================================================
#
# Browse Subjects-এর জন্য:
#
# Syllabus
# Unit 1
# Unit 2
# Unit 3
# Notes
# Questions
#
# এগুলো PreviousYearPaper-এর সঙ্গে আলাদা থাকবে।
# ==========================================================

class SubjectMaterial(models.Model):

    MATERIAL_TYPES = [

        (
            "syllabus",
            "Syllabus"
        ),

        (
            "unit",
            "Unit"
        ),

        (
            "notes",
            "Notes"
        ),

        (
            "questions",
            "Questions"
        ),

    ]

    department = models.CharField(
        max_length=100
    )

    semester = models.IntegerField()

    subject = models.CharField(
        max_length=150
    )

    material_type = models.CharField(
        max_length=20,
        choices=MATERIAL_TYPES
    )

    unit_number = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    title = models.CharField(
        max_length=200
    )

    pdf_file = models.FileField(
        upload_to="subject_materials/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_subject_materials"
    )

    download_count = models.PositiveIntegerField(
        default=0
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

            super().save(*args, **kwargs)

            base_slug = slugify(
                f"{self.department}-semester-{self.semester}-{self.subject}-{self.title}"
            )

            self.slug = f"{base_slug}-{self.pk}"

            super().save(
                update_fields=["slug"]
            )

            return

        # ==================================================
        # EXISTING OBJECT
        # ==================================================

        if not self.slug:

            base_slug = slugify(
                f"{self.department}-semester-{self.semester}-{self.subject}-{self.title}"
            )

            self.slug = f"{base_slug}-{self.pk}"

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.department} - "
            f"Sem {self.semester} - "
            f"{self.subject} - "
            f"{self.title}"
        )


# ==========================================================
# FAVORITE
# ==========================================================

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
                fields=[
                    "user",
                    "paper"
                ],
                name="unique_user_favorite_paper"
            )

        ]

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.paper.subject}"
        )