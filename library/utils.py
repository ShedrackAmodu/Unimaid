from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate_queryset(queryset, page_number, per_page=10):
    """
    Utility function to paginate a queryset with consistent error handling.

    Args:
        queryset: Django queryset to paginate
        page_number: Page number from request.GET.get('page')
        per_page: Number of items per page (default: 10)

    Returns:
        Paginated page object
    """
    paginator = Paginator(queryset, per_page)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj
