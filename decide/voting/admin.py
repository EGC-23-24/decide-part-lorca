from django.contrib import admin
from django.utils import timezone

from .models import QuestionOption
from .models import QuestionOptionRanked
from .models import Question
from .models import Voting
from .models import QuestionOptionYesNo

from .filters import StartedFilter


def start(modeladmin, request, queryset):
    """
    Admin action to start the voting process for selected items.

    This action sets the start date of each selected voting to the current time.

    :param modeladmin: The current ModelAdmin instance.
    :type modeladmin: ModelAdmin
    :param request: The HTTP request triggering this action.
    :type request: HttpRequest
    :param queryset: The queryset of selected items.
    :type queryset: QuerySet
    """
    
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()


def stop(ModelAdmin, request, queryset):
    """
    Admin action to stop the voting process for selected items.

    This action sets the end date of each selected voting to the current time.

    :param ModelAdmin: The current ModelAdmin instance.
    :type ModelAdmin: ModelAdmin
    :param request: The HTTP request triggering this action.
    :type request: HttpRequest
    :param queryset: The queryset of selected items.
    :type queryset: QuerySet
    """
    
    for v in queryset.all():
        v.end_date = timezone.now()
        v.save()


def tally(ModelAdmin, request, queryset):
    """
    Admin action to tally votes for selected items.

    This action triggers vote tallying for each selected voting that has ended.

    :param ModelAdmin: The current ModelAdmin instance.
    :type ModelAdmin: ModelAdmin
    :param request: The HTTP request triggering this action.
    :type request: HttpRequest
    :param queryset: The queryset of selected items.
    :type queryset: QuerySet
    """
    
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get('auth-token', '')
        v.tally_votes(token)

class QuestionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Question objects.

    Attributes:
        list_display: Fields to be displayed in the list view.
    """
    
    list_display = ('desc', 'type')

class QuestionOptionRankedAdmin(admin.ModelAdmin):
    """
    Admin interface for managing ranked QuestionOption objects.

    Attributes:
        list_display: Fields to be displayed in the list view.
    """
    
    list_display = ('question', 'number', 'option')

class QuestionOptionYesNoAdmin(admin.ModelAdmin):
    """
    Admin interface for managing yes/no QuestionOption objects.

    Attributes:
        list_display: Fields to be displayed in the list view.
    """
    
    list_display = ('question', 'number', 'option')


class VotingAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Voting objects.

    Attributes:
        list_display: Fields to be displayed in the list view.
        readonly_fields: Fields that are read-only in the admin interface.
        date_hierarchy: Field used to organize the date hierarchy.
        list_filter: Filters to apply in the list view.
        search_fields: Fields to search in the list view.
        actions: Custom actions available for this model.
    """
    
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

