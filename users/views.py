from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm
from .models import Member
from vote.models import Poll, Candidate

from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    if request.method == "POST":
        poll_code = request.POST["poll_code"]

        poll = Poll.objects.filter(poll_code=poll_code).first()

        if poll is not None:
            return redirect("vote:vote_pass", poll_code)
        
    return render(request, "users/index.html")

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("users:login")
    
    current_member = Member.objects.get(member_user=request.user)

    all_polls = Poll.objects.filter(creator=current_member)

    return render(request, "users/dashboard.html", {
        "member": current_member,
        "polls": all_polls,
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, "users/login.html", {
                "Message" : "Wrong Username or Password."
            })
        else:
            login(request, user)
            return redirect("users:dashboard")
        
    return render(request, "users/login.html")

def logout_view(request):
    logout(request)
    return redirect("users:main_page")

def register_view(request):

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            user.save()

            return redirect("users:login")
        else:
            print("THIS IS WRONG")
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {
        "form": form,
        "Message" : "Register your account to gain access.",
    })

@login_required(login_url='/login')
def profile_view(request):
    current_member = Member.objects.get(member_user=request.user)
    return render(request, "users/profile.html", {
        "member": current_member
    })

def poll_score(request, poll_code):

    poll = Poll.objects.get(poll_code=poll_code)

    all_candidates = Candidate.objects.filter(poll=poll)

    return render(request, "users/results.html", {
        "candidates": all_candidates,
    })