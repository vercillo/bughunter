from django.shortcuts import render, redirect, get_object_or_404
from .models import Bug
from .forms import BugForm

def bug_list(request):
    bugs = Bug.objects.all().order_by("-created_at")
    return render(request, "bugs/bug_list.html", {"bugs": bugs})

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