from django.shortcuts import render, redirect, get_object_or_404
from .models import Bug
from .forms import BugForm

def bug_list(request):
    bugs = Bug.objects.all()
    
    search_query = request.GET.get('q', '').strip()
    severity = request.GET.get('severity', '')
    status = request.GET.get('status', '')
    sort_by = request.GET.get('sort', 'newest')

    if search_query:
        from django.db.models import Q
        bugs = bugs.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        
    if severity in dict(Bug.SEVERITY_CHOICES):
        bugs = bugs.filter(severity=severity)

    if status in dict(Bug.STATUS_CHOICES):
        bugs = bugs.filter(status=status)

    sort_options = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'severity': 'severity',
    }

    if sort_by not in sort_options:
        sort_by = 'newest'

    bugs = bugs.order_by(sort_options[sort_by])
    bug_count = bugs.count()

    context = {
        'bugs': bugs,
        'search_query': search_query,
        'selected_severity': severity,
        'selected_status': status,
        'selected_sort': sort_by,
        'bug_count': bug_count,
    }

    return render(request, "bugs/bug_list.html", context)

def bug_create(request):
    if request.method == 'POST':
        form = BugForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('bug_list')
    else:
        form = BugForm()

    return render(request, 'bugs/bug_form.html', {'form': form})

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