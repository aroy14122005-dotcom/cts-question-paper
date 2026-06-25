from django.db import models


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

    def __str__(self):
        return f"{self.department} - Sem {self.semester} - {self.subject}"