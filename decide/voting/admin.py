from django.contrib import admin
from django.utils import timezone

from .models import QuestionOption
from .models import QuestionOptionRanked
from .models import Question
from .models import Voting
from .models import QuestionOptionYesNo

from .filters import StartedFilter


def start(modeladmin, request, queryset):
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        v.end_date = timezone.now()
        v.save()


def tally(ModelAdmin, request, queryset):
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get('auth-token', '')
        v.tally_votes(token)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('desc', 'type')

class QuestionOptionRankedAdmin(admin.ModelAdmin):
    list_display = ('question', 'number', 'option')

class QuestionOptionYesNoAdmin(admin.ModelAdmin):
    list_display = ('question', 'number', 'option')


class VotingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'future_stop')
    readonly_fields = ('start_date', 'end_date', 'pub_key',
                       'tally', 'postproc')
    date_hierarchy = 'start_date'
    list_filter = (StartedFilter,)
    search_fields = ('name', )

    actions = [ start, stop, tally ]



admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionOption)
admin.site.register(QuestionOptionRanked, QuestionOptionRankedAdmin)
admin.site.register(QuestionOptionYesNo, QuestionOptionYesNoAdmin)

