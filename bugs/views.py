from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from .models import Bug
from .forms import (
    BugForm,
    BugAssignmentForm,
    RegistrationForm,
    TechBugEditForm,
)


def is_staff_user(user):
    """Staff are superusers or users in the Tech Team group."""
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name="Tech Team").exists()
        )
    )


def get_bug_list_context(request, bugs, page_title, is_staff):
    """Build consistent filters and statistics for bug-list pages."""
    search_query = request.GET.get("q", "").strip()
    severity = request.GET.get("severity", "") if is_staff else ""
    status = request.GET.get("status", "")
    sort_by = request.GET.get("sort", "newest")

    if search_query:
        bugs = bugs.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    if severity in dict(Bug.SEVERITY_CHOICES):
        bugs = bugs.filter(severity=severity)

    if status in dict(Bug.STATUS_CHOICES):
        bugs = bugs.filter(status=status)

    sort_options = {
        "newest": "-created_at",
        "oldest": "created_at",
    }

    if is_staff:
        sort_options["severity"] = "severity"

    if sort_by not in sort_options:
        sort_by = "newest"

    filtered_bugs = bugs.order_by(sort_options[sort_by])

    return {
        "bugs": filtered_bugs,
        "is_staff_user": is_staff,
        "page_title": page_title,
        "search_query": search_query,
        "selected_severity": severity,
        "selected_status": status,
        "selected_sort": sort_by,
        "bug_count": filtered_bugs.count(),
    }


@login_required
def bug_list(request):
    """Dashboard: staff see all bugs; regular users see their own."""
    staff_user = is_staff_user(request.user)

    if staff_user:
        all_bugs = Bug.objects.all()
    else:
        all_bugs = Bug.objects.filter(reported_by=request.user)

    context = get_bug_list_context(
        request=request,
        bugs=all_bugs,
        page_title="Dashboard",
        is_staff=staff_user,
    )

    # Statistics are based on the user's permitted bug queryset,
    # not on the currently selected filters.
    context.update({
        "total_bugs": all_bugs.count(),
        "open_bugs": all_bugs.filter(status="open").count(),
        "in_progress_bugs": all_bugs.filter(status="in_progress").count(),
        "fixed_bugs": all_bugs.filter(status="fixed").count(),
    })

    return render(request, "bugs/bug_list.html", context)


@login_required
def bug_create(request):
    if request.method == "POST":
        form = BugForm(request.POST)
        if form.is_valid():
            bug = form.save(commit=False)
            bug.reported_by = request.user
            bug.save()
            return redirect("bug_list")
    else:
        form = BugForm()

    return render(
        request,
        "bugs/bug_form.html",
        {
            "form": form,
            "editing": False,
            "is_staff_user": is_staff_user(request.user),
        },
    )


@login_required
def bug_detail(request, bug_id):
    bug = get_object_or_404(Bug, id=bug_id)
    staff_user = is_staff_user(request.user)

    # Regular users cannot view other people's reports, even by URL.
    if not staff_user and bug.reported_by_id != request.user.id:
        raise Http404

    return render(
        request,
        "bugs/bug_detail.html",
        {
            "bug": bug,
            "is_staff_user": staff_user,
        },
    )


@login_required
def bug_edit(request, bug_id):
    bug = get_object_or_404(Bug, id=bug_id)
    staff_user = is_staff_user(request.user)

    # Regular users can edit only bugs they reported themselves.
    if not staff_user and bug.reported_by_id != request.user.id:
        raise Http404

    form_class = TechBugEditForm if staff_user else BugForm

    if request.method == "POST":
        form = form_class(request.POST, instance=bug)
        if form.is_valid():
            form.save()
            return redirect("bug_detail", bug_id=bug.id)
    else:
        form = form_class(instance=bug)

    return render(
        request,
        "bugs/bug_form.html",
        {
            "form": form,
            "editing": True,
            "bug": bug,
            "is_staff_user": staff_user,
        },
    )


@login_required
def assign_bug(request, bug_id):
    # Only staff can assign or unassign bugs.
    if not is_staff_user(request.user):
        raise Http404

    bug = get_object_or_404(Bug, id=bug_id)

    if request.method == "POST":
        form = BugAssignmentForm(request.POST, instance=bug)
        if form.is_valid():
            form.save()
            return redirect("bug_detail", bug_id=bug.id)
    else:
        form = BugAssignmentForm(instance=bug)

    return render(
        request,
        "bugs/bug_assign.html",
        {
            "form": form,
            "bug": bug,
        },
    )


@login_required
def assigned_to_me(request):
    """Staff-only page listing bugs assigned to the current user."""
    if not is_staff_user(request.user):
        raise Http404

    all_assigned_bugs = Bug.objects.filter(assigned_to=request.user)

    context = get_bug_list_context(
        request=request,
        bugs=all_assigned_bugs,
        page_title="Assigned to me",
        is_staff=True,
    )

    context.update({
        "total_bugs": all_assigned_bugs.count(),
        "open_bugs": all_assigned_bugs.filter(status="open").count(),
        "in_progress_bugs": all_assigned_bugs.filter(
            status="in_progress"
        ).count(),
        "fixed_bugs": all_assigned_bugs.filter(status="fixed").count(),
    })

    return render(request, "bugs/bug_list.html", context)


def landing(request):
    return render(request, "bugs/landing.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("bug_list")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("bug_list")
    else:
        form = RegistrationForm()

    return render(request, "bugs/register.html", {"form": form})