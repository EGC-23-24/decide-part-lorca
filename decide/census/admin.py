from django.contrib import admin

from .models import Census


class CensusAdmin(admin.ModelAdmin):
    """
    A Django admin interface class for the Census model.

    Configures how the Census model is displayed and interacted with in the Django admin interface. This includes settings for how the list of Census records is displayed, which fields are used for filtering and searching.

    Attributes:
        list_display: Specifies the fields of the Census model to be displayed in the list view.
        list_filter: Specifies the fields of the Census model to be used for filtering in the list view.
        search_fields: Specifies the fields of the Census model to be used for searching in the list view.
    """

    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )

    search_fields = ('voter_id', )


admin.site.register(Census, CensusAdmin)
