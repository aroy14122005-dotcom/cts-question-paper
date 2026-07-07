from django.db import models
from django.utils.text import slugify


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

    slug = models.SlugField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.department} - Sem {self.semester} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.subject)

        super().save(*args, **kwargs)