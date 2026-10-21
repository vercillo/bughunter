from django.conf import settings
from django.db import models


class Bug(models.Model):

    SEVERITY_CHOICES = [
        ("critical", "Critical"),
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("fixed", "Fixed"),
        ("retest", "Retest"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reported_bugs",
        null=True,
        blank=True,
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_bugs",
    )

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default="medium",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    bug = models.ForeignKey(
        Bug,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bug_comments',
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.bug}'