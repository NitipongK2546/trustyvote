from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Poll, Candidate

from utils.code_gen import generate_poll_code, create_seeded_hash

from utils.send import send_vote

from django.core.serializers import serialize
from cryptography.hazmat.primitives import serialization

from utils.rsa import generate_rsa_keys
from cryptography.hazmat.backends import default_backend

from django.contrib.auth.decorators import login_required

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
            send_vote(vote_data, voter_id, server_public_key, poll_code)

            print("finished")

            poll.voter_list.remove(voter)

            return redirect('vote:results', poll_code=poll_code)
        else:
            return redirect('/')
    
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