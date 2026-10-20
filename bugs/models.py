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