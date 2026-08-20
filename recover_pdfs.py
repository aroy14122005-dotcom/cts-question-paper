import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from main.models import PDFUpload, SubjectPDF


print("Starting recovery...\n")


for pdf in PDFUpload.objects.filter(semester=4):

    filename = os.path.basename(pdf.pdf_file.name).lower()

    # -----------------------------
    # Find subject
    # -----------------------------

    if "computer-networks" in filename:
        subject = "Computer Networks"

    elif (
        "introduction-to-dbms" in filename
        or "introduction-dbms" in filename
    ):
        subject = "Introduction to DBMS"

    elif "ssad-software-engineering" in filename:
        subject = "Software Engineering"

    elif (
        "operating-system" in filename
        or "operating-systems" in filename
    ):
        subject = "Operating Systems"

    elif "object-oriented-programming-using-java" in filename:
        subject = "OOP using Java"

    else:
        print("SKIPPED:", pdf.id, filename)
        continue


    # -----------------------------
    # Check existing PDF
    # -----------------------------

    if SubjectPDF.objects.filter(
        pdf_file=pdf.pdf_file.name
    ).exists():

        print(
            "ALREADY EXISTS:",
            pdf.id,
            "->",
            subject
        )

        continue


    # -----------------------------
    # Recover PDF
    # -----------------------------

    recovered = SubjectPDF(
        department="cst",
        semester=4,
        subject=subject,
        pdf_file=pdf.pdf_file.name,
    )

    recovered.save()


    print(
        "RECOVERED:",
        pdf.id,
        "->",
        subject,
        "| New SubjectPDF ID:",
        recovered.id
    )


print("\nRecovery complete!")

print(
    "PDFUpload count:",
    PDFUpload.objects.count()
)

print(
    "SubjectPDF count:",
    SubjectPDF.objects.count()
)