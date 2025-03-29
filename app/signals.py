from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *

# 🔔 Notifier lors de la perte d'un lead
@receiver(post_save, sender=BitaBoxLead)
def notify_lost_lead(sender, instance, **kwargs):
    if instance.statut == 'perdu':  # Supposons que "lost" est un statut défini pour un lead perdu
        BitaBoxNotification.objects.create(
            user=instance.commercial,
            event_type='lost_lead',
            message=f"Lead perdu : {instance.nom+" "+instance.prenom}",
        )

# 🔔 Notifier lors de la creation d'un lead
@receiver(post_save, sender=BitaBoxLead)
def notify_new_lead(sender, instance, **kwargs):
    if instance.statut == 'nouveau':  # Supposons que "nouveau" est un statut défini pour un lead nouveau
        BitaBoxNotification.objects.create(
            user=instance.commercial,
            event_type='new_lead',
            message=f"Lead Nouveau : {instance.nom+" "+instance.prenom}",
        )

# 🔔 Notifier lorsqu'un lead est converti
@receiver(post_save, sender=BitaBoxLead)
def notify_converti_lead(sender, instance, **kwargs):
    if instance.statut == 'converti':  # Supposons que "lost" est un statut défini pour un lead converti
        BitaBoxNotification.objects.create(
            user=instance.commercial,
            event_type='converti_lead',
            message=f"Lead Converti : {instance.nom+" "+instance.prenom}",
        )