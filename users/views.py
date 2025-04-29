from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm
from .models import Member
from vote.models import Candidate, Voter, Choice
from vote.models import Poll, Candidate

from django.contrib.auth.decorators import login_required
from utils.code_gen import generate_poll_code, create_seeded_hash
from utils.rsa import generate_rsa_keys

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

@login_required(login_url='/login')
def create_poll(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        choices = request.POST.getlist('choices[]')
        voter_ids_raw = request.POST.get('voter_ids')

        kpriv, kpub = generate_rsa_keys()

        print(kpub)
        print(kpub.decode('utf-8'))

        if question and choices:
            poll = Poll.objects.create(question=question, 
                                       creator=Member.objects.get(member_user=request.user),
                                        poll_code=generate_poll_code(),
                                        poll_secret=generate_poll_code(),
                                        public_key=kpub.decode('utf-8'),
                                        private_key=kpriv,
                                       )
            for choice_text in choices:
                if choice_text.strip():
                    Choice.objects.create(poll=poll, choice_text=choice_text.strip())
                    Candidate.objects.create(name=choice_text.strip(), poll=poll)

            if voter_ids_raw:
                try:
                    voter_id_list = [int(v.strip()) for v in voter_ids_raw.split(',') if v.strip()]
                    print(voter_id_list)
                    voter_hmac_list = [create_seeded_hash(str(v_id), poll.poll_secret) for v_id in voter_id_list]
                    print(voter_hmac_list)

                    voters = []
                    for voter_id in voter_hmac_list:
                        voter = Voter.objects.create(voter_code=voter_id) 
                        voters.append(voter)

                    print(voters)

                    poll.voter_list.set(voters)
                except ValueError:
                    poll.delete()  
                    return render(request, 'users/create_poll.html', {
                        
                    })
            else:
                # No voter IDs given -> allow all voters
                all_voters = Voter.objects.all()
                poll.voter_list.set(all_voters)

            return redirect(reverse('vote:success', kwargs={'poll_code': poll.poll_code}))  # Just redirect or show success message

    return render(request, 'users/create_poll.html', {

    })

@login_required(login_url='/login')
def poll_success(request, poll_code):

    poll = Poll.objects.get(poll_code=poll_code)

    return render(request, 'users/success.html', {
        'poll': poll
    })