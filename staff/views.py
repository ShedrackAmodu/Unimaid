from django.shortcuts import render, get_object_or_404
from library.utils import paginate_queryset
from .models import StaffMember


def staff_list(request):
    """Display list of staff members with pagination"""
    staff_members = StaffMember.objects.all().order_by("order", "name")

    staff_page = paginate_queryset(staff_members, request.GET.get("page"), per_page=12)

    context = {
        "staff_members": staff_page,
        "page_title": "Library Staff",
    }
    return render(request, "staff/staff_list.html", context)


def staff_detail(request, pk):
    """Display individual staff member"""
    staff_member = get_object_or_404(StaffMember, pk=pk)

    context = {
        "staff_member": staff_member,
        "page_title": staff_member.name,
    }
    return render(request, "staff/staff_detail.html", context)
