from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import string
import random



class BitaBoxUtilisateur(AbstractUser):
    id = models.AutoField(primary_key=True)  # ✅ Auto-incrémentation
    enterprise = models.ForeignKey("BitaBoxEntreprise", on_delete=models.CASCADE, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_commercial = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name="utilisateur_groups",  # ✅ Évite le conflit
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="utilisateur_permissions",  # ✅ Évite le conflit
        blank=True
    )
    class Meta:
        verbose_name = "Bitabox Utilisateur"
        verbose_name_plural = "Bitabox Utilisateurs"
    

    def __str__(self):
        return self.username

class BitaBoxEntreprise(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Bitabox Entreprise"
        verbose_name_plural = "Bitabox Entreprises"

    def __str__(self):
        return self.name


class BitaboxComment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(BitaBoxUtilisateur, on_delete=models.CASCADE)
    lead_id = models.ForeignKey("BitaBoxLead", on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.date} at {self.time}"
    class Meta:
        verbose_name = "Bitabox Comment"
        verbose_name_plural = "Bitabox Comments"

    def __str__(self):
        return f"{self.user.username} - {self.date} {self.time}"
    

def generate_lead_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class BitaBoxLead(models.Model):
    STATUS_CHOICES = [
        ("new", "New Lead"),
        ("init_call", "Initial Call"),
        ("no_answer", "No Answer"),
        ("not_interested", "Not interested"),
        ("call_back", "Call Back"),
        ("wrong_number", "Wrong Number"),
        ("wrong_info", "Wrong Info"),
        ("invalid", "Invalid"),
        ("hung_up", "Hung Up"),
        ("never_answer", "Never Answer"),
        ("converted", "Converted"),
    ]

    id = models.AutoField(primary_key=True)
    enterprise = models.ForeignKey(BitaBoxEntreprise, on_delete=models.CASCADE, related_name="leads")
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    contact = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="new")
    commercial = models.ForeignKey(BitaBoxUtilisateur, on_delete=models.SET_NULL, null=True, blank=True)

    # ✅ Newly added fields
    date = models.DateField(auto_now_add=True)
    time = time = models.TimeField(auto_now_add=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    call_code = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    id_lead = models.CharField(max_length=8, default=generate_lead_id, editable=False, unique=True)

    # ✅ Comments relation
    comments = models.ManyToManyField(BitaboxComment, related_name="lead_comments", blank=True)

    class Meta:
        verbose_name = "Bitabox Lead"
        verbose_name_plural = "Bitabox Leads"
        ordering = ['-date']

    def __str__(self):
        return f"Lead from {self.contact} - {self.status}"

class BitaBoxNotification(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Non lue'),
        ('read', 'Lue'),
    ]
    
    EVENT_TYPES = [
        ('new_lead', 'New lead'),
        ('lost_lead', 'Lost Lead'),
        ('converted', 'Converted Lead'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(BitaBoxUtilisateur, on_delete=models.CASCADE, related_name="notifications")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Bitabox Notification"
        verbose_name_plural = "Bitabox Notifications"

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.user.email}"