from django.contrib import admin
from .models import Poll, Candidate, Voter, Choice

# Register your models here.

class PollAdmin(admin.ModelAdmin):
    list_display = ("id", "poll_code", "question", "poll_secret")

class VoterAdmin(admin.ModelAdmin):
    list_display = ("id", "voter_code")

admin.site.register(Poll, PollAdmin)
admin.site.register(Voter, VoterAdmin)