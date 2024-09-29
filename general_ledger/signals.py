from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from loguru import logger
from rich import inspect
from xstate_machine import pre_transition

from general_ledger.helpers.invoice import InvoiceHelper
from general_ledger.models import (
    Invoice,
    InvoiceLine,
    PaymentItem,
    Payment,
    Transaction,
)
from general_ledger.models.invoice_transaction import InvoiceTransaction


@receiver(pre_save, sender=Invoice)
def store_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_status = Invoice.objects.get(pk=instance.pk).status
        except Invoice.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Invoice)
def trigger_invoice_processing(
    sender, instance, created, raw, using, update_fields, **kwargs
):

    logger.info("handling post save signal for invoice")
    if not created and hasattr(instance, "_previous_status"):
        if instance.status != instance._previous_status:
            logger.info("handling state change for invoice")
            process_invoice_state_change(
                instance.pk,
                instance.status,
                instance._previous_status,
            )


def process_invoice_state_change(
    invoice_pk,
    current_status,
    previous_status,
):
    logger.info(
        f"Invoice state change {invoice_pk} : {previous_status} -> {current_status}"
    )
    invoice_helper = InvoiceHelper(pk=invoice_pk)
    invoice_helper.do_state_change(previous_status, current_status)


# update the invoice total after a line is saved or deleted
@receiver(post_save, sender=InvoiceLine)
@receiver(post_delete, sender=InvoiceLine)
def update_invoice_total(sender, instance, **kwargs):
    print(f"calling post delete signal in invoice line")
    instance.invoice.recalculate_total()
    instance.invoice.save()


# update the parent total after child changes
@receiver(post_save, sender=PaymentItem)
@receiver(post_delete, sender=PaymentItem)
def update_payment_total(sender, instance, **kwargs):
    instance.payment.recalculate_total()
    instance.payment.save()


@receiver(pre_transition, sender=Payment)
def payment_state_change(sender, instance, name, source, target, **kwargs):
    # inspect(logger)
    logger.info(f"Payment state change {source} -> {target}")
    # print("Payment state change")


@receiver(post_delete, sender=InvoiceTransaction)
def delete_related_transaction(sender, instance, **kwargs):
    try:
        txs = Transaction.objects.get(id=instance.transaction.id)
        txs.delete()
        inspect(txs)
    except Transaction.DoesNotExist:
        pass  # No related transaction found, nothing to do


# @receiver(post_save, sender=InvoiceTransaction)
# def log_post_save(sender, instance, **kwargs):
#     notify.send(
#         instance,
#         recipient=get_user_model().objects.get(username="admin"),
#         verb="was saved",
#     )
# Notification.objects.unread()
