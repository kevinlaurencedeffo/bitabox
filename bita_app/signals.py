from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

# 🔔 ———————— BitaBoxLead ————————

@receiver(post_save, sender=BitaBoxLead)
def handle_lead_events(sender, instance, created, **kwargs):
    if not instance.commercial:
        return  # On ne peut pas notifier si aucun commercial n’est associé

    if created:
        BitaBoxNotification.objects.create(
            user=instance.commercial,
            event_type='new_lead',
            message=f"Nouveau lead : {instance.nom} {instance.prenom}"
        )
    else:
        statut = instance.statut
        messages = {
            'new': f"Lead réinitialisé : {instance.nom} {instance.prenom}",
            'no_answer': f"Pas de réponse pour le lead : {instance.nom} {instance.prenom}",
            'not_interested': f"Lead non intéressé : {instance.nom} {instance.prenom}",
            'call_back': f"Rappel demandé pour le lead : {instance.nom} {instance.prenom}",
            'wrong_number': f"Mauvais numéro pour le lead : {instance.nom} {instance.prenom}",
            'wrong_info': f"Infos erronées pour le lead : {instance.nom} {instance.prenom}",
            'hung_up': f"Le prospect a raccroché : {instance.nom} {instance.prenom}",
            'never_answer': f"Le prospect ne répond jamais : {instance.nom} {instance.prenom}",
            'converti': f"Lead converti : {instance.nom} {instance.prenom}",
        }

        # Définir le type d'événement selon le statut (peut être le même pour tous ou customisé)
        event_type = (
            'converti_lead' if statut == 'converti'
            else 'lost_lead' if statut in ['not_interested', 'wrong_info', 'hung_up', 'never_answer', 'wrong_number']
            else 'new_lead'  # Utilisé aussi pour 'new', 'call_back', 'no_answer'
        )

        # Créer la notification uniquement si le statut est reconnu
        if statut in messages:
            BitaBoxNotification.objects.create(
                user=instance.commercial,
                event_type=event_type,
                message=messages[statut]
            )

@receiver(post_delete, sender=BitaBoxLead)
def notify_deleted_lead(sender, instance, **kwargs):
    if instance.commercial:
        BitaBoxNotification.objects.create(
            user=instance.commercial,
            event_type='lost_lead',
            message=f"Lead supprimé : {instance.nom} {instance.prenom}"
        )


# 🔔 ———————— BitaBoxUtilisateur ————————

@receiver(post_save, sender=User)
def notify_user_created_or_updated(sender, instance, created, **kwargs):
    if created:
        BitaBoxNotification.objects.create(
            user=instance,
            event_type='new_lead',
            message=f"Nouvel utilisateur ajouté : {instance.username}"
        )
    else:
        BitaBoxNotification.objects.create(
            user=instance,
            event_type='converti_lead',
            message=f"Utilisateur mis à jour : {instance.username}"
        )

@receiver(post_delete, sender=User)
def notify_user_deleted(sender, instance, **kwargs):
    # On suppose qu'un admin reçoit la notif
    admins = User.objects.filter(is_superuser=True)
    for admin in admins:
        BitaBoxNotification.objects.create(
            user=admin,
            event_type='lost_lead',
            message=f"Utilisateur supprimé : {instance.username}"
        )


# 🔔 ———————— BitaBoxEntreprise ————————

@receiver(post_save, sender=BitaBoxEntreprise)
def notify_entreprise_created_or_updated(sender, instance, created, **kwargs):
    message = f"Nouvelle entreprise : {instance.nom}" if created else f"Entreprise mise à jour : {instance.nom}"
    admins = User.objects.filter(is_superuser=True)
    for admin in admins:
        BitaBoxNotification.objects.create(
            user=admin,
            event_type='new_lead',
            message=message
        )

@receiver(post_delete, sender=BitaBoxEntreprise)
def notify_entreprise_deleted(sender, instance, **kwargs):
    admins = User.objects.filter(is_superuser=True)
    for admin in admins:
        BitaBoxNotification.objects.create(
            user=admin,
            event_type='lost_lead',
            message=f"Entreprise supprimée : {instance.nom}"
        )
