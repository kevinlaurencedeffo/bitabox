from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class BitaBoxUtilisateur(AbstractUser):
    id = models.AutoField(primary_key=True)  # ✅ Auto-incrémentation
    entreprise = models.ForeignKey("BitaBoxEntreprise", on_delete=models.CASCADE, null=True, blank=True)
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
    

    def __str__(self):
        return self.username

class BitaBoxEntreprise(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class BitaBoxLead(models.Model):
    STATUTS = [
        ("nouveau", "Nouveau"),
        ("en_cours", "En cours"),
        ("converti", "Converti"),
        ("perdu", "Perdu"),
    ]
    id = models.AutoField(primary_key=True)
    entreprise = models.ForeignKey(BitaBoxEntreprise, on_delete=models.CASCADE, related_name="leads")
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    contact = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    statut = models.CharField(max_length=10, choices=STATUTS, default="nouveau")
    date_reception = models.DateTimeField(auto_now_add=True)
    commercial = models.ForeignKey(BitaBoxUtilisateur, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Lead de {self.contact} - {self.statut}"

class BitaBoxNotification(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Non lue'),
        ('read', 'Lue'),
    ]

    EVENT_TYPES = [
        ('new_lead', 'Nouveau lead'),
        ('lost_lead', 'Lead perdu'),
        ('new_entreprise', 'Nouvelle entreprise'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(BitaBoxUtilisateur, on_delete=models.CASCADE, related_name="notifications")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.user.email}"