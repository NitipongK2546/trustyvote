from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Poll, Voter, Choice, Candidate
from users.models import Member

from .code_gen import generate_poll_code, create_seeded_hash

from examples.send import send_vote

from django.core.serializers import serialize
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives.asymmetric import rsa
from examples.rsa import generate_rsa_keys
from cryptography.hazmat.backends import default_backend

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
                    return render(request, 'vote/create_poll.html', {
                        
                    })
            else:
                # No voter IDs given -> allow all voters
                all_voters = Voter.objects.all()
                poll.voter_list.set(all_voters)

            return redirect(reverse('vote:success', kwargs={'poll_code': poll.poll_code}))  # Just redirect or show success message

    return render(request, 'vote/create_poll.html', {

    })

def poll_success(request, poll_code):

    poll = Poll.objects.get(poll_code=poll_code)

    return render(request, 'vote/success.html', {
        'poll': poll
    })

def poll(request, poll_code):
    if not request.session.get('has_access'):
        return redirect("vote:vote_authen", poll_code)
    if not request.COOKIES.get('voter_id'):
        return redirect("vote:vote_authen", poll_code)
    poll = Poll.objects.get(poll_code=poll_code)
    if request.method == 'POST':

        voter_id = request.COOKIES.get('voter_id')
        
        voter = poll.voter_list.filter(voter_code=voter_id).first()

        if(voter != None):
            # server_public_key = poll.public_key.encode('utf-8')

            print(type(poll.public_key))
            print(poll.public_key)

            pem_data = f"""
            {poll.public_key}
            """

            # Load the public key
            server_public_key = serialization.load_pem_public_key(
                pem_data.encode('utf-8'),
                backend=default_backend()
            )

            print(server_public_key)

            server_public_key = server_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            print(server_public_key)

            # print(public_key)

            selected_choice = poll.choices.get(id=request.POST['choice'])

            candidate = Candidate.objects.get(name=selected_choice, poll=poll)

            candidate_data = serialize('json', [candidate])

            vote_data = {
                "choice": candidate_data  
            }
            #
            # time to create packet and send it.
            # use send_vote(vote_data, voter_id, server_public_key)
            # 
            # vote_data : vote turned into a dict/json
            # voter_id: the randomly generated one, use real id hash with poll_secret
            # server_public_key : hidden input field should be fine? We can't prevent it from being changed.
            #
            send_vote(vote_data, voter_id, server_public_key)

            print("finished")

            poll.voter_list.remove(voter)

            return redirect('vote:results', poll_code=poll_code)
        else:
            return redirect('users:main_page')
    
    print(poll.public_key)
    return render(request, 'vote/poll.html', {
        'poll': poll
    })

def poll_authen(request, poll_code):
    if request.method == 'POST':
        received_code = request.POST["code"]

        current_poll = Poll.objects.get(poll_code=poll_code)

        hashed_code = create_seeded_hash(received_code, current_poll.poll_secret)

        voter = current_poll.voter_list.filter(voter_code=hashed_code).first()

        print(voter)

        if(voter != None):
            print(voter.voter_code)
            request.session['has_access'] = True
            response = redirect("vote:vote_pass", poll_code)
            response.set_cookie('voter_id', hashed_code)
            return response
        
    return render(request, 'vote/poll_authen.html', {
        
    })

def results(request, poll_code):
    response = render(request, 'vote/results.html', {})
    response.delete_cookie('voter_id')
    response.delete_cookie('sessionid')
    if 'has_access' in request.session:
        del request.session['has_access']
    return response


# # 
# # Vote here
# # You should see each choices available from making a poll
# # Then you encrypt the answer voter choose
# # Whether how you can encrypt a model is a mystery.
# # 
# def poll(request, poll_code):
#     poll = Poll.objects.get(poll_code=poll_code)
#     if request.method == 'POST':
#         selected_choice = poll.choices.get(id=request.POST['choice'])
#         selected_choice.polls += 1
#         selected_choice.save()
#         return redirect('vote:results', poll_id=poll.id)

#     return render(request, 'vote/poll.html', {
#         'poll': poll
#     })