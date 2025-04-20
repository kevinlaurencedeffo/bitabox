from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

# 🔔 ———————— BitaBoxLead ————————

@receiver(post_save, sender=BitaBoxLead)
def handle_lead_events(sender, instance, created, **kwargs):
    if not instance.commercial:
        return  # Cannot notify if no commercial is associated

    if created:
        BitaBoxNotification.objects.create(
            user=instance.commercial,
            event_type='new',
            message=f"New lead: {instance.name} {instance.surname}"
        )
    else:
        status = instance.status
        messages = {
            'Initial Call': f"Lead initialized: {instance.name} {instance.surname}",
            'no_answer': f"No answer from lead: {instance.name} {instance.surname}",
            'not_interested': f"Lead not interested: {instance.name} {instance.surname}",
            'call_back': f"Call back requested for lead: {instance.name} {instance.surname}",
            'wrong_number': f"Wrong number for lead: {instance.name} {instance.surname}",
            'wrong_info': f"Incorrect info for lead: {instance.name} {instance.surname}",
            'hung_up': f"Lead hung up: {instance.name} {instance.surname}",
            'never_answer': f"Lead never answers: {instance.name} {instance.surname}",
            'converti': f"Lead converted: {instance.name} {instance.surname}",
        }

        # Define event type based on status
        event_type = (
            'converted_lead' if status == 'converti'
            else 'lost_lead' if status in ['not_interested', 'wrong_info', 'hung_up', 'never_answer', 'wrong_number']
            else 'new_lead'
        )

        # Only create notification if status is recognized
        if status in messages:
            BitaBoxNotification.objects.create(
                user=instance.commercial,
                event_type=event_type,
                message=messages[status]
            )

@receiver(post_delete, sender=BitaBoxLead)
def notify_deleted_lead(sender, instance, **kwargs):
    if instance.commercial:
        BitaBoxNotification.objects.create(
            user=instance.commercial,
            event_type='lost_lead',
            message=f"Lead deleted: {instance.name} {instance.surname}"
        )


# 🔔 ———————— BitaBoxUtilisateur ————————

@receiver(post_save, sender=User)
def notify_user_created_or_updated(sender, instance, created, **kwargs):
    if created:
        BitaBoxNotification.objects.create(
            user=instance,
            event_type='new_user',
            message=f"New user added: {instance.username}"
        )
    else:
        BitaBoxNotification.objects.create(
            user=instance,
            event_type='updated_user',
            message=f"User updated: {instance.username}"
        )

@receiver(post_delete, sender=User)
def notify_user_deleted(sender, instance, **kwargs):
    # Assume that an admin receives the notification
    admins = User.objects.filter(is_superuser=True)
    for admin in admins:
        BitaBoxNotification.objects.create(
            user=admin,
            event_type='lost_user',
            message=f"User deleted: {instance.username}"
        )


# 🔔 ———————— BitaBoxEntreprise ————————

@receiver(post_save, sender=BitaBoxEntreprise)
def notify_entreprise_created_or_updated(sender, instance, created, **kwargs):
    message = f"New company: {instance.name}" if created else f"Company updated: {instance.name}"
    admins = User.objects.filter(is_superuser=True)
    for admin in admins:
        BitaBoxNotification.objects.create(
            user=admin,
            event_type='new_enterprise',
            message=message
        )

@receiver(post_delete, sender=BitaBoxEntreprise)
def notify_entreprise_deleted(sender, instance, **kwargs):
    admins = User.objects.filter(is_superuser=True)
    for admin in admins:
        BitaBoxNotification.objects.create(
            user=admin,
            event_type='lost_enterprise',
            message=f"Company deleted: {instance.name}"
        )
