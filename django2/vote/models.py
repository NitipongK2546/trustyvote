from django.db import models
from users.models import Member

class Voter(models.Model):
    # Has to be unique and created randomly
    voter_code = models.CharField(max_length=64)
    # hasVoted = models.BooleanField(default=False)
    # One code, One Poll
    # allowed_poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

class Poll(models.Model):
    poll_code = models.CharField(max_length=32, null=True, blank=True)
    question = models.CharField(max_length=255)

    poll_secret = models.CharField(max_length=16)

    public_key = models.TextField()
    private_key = models.BinaryField()

    voter_list = models.ManyToManyField(Voter, related_name='allowed_poll')

    creator = models.ForeignKey(Member, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.question

# 1 Page accessed through hyperlink or code using website.com/vote
# 1 textbox asking for voter_code
#
# user = Voter.objects.get(voter_code=voter_code)
# IF USER OVJECT EXIST allowed poll -> poll code -> send to directory of code
# maybe there's a loophole, but it will work.
#
# IF THE CODE FAILS, YOU WON'T GET OBJECT, SO NEED TO TAKE CARE OF THAT TOO.
# filter(voter_code=voter_code).first() should work?
#
# Alternative, each poll has key. 
# If you enter real userID and has the page convert to key, 
# then you can vote.
#

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name='choices', on_delete=models.CASCADE)
    # choice_text = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=64)
    
    def __str__(self):
        return self.choice_text
    
class VoteCard(models.Model):
    data = models.JSONField()
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)