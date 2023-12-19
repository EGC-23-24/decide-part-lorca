from django.contrib.admin import SimpleListFilter


class StartedFilter(SimpleListFilter):
    """
    A custom filter for the Django admin interface to filter objects based on their start status.

    This filter allows admin users to filter objects based on whether they have started, are running, or have finished.

    Attributes:
        title (str): The title displayed on the filter interface.
        parameter_name (str): The name of the parameter used in the query string.
    """

    title = 'started'
    parameter_name = 'started'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples containing the lookup options for this filter.

        :param request: The HttpRequest object.
        :type request: HttpRequest
        :param model_admin: The ModelAdmin object for the model.
        :type model_admin: ModelAdmin
        :return: List of tuples, where each tuple represents a lookup option.
        :rtype: list
        """

        return [
            ('NS', 'Not started'),
            ('S', 'Started'),
            ('R', 'Running'),
            ('F', 'Finished'),
        ]

    def queryset(self, request, queryset):
        """
        Returns the queryset filtered based on the selected lookup option.

        :param request: The HttpRequest object.
        :type request: HttpRequest
        :param queryset: The original queryset.
        :type queryset: QuerySet
        :return: Filtered queryset based on the selected lookup option.
        :rtype: QuerySet
        """

        if self.value() == 'NS':
            return queryset.filter(start_date__isnull=True)
        if self.value() == 'S':
            return queryset.exclude(start_date__isnull=True)
        if self.value() == 'R':
            return queryset.exclude(
                start_date__isnull=True).filter(
                end_date__isnull=True)
        if self.value() == 'F':
            return queryset.exclude(end_date__isnull=True)
        else:
            return queryset.all()
