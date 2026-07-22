from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class PDFUpload(models.Model):
    semester = models.IntegerField()
    pdf_file = models.FileField(upload_to='pdfs/')

    def __str__(self):
        return self.pdf_file.name


class SubjectPDF(models.Model):
    department = models.CharField(max_length=100)
    semester = models.IntegerField()
    subject = models.CharField(max_length=150)
    pdf_file = models.FileField(upload_to='subject_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # 👇 নতুন field
    download_count = models.PositiveIntegerField(default=0)

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    slug = models.SlugField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.department} - Sem {self.semester} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.subject)

        super().save(*args, **kwargs)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(SubjectPDF, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "paper")

    def __str__(self):
        return f"{self.user.username} - {self.paper.subject}"