from django.contrib import admin
from .models import Member

from vote.models import VoteCard

# Register your models here.

class MemberAdmin(admin.ModelAdmin):
    list_display = ("id", "member_fname", "member_lname")

class CardAdmin(admin.ModelAdmin):
    list_display = ("id", "data", "poll")

admin.site.register(Member, MemberAdmin)
admin.site.register(VoteCard, CardAdmin)

