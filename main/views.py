from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import PDFUpload, SubjectPDF
import os
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Favorite
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import SubjectPDF, Favorite
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse

@staff_member_required
def admin_dashboard(request):
    return render(request, "main/admin_dashboard.html")


def login_page(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "register":
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password")

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect("/?login=true")

            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            messages.success(request, "Registration successful. Please login.")
            return redirect("/?login=true")

        elif form_type == "login":
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password")

            print("Username:", repr(username))
            print("Password:", repr(password))

            user = authenticate(
                request,
                username=username,
                password=password
            )

            print("Authenticated User:", user)

            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password")
                return redirect("login")

    return render(request, "main/login.html")


def home(request):
    return render(request, "main/home.html")


def semester(request, dept_name):
    return render(request, "main/semester.html", {
        "dept_name": dept_name
    })

def upload_pdf(request, sem_no):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf_file")

        if pdf_file:
            PDFUpload.objects.create(
                semester=sem_no,
                pdf_file=pdf_file
            )

        return redirect("upload_pdf", sem_no=sem_no)

    pdfs = PDFUpload.objects.filter(semester=sem_no)

    return render(request, "main/upload.html", {
        "sem_no": sem_no,
        "pdfs": pdfs
    })


def delete_pdf(request, pdf_id):
    pdf = PDFUpload.objects.get(id=pdf_id)
    sem_no = pdf.semester

    if pdf.pdf_file:
        pdf.pdf_file.delete(save=False)

    pdf.delete()
    return redirect("upload_pdf", sem_no=sem_no)


SUBJECTS = {
    "cst": {
        1: ["Applied Chemistry", "Applied Physics I", "Communication Skills in English", "Mathematics I"],
        2: ["Introduction to IT Systems", "Applied Physics II", "Fundamentals of Electrical & Electronics", "Engineering Mechanics", "Mathematics II"],
        3: ["Algorithms", "Computer System Organization", "Computer Programming in C", "Scripting Languages Python", "Data Structures"],
        4: ["Operating Systems", "Introduction to DBMS", "Software Engineering", "Computer Networks", "Object Oriented Programming using Java"],
        5: ["Advanced Computer Network", "Computer Graphics", "Fundamentals of AI", "Microprocessor & Microcontroller", "Digital Image Processing", "Theory of Automata", "Mobile Computing", "Internet of Things"],
        6: ["Cloud Computing", "Data Science Data Warehousing & Data Mining", "Web Designing", "Entrepreneurship & Start-ups", "Machine Learning"],
    },
    "civil": {
        1: ["Applied Chemistry", "Applied Physics I", "Communication Skills in English", "Mathematics I"],
        2: ["Introduction to IT Systems", "Applied Physics II", "Fundamentals of Electrical & Electronics", "Engineering Mechanics", "Mathematics II"],
        3: ["Engineering Survey", "Building Materials", "Civil Engineering Drawing", "Strength of Materials", "Construction Technology"],
        4: ["Structural Mechanics", "Concrete Technology", "Transportation Engineering", "Geotechnical Engineering", "Environmental Engineering"],
        5: ["Design of Concrete Structures", "Estimating & Costing", "Irrigation Engineering", "Advanced Surveying", "Construction Management", "Railway Bridge & Tunnel Engineering"],
        6: ["Design of Steel Structures", "Quantity Surveying & Valuation", "Public Health Engineering", "Disaster Management", "Entrepreneurship & Start-ups"],
    },
    "electrical": {
        1: ["Applied Chemistry", "Applied Physics I", "Communication Skills in English", "Mathematics I"],
        2: ["Introduction to IT Systems", "Applied Physics II", "Fundamentals of Electrical & Electronics", "Engineering Mechanics", "Mathematics II"],
        3: ["Electrical Circuit Theory", "Electrical Machines I", "Basic Electronics", "Programming Concepts Using C", "Electrical Measuring Instruments", "Elements of Mechanical Engineering"],
        4: ["Electrical Machines II", "Electrical Measurement & Control", "Transmission & Distribution of Electric Power", "Applied & Digital Electronics", "Power Plant Engineering"],
        5: ["Industrial Electronics", "Switchgear & Protection", "Microprocessor & Microcontroller", "Utilization of Electrical Energy", "Electrical Design & Estimation", "Renewable Energy Sources"],
        6: ["Industrial Management", "Instrumentation & Control", "Electrical Maintenance & Safety", "Energy Conservation & Audit", "Entrepreneurship & Start-ups"],
    },
    "mechanical": {
        1: ["Applied Chemistry", "Applied Physics I", "Communication Skills in English", "Mathematics I"],
        2: ["Introduction to IT Systems", "Applied Physics II", "Fundamentals of Electrical & Electronics", "Engineering Mechanics", "Mathematics II"],
        3: ["Engineering Materials", "Manufacturing Processes", "Strength of Materials", "Engineering Thermodynamics", "Engineering Drawing & Machine Drawing"],
        4: ["Theory of Machines", "Fluid Mechanics & Hydraulics", "Manufacturing Technology", "Metrology & Measurement", "Workshop Technology"],
        5: ["Machine Design", "Thermal Engineering", "Production Engineering", "Industrial Engineering & Management", "CAD CAM", "Automobile Engineering"],
        6: ["Refrigeration & Air Conditioning", "Mechatronics", "Power Plant Engineering", "Maintenance Engineering", "Engineering Economics & Project Management"],
    },
}


def subject_page(request, dept_name):
    subjects = SUBJECTS.get(dept_name)

    return render(request, "main/subjects.html", {
        "dept_name": dept_name,
        "subjects": subjects
    })


def subject_upload(request, dept_name, sem_no, subject_name):
    if request.method == "POST" and request.FILES.get("pdf_file"):
        SubjectPDF.objects.create(
            department=dept_name,
            semester=sem_no,
            subject=subject_name,
            pdf_file=request.FILES["pdf_file"],
            uploaded_by=request.user,
        )

        return redirect(
            "subject_upload",
            dept_name=dept_name,
            sem_no=sem_no,
            subject_name=subject_name
        )

    pdfs = SubjectPDF.objects.filter(
        department=dept_name,
        semester=sem_no,
        subject=subject_name
    ).order_by("-uploaded_at")

    return render(request, "main/upload.html", {
        "dept_name": dept_name,
        "sem_no": sem_no,
        "subject_name": subject_name,
        "pdfs": pdfs,
        "is_subject_upload": True,
    })


def delete_subject_pdf(request, pdf_id):
    pdf = SubjectPDF.objects.get(id=pdf_id)
    dept_name = pdf.department
    sem_no = pdf.semester
    subject_name = pdf.subject

    if pdf.pdf_file:
        pdf.pdf_file.delete(save=False)

    pdf.delete()

    return redirect(
        "subject_upload",
        dept_name=dept_name,
        sem_no=sem_no,
        subject_name=subject_name
    )
def search_page(request):

    query = request.GET.get("q", "").strip()
    department = request.GET.get("department", "").strip()

    results = SubjectPDF.objects.none()

    if query:

        results = SubjectPDF.objects.filter(

           Q(subject__icontains=query) |
           Q(department__icontains=query) |
           Q(semester__icontains=query)

        )

        if department:

            results = results.filter(department=department)

        results = results.order_by("-uploaded_at")

    return render(request, "main/search.html", {

        "query": query,
        "department": department,
        "results": results,

    })
def search_api(request):

    query = request.GET.get("q", "").strip()
    department = request.GET.get("department", "").strip()

    results = SubjectPDF.objects.filter(
        subject__icontains=query
    )

    if department:
        results = results.filter(department=department)

    results = results[:8]

    data = []

    for pdf in results:
        data.append({
            "id": pdf.id,
            "subject": pdf.subject,
            "department": pdf.department,
            "semester": pdf.semester,
        })

    return JsonResponse(data, safe=False)

def paper_detail(request, pdf_id):
    pdf = get_object_or_404(SubjectPDF, id=pdf_id)

    is_favorite = False

    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user,
            paper=pdf
        ).exists()

    return render(request, "main/paper_detail.html", {
        "pdf": pdf,
        "is_favorite": is_favorite,
    })

@login_required
def favorites(request):
    favorites = Favorite.objects.filter(user=request.user)

    return render(request, "main/favorites.html", {
        "favorites": favorites,
    })


@login_required
def add_favorite(request, paper_id):
    paper = get_object_or_404(SubjectPDF, id=paper_id)

    Favorite.objects.get_or_create(
        user=request.user,
        paper=paper
    )

    return redirect("favorites")


@login_required
def remove_favorite(request, paper_id):
    paper = get_object_or_404(SubjectPDF, id=paper_id)

    Favorite.objects.filter(
        user=request.user,
        paper=paper
    ).delete()

    return redirect("favorites")


@login_required
def profile(request):
    favorite_count = Favorite.objects.filter(user=request.user).count()

    return render(request, "main/profile.html", {
        "favorite_count": favorite_count,
    })


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "main/change_password.html"
    success_url = reverse_lazy("profile")

def contact(request):
    return render(request, "main/contact.html")

def error_404(request, exception):
    return render(request, "main/404.html", status=404)

def logout_user(request):
    logout(request)
    return redirect("login")

@login_required
def edit_profile(request):

    if request.method == "POST":

        # .strip() যোগ করো
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()

        # Debug (Terminal-এ দেখাবে)
        print("Logged in user:", request.user.username)
        print("Entered username:", username)

        # Username already exists?
        if User.objects.exclude(id=request.user.id).filter(username=username).exists():
           messages.error(request, "Username already exists.")

           return render(request, "main/edit_profile.html", {
              "username": username,
              "email": email,
    })
        

        # Email already exists?
        if User.objects.exclude(id=request.user.id).filter(email=email).exists():

           messages.error(request, "Email already exists.")

           return render(request, "main/edit_profile.html", {
              "username": username,
              "email": email,
    })
        
        user = request.user
        user.username = username
        user.email = email
        user.save()

        messages.success(request, "Profile updated successfully.")

        return redirect("profile")

    return render(request, "main/edit_profile.html", {
    "username": request.user.username,
    "email": request.user.email,
})

@login_required
def delete_account(request):

    if request.method == "POST":

        password = request.POST.get("password")

        user = authenticate(
            username=request.user.username,
            password=password,
        )

        if user is not None:

            user = request.user

            logout(request)

            user.delete()

            messages.success(
            request,
            "Your account has been deleted successfully.",
            )

            return redirect("login")

        else:

            messages.error(
                request,
                "Incorrect password.",
            )

    return render(
        request,
        "main/delete_account.html",
    )

from django.http import HttpResponse

def robots_txt(request):
    return HttpResponse(
        "User-agent: *\n"
        "Allow: /\n\n"
        "Sitemap: https://cts-question-paper.onrender.com/sitemap.xml",
        content_type="text/plain",
    )

def download_pdf(request, slug):
    paper = get_object_or_404(SubjectPDF, slug=slug)

    paper.download_count += 1
    paper.save(update_fields=["download_count"])

    return FileResponse(
        paper.pdf_file.open("rb"),
        as_attachment=True,
        filename=paper.pdf_file.name.split("/")[-1],
    )