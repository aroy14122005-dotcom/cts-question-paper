import os
import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.contrib.admin.views.decorators import staff_member_required

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models import F
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .models import PDFUpload, SubjectPDF, Favorite


# ==========================================================
# SUBJECT LIST
# ==========================================================

SUBJECTS = {

    "cst": {
        1: [
            "Applied Chemistry",
            "Applied Physics I",
            "Communication Skills in English",
            "Mathematics I",
        ],
        2: [
            "Introduction to IT Systems",
            "Applied Physics II",
            "Fundamentals of Electrical & Electronics",
            "Engineering Mechanics",
            "Mathematics II",
        ],
        3: [
            "Algorithms",
            "Computer System Organization",
            "Computer Programming in C",
            "Scripting Languages Python",
            "Data Structures",
        ],
        4: [
            "Operating Systems",
            "Introduction to DBMS",
            "Software Engineering",
            "Computer Networks",
            "Object Oriented Programming using Java",
        ],
        5: [
            "Advanced Computer Network",
            "Computer Graphics",
            "Fundamentals of AI",
            "Microprocessor & Microcontroller",
            "Digital Image Processing",
            "Theory of Automata",
            "Mobile Computing",
            "Internet of Things",
        ],
        6: [
            "Cloud Computing",
            "Data Science Data Warehousing & Data Mining",
            "Web Designing",
            "Entrepreneurship & Start-ups",
            "Machine Learning",
        ],
    },

    "civil": {
        1: [
            "Applied Chemistry",
            "Applied Physics I",
            "Communication Skills in English",
            "Mathematics I",
        ],
        2: [
            "Introduction to IT Systems",
            "Applied Physics II",
            "Fundamentals of Electrical & Electronics",
            "Engineering Mechanics",
            "Mathematics II",
        ],
        3: [
            "Engineering Survey",
            "Building Materials",
            "Civil Engineering Drawing",
            "Strength of Materials",
            "Construction Technology",
        ],
        4: [
            "Structural Mechanics",
            "Concrete Technology",
            "Transportation Engineering",
            "Geotechnical Engineering",
            "Environmental Engineering",
        ],
        5: [
            "Design of Concrete Structures",
            "Estimating & Costing",
            "Irrigation Engineering",
            "Advanced Surveying",
            "Construction Management",
            "Railway Bridge & Tunnel Engineering",
        ],
        6: [
            "Design of Steel Structures",
            "Quantity Surveying & Valuation",
            "Public Health Engineering",
            "Disaster Management",
            "Entrepreneurship & Start-ups",
        ],
    },

    "electrical": {
        1: [
            "Applied Chemistry",
            "Applied Physics I",
            "Communication Skills in English",
            "Mathematics I",
        ],
        2: [
            "Introduction to IT Systems",
            "Applied Physics II",
            "Fundamentals of Electrical & Electronics",
            "Engineering Mechanics",
            "Mathematics II",
        ],
        3: [
            "Electrical Circuit Theory",
            "Electrical Machines I",
            "Basic Electronics",
            "Programming Concepts Using C",
            "Electrical Measuring Instruments",
            "Elements of Mechanical Engineering",
        ],
        4: [
            "Electrical Machines II",
            "Electrical Measurement & Control",
            "Transmission & Distribution of Electric Power",
            "Applied & Digital Electronics",
            "Power Plant Engineering",
        ],
        5: [
            "Industrial Electronics",
            "Switchgear & Protection",
            "Microprocessor & Microcontroller",
            "Utilization of Electrical Energy",
            "Electrical Design & Estimation",
            "Renewable Energy Sources",
        ],
        6: [
            "Industrial Management",
            "Instrumentation & Control",
            "Electrical Maintenance & Safety",
            "Energy Conservation & Audit",
            "Entrepreneurship & Start-ups",
        ],
    },

    "mechanical": {
        1: [
            "Applied Chemistry",
            "Applied Physics I",
            "Communication Skills in English",
            "Mathematics I",
        ],
        2: [
            "Introduction to IT Systems",
            "Applied Physics II",
            "Fundamentals of Electrical & Electronics",
            "Engineering Mechanics",
            "Mathematics II",
        ],
        3: [
            "Engineering Materials",
            "Manufacturing Processes",
            "Strength of Materials",
            "Engineering Thermodynamics",
            "Engineering Drawing & Machine Drawing",
        ],
        4: [
            "Theory of Machines",
            "Fluid Mechanics & Hydraulics",
            "Manufacturing Technology",
            "Metrology & Measurement",
            "Workshop Technology",
        ],
        5: [
            "Machine Design",
            "Thermal Engineering",
            "Production Engineering",
            "Industrial Engineering & Management",
            "CAD CAM",
            "Automobile Engineering",
        ],
        6: [
            "Refrigeration & Air Conditioning",
            "Mechatronics",
            "Power Plant Engineering",
            "Maintenance Engineering",
            "Engineering Economics & Project Management",
        ],
    },
}


# ==========================================================
# PDF VALIDATION
# ==========================================================

MAX_PDF_SIZE = 10 * 1024 * 1024


def validate_pdf_file(pdf_file):

    if not pdf_file:
        return "Please select a PDF file."

    # File size
    if pdf_file.size <= 0:
        return "The uploaded file is empty."

    if pdf_file.size > MAX_PDF_SIZE:
        return "PDF size must be 10 MB or less."

    # Extension
    filename = pdf_file.name.lower()

    if not filename.endswith(".pdf"):
        return "Only PDF files are allowed."

    # Content type check
    content_type = (
        getattr(
            pdf_file,
            "content_type",
            ""
        )
        or ""
    ).lower()

    if content_type not in (
        "application/pdf",
        "application/octet-stream",
        "",
    ):
        return "Invalid PDF file."

    # Basic PDF signature check
    try:
        current_position = pdf_file.tell()

        pdf_file.seek(0)

        file_header = pdf_file.read(5)

        pdf_file.seek(current_position)

        if file_header != b"%PDF-":
            return "The uploaded file is not a valid PDF."

    except Exception:
        return "Could not validate the PDF file."

    return None


# ==========================================================
# FILE INFORMATION
# ==========================================================

def add_file_information(pdfs):

    for pdf in pdfs:

        # ----------------------------------------------
        # Filename
        # ----------------------------------------------

        try:

            filename = os.path.basename(
                pdf.pdf_file.name
            )

            filename = os.path.splitext(
                filename
            )[0]

            pdf.filename = filename

        except Exception:

            pdf.filename = "Unknown file"


        # ----------------------------------------------
        # File size
        # ----------------------------------------------

        try:

            size = pdf.pdf_file.size

            if size < 1024:

                pdf.filesize = (
                    f"{size} B"
                )

            elif size < 1024 * 1024:

                pdf.filesize = (
                    f"{size / 1024:.1f} KB"
                )

            else:

                pdf.filesize = (
                    f"{size / (1024 * 1024):.2f} MB"
                )

        except Exception:

            pdf.filesize = "Unknown size"

    return pdfs


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@staff_member_required
def admin_dashboard(request):

    return render(
        request,
        "main/admin_dashboard.html"
    )


# ==========================================================
# LOGIN / REGISTER
# ==========================================================

def login_page(request):

    if request.method == "POST":

        form_type = request.POST.get(
            "form_type",
            ""
        ).strip()


        # ==================================================
        # REGISTER
        # ==================================================

        if form_type == "register":

            username = request.POST.get(
                "username",
                ""
            ).strip()

            email = request.POST.get(
                "email",
                ""
            ).strip()

            password = request.POST.get(
                "password",
                ""
            )


            if not username:

                messages.error(
                    request,
                    "Username is required."
                )

                return redirect(
                    "login"
                )


            if not password:

                messages.error(
                    request,
                    "Password is required."
                )

                return redirect(
                    "login"
                )


            if User.objects.filter(
                username__iexact=username
            ).exists():

                messages.error(
                    request,
                    "Username already exists."
                )

                return redirect(
                    "/?login=true"
                )


            if email and User.objects.filter(
                email__iexact=email
            ).exists():

                messages.error(
                    request,
                    "Email already exists."
                )

                return redirect(
                    "/?login=true"
                )


            User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )


            messages.success(
                request,
                "Registration successful. Please login."
            )

            return redirect(
                "/?login=true"
            )


        # ==================================================
        # LOGIN
        # ==================================================

        elif form_type == "login":

            username = request.POST.get(
                "username",
                ""
            ).strip()

            password = request.POST.get(
                "password",
                ""
            )


            user = authenticate(
                request,
                username=username,
                password=password,
            )


            if user is not None:

                login(
                    request,
                    user
                )

                return redirect(
                    "home"
                )


            messages.error(
                request,
                "Invalid username or password."
            )

            return redirect(
                "login"
            )


    return render(
        request,
        "main/login.html"
    )


# ==========================================================
# HOME
# ==========================================================

def home(request):

    total_papers = (
        SubjectPDF.objects.count()
    )

    total_students = (
        User.objects.count()
    )

    total_departments = (
        SubjectPDF.objects
        .values("department")
        .distinct()
        .count()
    )

    total_semesters = (
        SubjectPDF.objects
        .values("semester")
        .distinct()
        .count()
    )

    return render(
        request,
        "main/home.html",
        {
            "total_papers": total_papers,
            "total_students": total_students,
            "total_departments": total_departments,
            "total_semesters": total_semesters,
        }
    )


# ==========================================================
# SEMESTER
# ==========================================================

@login_required
def semester(request, dept_name):

    if dept_name not in SUBJECTS:

        return redirect(
            "home"
        )

    return render(
        request,
        "main/semester.html",
        {
            "dept_name": dept_name
        }
    )


# ==========================================================
# UPLOAD PDF PAGE
# ==========================================================

@login_required
def upload_pdf(request, dept_name, sem_no):

    # ======================================================
    # SUBJECT LIST
    # ======================================================

    semester_subjects = SUBJECTS.get(
        dept_name,
        {}
    ).get(
        sem_no,
        []
    )

    # ======================================================
    # INVALID DEPARTMENT / SEMESTER
    # ======================================================

    if not semester_subjects:

        messages.error(
            request,
            "Invalid department or semester."
        )

        return redirect("home")

    # ======================================================
    # PDF UPLOAD — STAFF ONLY
    # ======================================================

    if request.method == "POST":

        if not request.user.is_staff:

            raise PermissionDenied

        # --------------------------------------------------
        # GET PDF
        # --------------------------------------------------

        pdf_file = request.FILES.get(
            "pdf_file"
        )

        # --------------------------------------------------
        # VALIDATE PDF
        # --------------------------------------------------

        pdf_error = validate_pdf_file(
            pdf_file
        )

        if pdf_error:

            messages.error(
                request,
                pdf_error
            )

            return redirect(
                "upload_pdf",
                dept_name=dept_name,
                sem_no=sem_no
            )

        # --------------------------------------------------
        # GET SUBJECT
        # --------------------------------------------------

        upload_subject = request.POST.get(
            "upload_subject",
            ""
        ).strip()

        # --------------------------------------------------
        # SUBJECT REQUIRED
        # --------------------------------------------------

        if not upload_subject:

            messages.error(
                request,
                "Please select a subject."
            )

            return redirect(
                "upload_pdf",
                dept_name=dept_name,
                sem_no=sem_no
            )

        # --------------------------------------------------
        # SUBJECT VALIDATION
        # --------------------------------------------------

        if upload_subject not in semester_subjects:

            messages.error(
                request,
                "Invalid subject selected."
            )

            return redirect(
                "upload_pdf",
                dept_name=dept_name,
                sem_no=sem_no
            )

        # --------------------------------------------------
        # SAVE PDF
        # --------------------------------------------------

        SubjectPDF.objects.create(

            department=dept_name,

            semester=sem_no,

            subject=upload_subject,

            pdf_file=pdf_file,

            uploaded_by=request.user,
        )

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        messages.success(
            request,
            "PDF uploaded successfully."
        )

        return redirect(
            "upload_pdf",
            dept_name=dept_name,
            sem_no=sem_no
        )

    # ======================================================
    # SUBJECT FILTER
    # ======================================================

    selected_subject = request.GET.get(
        "subject",
        ""
    ).strip()

    # ======================================================
    # VALIDATE GET SUBJECT
    # ======================================================

    if selected_subject:

        if selected_subject not in semester_subjects:

            messages.error(
                request,
                "Invalid subject selected."
            )

            return redirect(
                "upload_pdf",
                dept_name=dept_name,
                sem_no=sem_no
            )

    # ======================================================
    # PDF LIST
    # ======================================================

    pdfs = SubjectPDF.objects.filter(

        department=dept_name,

        semester=sem_no

    ).order_by(
        "-uploaded_at"
    )

    # ======================================================
    # FILTER
    # ======================================================

    if selected_subject:

        pdfs = pdfs.filter(
            subject=selected_subject
        )

    # ======================================================
    # FILE INFORMATION
    # ======================================================

    for pdf in pdfs:

        # --------------------------------------------------
        # CLEAN FILENAME
        # --------------------------------------------------

        filename = os.path.basename(
            pdf.pdf_file.name
        )

        filename = os.path.splitext(
            filename
        )[0]

        filename = re.sub(
            r'_[A-Za-z0-9]+$',
            '',
            filename
        )

        pdf.filename = filename

        # --------------------------------------------------
        # FILE SIZE
        # --------------------------------------------------

        try:

            size = pdf.pdf_file.size

            if size < 1024:

                pdf.filesize = (
                    f"{size} B"
                )

            elif size < 1024 * 1024:

                pdf.filesize = (
                    f"{size / 1024:.1f} KB"
                )

            else:

                pdf.filesize = (
                    f"{size / (1024 * 1024):.2f} MB"
                )

        except Exception:

            pdf.filesize = "Unknown size"

    # ======================================================
    # RENDER
    # ======================================================

    return render(
        request,
        "main/upload.html",
        {
            "dept_name": dept_name,

            "sem_no": sem_no,

            "subject_name": (
                selected_subject
                or f"Semester {sem_no}"
            ),

            "subjects": semester_subjects,

            "selected_subject": selected_subject,

            "pdfs": pdfs,

            "is_subject_upload": False,
        }
    )


# ==========================================================
# DELETE PDF
# ==========================================================

@staff_member_required
@require_POST
def delete_pdf(request, pdf_id):

    # ======================================================
    # FIND PDF
    # ======================================================

    pdf = get_object_or_404(
        SubjectPDF,
        id=pdf_id
    )

    # ======================================================
    # SAVE PAGE INFORMATION
    # ======================================================

    dept_name = pdf.department

    sem_no = pdf.semester

    subject_name = pdf.subject

    # ======================================================
    # DELETE ACTUAL FILE
    # ======================================================

    if pdf.pdf_file:

        try:

            pdf.pdf_file.delete(
                save=False
            )

        except Exception:

            pass

    # ======================================================
    # DELETE DATABASE RECORD
    # ======================================================

    pdf.delete()

    # ======================================================
    # SUCCESS
    # ======================================================

    messages.success(
        request,
        "PDF deleted successfully."
    )

    # ======================================================
    # RETURN
    # ======================================================

    return redirect(
        "upload_pdf",
        dept_name=dept_name,
        sem_no=sem_no
    )


# ==========================================================
# SUBJECT PAGE
# ==========================================================

@login_required
def subject_page(
    request,
    dept_name
):

    subjects = SUBJECTS.get(
        dept_name
    )

    if subjects is None:

        messages.error(
            request,
            "Invalid department."
        )

        return redirect(
            "home"
        )


    return render(
        request,
        "main/subjects.html",
        {
            "dept_name": dept_name,
            "subjects": subjects,
        }
    )


# ==========================================================
# SUBJECT UPLOAD
# ==========================================================

@login_required
def subject_upload(
    request,
    dept_name,
    sem_no,
    subject_name
):

    # ======================================================
    # SUBJECT LIST
    # ======================================================

    semester_subjects = SUBJECTS.get(
        dept_name,
        {}
    ).get(
        sem_no,
        []
    )

    # ======================================================
    # INVALID DEPARTMENT / SEMESTER
    # ======================================================

    if not semester_subjects:

        messages.error(
            request,
            "Invalid department or semester."
        )

        return redirect("home")

    # ======================================================
    # SELECTED SUBJECT
    # ======================================================

    selected_subject = request.GET.get(
        "subject",
        ""
    ).strip()

    if not selected_subject:

        selected_subject = subject_name

    # ======================================================
    # VALIDATE SUBJECT
    # ======================================================

    if selected_subject not in semester_subjects:

        messages.error(
            request,
            "Invalid subject selected."
        )

        return redirect(
            "subject_upload",
            dept_name=dept_name,
            sem_no=sem_no,
            subject_name=subject_name
        )

    # ======================================================
    # POST — STAFF ONLY
    # ======================================================

    if request.method == "POST":

        if not request.user.is_staff:

            raise PermissionDenied

        # --------------------------------------------------
        # PDF
        # --------------------------------------------------

        pdf_file = request.FILES.get(
            "pdf_file"
        )

        # --------------------------------------------------
        # VALIDATE PDF
        # --------------------------------------------------

        pdf_error = validate_pdf_file(
            pdf_file
        )

        if pdf_error:

            messages.error(
                request,
                pdf_error
            )

            return redirect(
                "subject_upload",
                dept_name=dept_name,
                sem_no=sem_no,
                subject_name=selected_subject
            )

        # --------------------------------------------------
        # UPLOAD SUBJECT
        # --------------------------------------------------

        upload_subject = request.POST.get(
            "upload_subject",
            ""
        ).strip()

        # --------------------------------------------------
        # DEFAULT SUBJECT
        # --------------------------------------------------

        if not upload_subject:

            upload_subject = selected_subject

        # --------------------------------------------------
        # VALIDATE SUBJECT
        # --------------------------------------------------

        if upload_subject not in semester_subjects:

            messages.error(
                request,
                "Invalid subject selected."
            )

            return redirect(
                "subject_upload",
                dept_name=dept_name,
                sem_no=sem_no,
                subject_name=selected_subject
            )

        # --------------------------------------------------
        # SAVE
        # --------------------------------------------------

        SubjectPDF.objects.create(

            department=dept_name,

            semester=sem_no,

            subject=upload_subject,

            pdf_file=pdf_file,

            uploaded_by=request.user,
        )

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        messages.success(
            request,
            "PDF uploaded successfully."
        )

        # --------------------------------------------------
        # RETURN SAME SUBJECT
        # --------------------------------------------------

        return redirect(
            "subject_upload",
            dept_name=dept_name,
            sem_no=sem_no,
            subject_name=upload_subject
        )

    # ======================================================
    # PDF LIST
    # ======================================================

    pdfs = SubjectPDF.objects.filter(

        department=dept_name,

        semester=sem_no,

        subject=selected_subject

    ).order_by(
        "-uploaded_at"
    )

    # ======================================================
    # FILE INFORMATION
    # ======================================================

    for pdf in pdfs:

        # --------------------------------------------------
        # FILENAME
        # --------------------------------------------------

        filename = os.path.basename(
            pdf.pdf_file.name
        )

        filename = os.path.splitext(
            filename
        )[0]

        filename = re.sub(
            r'_[A-Za-z0-9]+$',
            '',
            filename
        )

        pdf.filename = filename

        # --------------------------------------------------
        # FILE SIZE
        # --------------------------------------------------

        try:

            size = pdf.pdf_file.size

            if size < 1024:

                pdf.filesize = (
                    f"{size} B"
                )

            elif size < 1024 * 1024:

                pdf.filesize = (
                    f"{size / 1024:.1f} KB"
                )

            else:

                pdf.filesize = (
                    f"{size / (1024 * 1024):.2f} MB"
                )

        except Exception:

            pdf.filesize = "Unknown size"

    # ======================================================
    # RENDER
    # ======================================================

    return render(
        request,
        "main/upload.html",
        {
            "dept_name": dept_name,

            "sem_no": sem_no,

            "subject_name": selected_subject,

            "subjects": semester_subjects,

            "selected_subject": selected_subject,

            "pdfs": pdfs,

            "is_subject_upload": True,
        }
    )


# ==========================================================
# DELETE SUBJECT PDF
# ==========================================================

@staff_member_required
@require_POST
def delete_subject_pdf(request, pdf_id):

    # ======================================================
    # FIND PDF
    # ======================================================

    pdf = get_object_or_404(
        SubjectPDF,
        id=pdf_id
    )

    # ======================================================
    # SAVE PAGE INFORMATION
    # ======================================================

    dept_name = pdf.department

    sem_no = pdf.semester

    subject_name = pdf.subject

    # ======================================================
    # DELETE ACTUAL FILE
    # ======================================================

    if pdf.pdf_file:

        try:

            pdf.pdf_file.delete(
                save=False
            )

        except Exception:

            pass

    # ======================================================
    # DELETE DATABASE RECORD
    # ======================================================

    pdf.delete()

    # ======================================================
    # SUCCESS
    # ======================================================

    messages.success(
        request,
        "PDF deleted successfully."
    )

    # ======================================================
    # RETURN
    # ======================================================

    return redirect(
        "subject_upload",
        dept_name=dept_name,
        sem_no=sem_no,
        subject_name=subject_name
    )


# ==========================================================
# SEARCH PAGE
# ==========================================================

def search_page(request):

    query = request.GET.get(
        "q",
        ""
    ).strip()

    department = request.GET.get(
        "department",
        ""
    ).strip()


    results = SubjectPDF.objects.none()


    if query:

        filters = (
            Q(subject__icontains=query)
            |
            Q(department__icontains=query)
        )


        if query.isdigit():

            filters |= Q(
                semester=int(query)
            )


        results = SubjectPDF.objects.filter(
            filters
        )


        if department:

            results = results.filter(
                department=department
            )


        results = results.order_by(
            "-uploaded_at"
        )


    return render(
        request,
        "main/search.html",
        {
            "query": query,
            "department": department,
            "results": results,
        }
    )


# ==========================================================
# SEARCH API
# ==========================================================

def search_api(request):

    query = request.GET.get(
        "q",
        ""
    ).strip()

    department = request.GET.get(
        "department",
        ""
    ).strip()


    # Empty query → no results
    if not query:

        return JsonResponse(
            [],
            safe=False
        )


    filters = Q(
        subject__icontains=query
    )


    if query.isdigit():

        filters |= Q(
            semester=int(query)
        )


    results = SubjectPDF.objects.filter(
        filters
    )


    if department:

        results = results.filter(
            department=department
        )


    results = results.order_by(
        "-uploaded_at"
    )[:8]


    data = []


    for pdf in results:

        data.append(
            {
                "id": pdf.id,
                "slug": pdf.slug,
                "subject": pdf.subject,
                "department": pdf.department,
                "semester": pdf.semester,
            }
        )


    return JsonResponse(
        data,
        safe=False
    )


# ==========================================================
# PAPER DETAIL
# ==========================================================

def paper_detail(request, slug):

    pdf = get_object_or_404(
        SubjectPDF,
        slug=slug
    )

    is_favorite = False

    if request.user.is_authenticated:

        is_favorite = Favorite.objects.filter(
            user=request.user,
            paper=pdf
        ).exists()

    return render(
        request,
        "main/paper_detail.html",
        {
            "pdf": pdf,
            "is_favorite": is_favorite,
        }
    )


# ==========================================================
# FAVORITES
# ==========================================================

@login_required
def favorites(request):

    favorite_list = (
        Favorite.objects
        .filter(user=request.user)
        .select_related("paper")
        .order_by("-created_at")
    )


    return render(
        request,
        "main/favorites.html",
        {
            "favorites": favorite_list,
        }
    )


@login_required
@require_POST
def add_favorite(
    request,
    paper_id
):

    paper = get_object_or_404(
        SubjectPDF,
        id=paper_id
    )


    Favorite.objects.get_or_create(
        user=request.user,
        paper=paper
    )


    return redirect(
        "favorites"
    )


@login_required
@require_POST
def remove_favorite(
    request,
    paper_id
):

    paper = get_object_or_404(
        SubjectPDF,
        id=paper_id
    )


    Favorite.objects.filter(
        user=request.user,
        paper=paper
    ).delete()


    return redirect(
        "favorites"
    )


# ==========================================================
# PROFILE
# ==========================================================

@login_required
def profile(request):

    favorite_count = (
        Favorite.objects.filter(
            user=request.user
        ).count()
    )


    return render(
        request,
        "main/profile.html",
        {
            "favorite_count": favorite_count,
        }
    )


# ==========================================================
# PASSWORD CHANGE
# ==========================================================

class CustomPasswordChangeView(
    PasswordChangeView
):

    template_name = (
        "main/change_password.html"
    )

    success_url = reverse_lazy(
        "profile"
    )


# ==========================================================
# CONTACT
# ==========================================================

def contact(request):

    return render(
        request,
        "main/contact.html"
    )


# ==========================================================
# 404
# ==========================================================

def error_404(
    request,
    exception
):

    return render(
        request,
        "main/404.html",
        status=404
    )


# ==========================================================
# LOGOUT
# ==========================================================

@login_required
def logout_user(request):

    logout(request)

    return redirect(
        "login"
    )


# ==========================================================
# EDIT PROFILE
# ==========================================================

@login_required
def edit_profile(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()


        if not username:

            messages.error(
                request,
                "Username is required."
            )

            return render(
                request,
                "main/edit_profile.html",
                {
                    "username": username,
                    "email": email,
                }
            )


        # ==================================================
        # USERNAME CHECK
        # ==================================================

        if User.objects.exclude(
            id=request.user.id
        ).filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return render(
                request,
                "main/edit_profile.html",
                {
                    "username": username,
                    "email": email,
                }
            )


        # ==================================================
        # EMAIL CHECK
        # ==================================================

        if email and User.objects.exclude(
            id=request.user.id
        ).filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return render(
                request,
                "main/edit_profile.html",
                {
                    "username": username,
                    "email": email,
                }
            )


        user = request.user

        user.username = username
        user.email = email

        user.save(
            update_fields=[
                "username",
                "email",
            ]
        )


        messages.success(
            request,
            "Profile updated successfully."
        )


        return redirect(
            "profile"
        )


    return render(
        request,
        "main/edit_profile.html",
        {
            "username": request.user.username,
            "email": request.user.email,
        }
    )


# ==========================================================
# DELETE ACCOUNT
# ==========================================================

@login_required
@require_POST
def delete_account(
    request
):

    password = request.POST.get(
        "password",
        ""
    )


    user = authenticate(
        request,
        username=request.user.username,
        password=password,
    )


    if user is None:

        messages.error(
            request,
            "Incorrect password."
        )

        return render(
            request,
            "main/delete_account.html"
        )


    current_user = request.user

    logout(request)

    current_user.delete()


    messages.success(
        request,
        "Your account has been deleted successfully."
    )


    return redirect(
        "login"
    )


# ==========================================================
# ROBOTS.TXT
# ==========================================================

def robots_txt(request):

    return HttpResponse(
        "User-agent: *\n"
        "Allow: /\n\n"
        "Sitemap: "
        "https://cts-question-paper.onrender.com/"
        "sitemap.xml",
        content_type="text/plain",
    )


# ==========================================================
# DOWNLOAD PDF
# ==========================================================

def download_pdf(request, slug):

    paper = get_object_or_404(
        SubjectPDF,
        slug=slug
    )

    # ======================================================
    # CHECK FILE
    # ======================================================

    if not paper.pdf_file:

        messages.error(
            request,
            "PDF file is not available."
        )

        return redirect(
            "paper_detail",
            slug=paper.slug
        )

    # ======================================================
    # INCREMENT DOWNLOAD COUNT
    # ======================================================

    SubjectPDF.objects.filter(
        pk=paper.pk
    ).update(
        download_count=F(
            "download_count"
        ) + 1
    )

    # ======================================================
    # OPEN FILE
    # ======================================================

    try:

        file_handle = paper.pdf_file.open(
            "rb"
        )

    except Exception:

        messages.error(
            request,
            "Unable to open PDF file."
        )

        return redirect(
            "paper_detail",
            slug=paper.slug
        )

    # ======================================================
    # DOWNLOAD
    # ======================================================

    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=os.path.basename(
            paper.pdf_file.name
        ),
    )