from django.shortcuts import render, redirect, get_object_or_404
from .models import Bug
from .forms import BugForm
from django.contrib.auth import login
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required


def bug_list(request):
    from django.db.models import Q

    bugs = Bug.objects.all()

    search_query = request.GET.get("q", "").strip()
    severity = request.GET.get("severity", "")
    status = request.GET.get("status", "")
    sort_by = request.GET.get("sort", "newest")

    # Search by title or description
    if search_query:
        bugs = bugs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filter by severity
    if severity in dict(Bug.SEVERITY_CHOICES):
        bugs = bugs.filter(severity=severity)

    # Filter by status
    if status in dict(Bug.STATUS_CHOICES):
        bugs = bugs.filter(status=status)

    # Sorting
    sort_options = {
        "newest": "-created_at",
        "oldest": "created_at",
        "severity": "severity",
    }

    if sort_by not in sort_options:
        sort_by = "newest"

    bugs = bugs.order_by(sort_options[sort_by])

    # Count bugs matching the current filters
    bug_count = bugs.count()

    # Dashboard statistics: always count all bugs,
    # regardless of the active search or filters
    total_bugs = Bug.objects.count()
    open_bugs = Bug.objects.filter(status="open").count()
    in_progress_bugs = Bug.objects.filter(status="in_progress").count()
    fixed_bugs = Bug.objects.filter(status="fixed").count()

    context = {
        "bugs": bugs,
        "search_query": search_query,
        "selected_severity": severity,
        "selected_status": status,
        "selected_sort": sort_by,
        "bug_count": bug_count,
        "total_bugs": total_bugs,
        "open_bugs": open_bugs,
        "in_progress_bugs": in_progress_bugs,
        "fixed_bugs": fixed_bugs,
    }

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

    return render(request, "bugs/bug_form.html", {"form": form})

def bug_detail(request, bug_id):
    bug = get_object_or_404(Bug, id=bug_id)
    return render(request, 'bugs/bug_detail.html', {'bug': bug})

def bug_edit(request, bug_id):
    bug = get_object_or_404(Bug, id=bug_id)

    if request.method == 'POST':
        form = BugForm(request.POST, instance=bug)

        if form.is_valid():
            form.save()
            return redirect('bug_detail', bug_id=bug_id)
    else:
        form = BugForm(instance=bug)

    return render(request, 'bugs/bug_form.html', {'form': form, 'editing': True,})

def landing(request):
    return render(request, 'bugs/landing.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('bug_list')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('bug_list')
    else:
        form = RegistrationForm()

    return render(request, 'bugs/register.html', {'form': form})

@login_required
def my_bugs(request):
    bugs = Bug.objects.filter(
        reported_by=request.user
    ).order_by("-created_at")

    return render(request, "bugs/bug_list.html", {
        "bugs": bugs,
        "page_title": "My Bugs",
    })