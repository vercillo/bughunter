
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST

from .models import Bug, Comment
from .forms import (
    BugForm,
    BugAssignmentForm,
    RegistrationForm,
    TechBugEditForm,
    SuperuserBugEditForm,
    TechStaffCreationForm,
    CommentForm,
)


def is_tech_staff(user):
    """Return True for authenticated Tech Team members and superusers."""
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name="Tech Team").exists()
        )
    )


def is_staff_user(user):
    """Backward-compatible alias for existing templates."""
    return is_tech_staff(user)


def superuser_check(user):
    return user.is_authenticated and user.is_superuser


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
        "is_superuser": request.user.is_superuser,
        "page_title": page_title,
        "search_query": search_query,
        "selected_severity": severity,
        "selected_status": status,
        "selected_sort": sort_by,
        "bug_count": filtered_bugs.count(),
    }


@login_required
def bug_list(request):
    """Staff see every bug; regular users see only bugs they reported."""
    staff_user = is_tech_staff(request.user)

    if staff_user:
        permitted_bugs = Bug.objects.all()
    else:
        permitted_bugs = Bug.objects.filter(reported_by=request.user)

    context = get_bug_list_context(
        request=request,
        bugs=permitted_bugs,
        page_title="Dashboard",
        is_staff=staff_user,
    )

    context.update({
        "total_bugs": permitted_bugs.count(),
        "open_bugs": permitted_bugs.filter(status="open").count(),
        "in_progress_bugs": permitted_bugs.filter(
            status="in_progress"
        ).count(),
        "retest_bugs": permitted_bugs.filter(status="retest").count(),
        "closed_bugs": permitted_bugs.filter(status="closed").count(),
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
            "is_staff_user": is_tech_staff(request.user),
            "is_superuser": request.user.is_superuser,
        },
    )


@login_required
def bug_detail(request, bug_id):
    bug = get_object_or_404(Bug, id=bug_id)
    staff_user = is_tech_staff(request.user)

    # Regular users can only access their own reports.
    if not staff_user and bug.reported_by_id != request.user.id:
        raise Http404

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.bug = bug
            comment.author = request.user
            comment.save()
            return redirect("bug_detail", bug_id=bug.id)
    else:
        form = CommentForm()

    comments = bug.comments.select_related("author").all()

    # Use a set so the template can correctly identify Tech Team authors,
    # even when a user belongs to multiple groups.
    tech_user_ids = set(
        User.objects.filter(groups__name="Tech Team")
        .values_list("id", flat=True)
    )

    return render(
        request,
        "bugs/bug_detail.html",
        {
            "bug": bug,
            "is_staff_user": staff_user,
            "is_superuser": request.user.is_superuser,
            "comments": comments,
            "comment_form": form,
            "tech_user_ids": tech_user_ids,
        },
    )



@login_required
def bug_edit(request, bug_id):
    bug = get_object_or_404(Bug, id=bug_id)
    user = request.user

    # Only Tech Team and Owner can edit bug reports.
    if not user.is_superuser and not is_tech_staff(user):
        raise Http404

    if user.is_superuser:
        form_class = SuperuserBugEditForm
    else:
        form_class = TechBugEditForm

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
            "is_staff_user": is_tech_staff(user),
            "is_superuser": user.is_superuser,
        },
    )



@login_required
def assign_bug(request, bug_id):
    # Only Tech Team members and superusers can assign bugs.
    if not is_tech_staff(request.user):
        raise Http404

    bug = get_object_or_404(Bug, id=bug_id)

    if request.method == "POST":
        form = BugAssignmentForm(request.POST, instance=bug)

        if form.is_valid():
            bug = form.save(commit=False)

            # Preserve existing behavior: assigning an open bug starts work.
            if bug.assigned_to and bug.status == "open":
                bug.status = "in_progress"

            bug.save()
            return redirect("bug_detail", bug_id=bug.id)
    else:
        form = BugAssignmentForm(instance=bug)

    return render(
        request,
        "bugs/bug_assign.html",
        {
            "form": form,
            "bug": bug,
            "is_superuser": request.user.is_superuser,
        },
    )


@login_required
def assigned_to_me(request):
    """Staff-only page listing bugs assigned to the current user."""
    if not is_tech_staff(request.user):
        raise Http404

    assigned_bugs = Bug.objects.filter(assigned_to=request.user)

    context = get_bug_list_context(
        request=request,
        bugs=assigned_bugs,
        page_title="Assigned to me",
        is_staff=True,
    )

    context.update({
        "total_bugs": assigned_bugs.count(),
        "open_bugs": assigned_bugs.filter(status="open").count(),
        "in_progress_bugs": assigned_bugs.filter(
            status="in_progress"
        ).count(),
        "retest_bugs": assigned_bugs.filter(status="retest").count(),
        "closed_bugs": assigned_bugs.filter(status="closed").count(),
    })

    return render(request, "bugs/bug_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def bug_delete(request, bug_id):
    """Only superusers can delete a bug."""
    if not request.user.is_superuser:
        raise Http404

    bug = get_object_or_404(Bug, id=bug_id)

    if request.method == "POST":
        bug.delete()
        return redirect("bug_list")

    return render(
        request,
        "bugs/bug_confirm_delete.html",
        {"bug": bug},
    )


@login_required
@user_passes_test(superuser_check, login_url="bug_list")
def add_tech_staff(request):
    """Allow only superusers to create Tech Team accounts."""
    tech_group, _ = Group.objects.get_or_create(name="Tech Team")

    if request.method == "POST":
        form = TechStaffCreationForm(request.POST)

        if form.is_valid():
            tech_user = form.save()
            tech_user.groups.add(tech_group)
            return redirect("assigned_to_me")
    else:
        form = TechStaffCreationForm()

    return render(
        request,
        "bugs/add_tech_staff.html",
        {"form": form},
    )


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
