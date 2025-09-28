import random
import openai
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import OTP,StudyDay,StudyPlan

# ---------------------- Signup ----------------------
def signup_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "study_plans/signup.html", {"error": "Passwords do not match"})

        if User.objects.filter(email=email).exists():
            return render(request, "study_plans/signup.html", {"error": "Email already registered"})

        username = email.split("@")[0:5]
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_active=False  # inactive until OTP verified
        )

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, code=otp_code)

        # Send OTP
        send_mail(
            "Study Tracks Verification Code",
            f"Your verification code is: {otp_code}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )

        return redirect("verify_otp", user_id=user.id)

    return render(request, "study_plans/signup.html")


# ---------------------- Verify ----------------------
def verify_otp_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        code = request.POST.get("verification_code")
        otp = get_object_or_404(OTP, user=user)

        if otp.code == code:
            user.is_active = True
            user.save()
            login(request, user)
            return redirect("login")
        else:
            return render(request, "study_plans/verify_otp.html", {"error": "Invalid verification code"})

    return render(request, "study_plans/verify_otp.html")


# ---------------------- Login ----------------------
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            return render(request, "study_plans/login.html", {"error": "Both fields are required"})

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "study_plans/login.html", {"error": "No account found with this email"})

        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "study_plans/login.html", {"error": "Invalid password"})

    return render(request, "study_plans/login.html")

# ---------------------- Logout ----------------------
def logout_view(request):
    logout(request)
    return redirect("login")




# study_plans/views.py
import openai
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import StudyPlan, StudyDay


@login_required(login_url='login')
def dashboard_view(request):
    plans = StudyPlan.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'study_plans/dashboard.html', {'plans': plans})

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import StudyPlan, StudyDay
import openai
@login_required
def create_plan_view(request):
    if request.method == "POST":
        class_name = request.POST.get("class_name", "").strip()
        subject = request.POST.get("subject", "").strip()
        total_days = request.POST.get("duration", "").strip()

        # Validate total_days
        try:
            total_days = int(total_days)
        except ValueError:
            total_days = 0

        if not class_name or not subject or total_days <= 0:
            error = "⚠️ Please select class, subject, and enter a valid duration."
            return render(
                request,
                "study_plans/create_plan.html",
                {
                    "error": error,
                    "class_choices": StudyPlan.CLASS_CHOICES,
                    "subject_choices": StudyPlan.SUBJECT_CHOICES,
                },
            )

        # Create StudyPlan entry first
        plan = StudyPlan.objects.create(
            user=request.user,
            class_name=class_name,
            subject=subject,
            total_days=total_days,
        )

        # Prepare topics list
        topics = []

        # AI Prompt
        prompt = f"""
        Act as a study planner.CBSE NCERT OFFICIALS 
        Create a {total_days}-day day-wise study plan for Class {class_name} - {subject}.
        as per the latest syllabus of cbse ncert .. no extra ch also no ch should missed
        Rules:
        
    - Cover ALL NCERT chapters sequentially with 100 percent  accuracy of year 2025  .
        - Use exactly {total_days} days and cover entire syllabus within it.
        - Split big chapters, merge small ones.
        - Add revision/practice days naturally.
        - Output strictly in this format: and no into and ontro 

        Day 1: Chapter No & Name - [Subtopic if needed]
        Day 2: Chapter No & Name - [Subtopic if needed]
        ...
        Day {total_days}: Chapter/Revision
        """

        try:
            # OpenRouter / DeepSeek configuration
            openai.api_key = getattr(settings, "API_KEY", None)
            openai.api_base = "https://openrouter.ai/api/v1"

            response = openai.ChatCompletion.create(
                model="deepseek/deepseek-chat-v3.1:free",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=1800,
            )

            ai_text = response.choices[0].message.content
            print("\n📘 Generated Study Plan:\n", ai_text)

            # Parse AI output
            for line in ai_text.split("\n"):
                if line.strip().lower().startswith("day"):
                    topics.append(line.strip())

        except Exception as e:
            print("⚠️ AI Error:", e)

        # Ensure exactly total_days entries
        if len(topics) < total_days:
            for i in range(len(topics), total_days):
                topics.append(f"Day {i+1}: Topic TBD")
        elif len(topics) > total_days:
            topics = topics[:total_days]

        # Save StudyDay entries
        for i, topic in enumerate(topics):
            StudyDay.objects.create(
                plan=plan,
                day_number=i + 1,
                topic=topic,
            )

        return redirect("view_plan", plan_id=plan.id)

    # GET request → show form
    return render(
        request,
        "study_plans/create_plan.html",
        {
            "class_choices": StudyPlan.CLASS_CHOICES,
            "subject_choices": StudyPlan.SUBJECT_CHOICES,
        },
    )

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import StudyPlan, StudyDay

@login_required
def view_plan_view(request, plan_id):
    # Get the plan for the logged-in user
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    days = plan.days.all()  # Fetch all StudyDay objects for this plan

    if request.method == "POST":
        # Get list of completed day IDs from form
        completed_days = request.POST.getlist("completed")
        
        # Update each day's completion status
        for day in days:
            day.is_completed = str(day.id) in completed_days
            day.save()

        return redirect('view_plan', plan_id=plan.id)  # Refresh page after update

    # Render the plan with days
    return render(request, 'study_plans/view_plan.html', {
        'plan': plan,
        'days': days
    })

@login_required(login_url='login')
def about_view(request):
    return render(request, "study_plans/about.html")

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render

@login_required(login_url='login')
def contact_view(request):
    success = False
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Send email (optional)
        send_mail(
            subject=f"Contact Form Submission from {name}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],  # set in settings.py
            fail_silently=False,
        )
        success = True

    return render(request, "study_plans/contact.html", {"success": success})


from django.shortcuts import render, get_object_or_404, redirect
from .models import StudyPlan, StudyDay

# Delete StudyPlan
def delete_plan(request, pk):
    if request.method == "POST":
        plan = get_object_or_404(StudyPlan, pk=pk, user=request.user)
        plan.delete()
    return redirect('dashboard')
    
