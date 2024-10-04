import logging
from datetime import date
from decimal import Decimal, ROUND_HALF_EVEN

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from loguru import logger
from simple_history.models import HistoricalRecords

from general_ledger.managers.invoice import InvoiceManager, InvoiceQuerySet
from general_ledger.models import Book
from general_ledger.models.invoice_base import InvoiceBaseMixin
from general_ledger.models.tax_inclusive import TaxInclusive
from general_ledger.models.validators import validate_is_customer


class Invoice(
    InvoiceBaseMixin,
):
    """
    https://docs.oasis-open.org/ubl/os-UBL-2.3/mod/summary/reports/UBL-Invoice-2.3.html
    """

    logger = logging.getLogger(f"{__name__}.{__qualname__}")
    objects = InvoiceManager.from_queryset(queryset_class=InvoiceQuerySet)()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        db_table = "gl_invoice"
        ordering = ["-created_at"]

    # invoice_lines = Manager.from_queryset(self.items.get_queryset)()

    # generic view class attributes
    links_detail = "general_ledger:invoice-detail"
    links_list = "general_ledger:invoice-list"
    links_create = "general_ledger:invoice-create"
    links_edit = "general_ledger:invoice-update"
    links_title_field = "invoice_number"

    generic_list_display = (
        "link",
        "due_date",
        # "date",
        "contact",
        # "description",
        "total_amount",
        "status",
        "tax_inclusive",
    )

    # @TODO move to standalone
    class InvoiceStatus(models.TextChoices):
        DRAFT = "DR", _("Draft")
        AWAITING_APPROVAL = "AA", _("Awaiting Approval")
        AWAITING_PAYMENT = "AP", _("Awaiting Payment")
        PAID = "PD", _("Paid")

    status = models.CharField(
        max_length=2,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
    )

    @property
    def status_display(self):
        return self.InvoiceStatus(self.status).label

    def limit_contact_choices(self):
        return {"is_customer": True}

    contact = models.ForeignKey(
        "Contact",
        on_delete=models.CASCADE,
        limit_choices_to={"is_customer": True},
        # validators=[validate_is_customer],
    )

    tax_inclusive = models.CharField(
        max_length=3,
        choices=TaxInclusive.choices,
        default=TaxInclusive.EXCLUSIVE,
        null=True,
        blank=True,
    )

    bank_account = models.ForeignKey(
        "Bank",
        on_delete=models.CASCADE,
        related_name="bank_accounts",
        null=True,
        blank=True,
    )

    transactions = models.ManyToManyField(
        "Transaction",
        related_name="invoices",
        through="InvoiceTransaction",
    )

    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        default=0,
    )

    @property
    def amount(self):
        return self.total_amount

    def get_invoice_number(self):
        return self.invoice_number

    def __str__(self):
        return f"{self.invoice_number}:{self.date}:[{self.total_amount:4,.2f}]:{self.status}"

    #
    ## Do custom handling stuff upon saving an invoice
    #
    def save(self, *args, **kwargs):
        logger.trace(f"Invoice: [saving] {self._state}")
        if self._state.adding:
            if self.ledger_id is not None:
                # @TODO this is a hack to get the next invoice number
                # causes a problem with validation because the
                # f expression can't be validated
                instance = Book.objects.get(pk=self.ledger.book.pk)
                if instance:
                    instance.invoice_sequence = F("invoice_sequence") + 1
                    instance.save()
                else:
                    logger.error("unable to update invoice sequence")
        self.recalculate_total()
        super().save(*args, **kwargs)

    def recalculate_total(self):
        try:
            self.total_amount = self.total_inclusive().quantize(
                Decimal("0.0000"), ROUND_HALF_EVEN
            )
        except Exception as e:
            logger.error(f"error calculating total amount {e}")

    @property
    def next_status(self):
        return self.get_next_status()

    def get_next_status(self):
        if self.is_draft():
            return self.InvoiceStatus.AWAITING_APPROVAL
        if self.is_awaiting_approval():
            return self.InvoiceStatus.AWAITING_PAYMENT
        if self.is_awaiting_payment():
            return self.InvoiceStatus.PAID
        if self.is_fully_paid():
            return None

    @property
    def prev_status(self):
        return self.get_prev_status()

    # @:TODO get rid of is_paid field
    def get_prev_status(self):
        if self.is_awaiting_approval():
            return self.InvoiceStatus.DRAFT
        if self.is_awaiting_payment():
            return self.InvoiceStatus.AWAITING_APPROVAL
        if Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.PAID:
            return self.InvoiceStatus.AWAITING_PAYMENT
        return None

    # @TODO this dumb
    def get_sales_account(self):
        """
        this does a walk through various relationships to find a sales account
        :return:
        """
        if self.sales_account:
            return self.sales_account
        if self.contact.sales_account:
            return self.contact.sales_account
        return self.ledger.coa.get_sales_account()
        # @TODO can never do this as CoA will find one
        # also as copilot pointed out it is circular
        # if self.ledger.book.sales_account:
        #     return self.ledger.book.sales_account

    def get_sales_vat_account(self):
        return self.ledger.coa.account_set.get(
            slug="vat",
        )

    def get_sales_vat_rate(self):
        """
        this does a walk through various relationships to find a default rate account
        :return:
        """
        if self.sales_tax_rate:
            return self.sales_tax_rate
        if self.contact.sales_tax_rate:
            return self.contact.sales_tax_rate
        if self.ledger.book.sales_tax_rate:
            return self.ledger.book.sales_tax_rate
        return self.ledger.book.taxrate_set.get(
            tax_type__slug="sales",
            is_default=True,
        )

    def get_accounts_receivable(self):
        """
        this should check the invoice for an override value
        then check the contact, and fall back to a ledger default
        :return:
        """
        # if self.ledger.coa.accounts_receivable:
        return self.ledger.coa.account_set.get(
            slug="accounts-receivable",
        )

    def subtotal(self):
        """
        Calculate the subtotal (sum of line totals excluding tax).
        """
        return sum(line.line_total_exclusive()[0] for line in self.invoice_lines.all())

    def total_exclusive(self):
        return self.subtotal()

    def total_tax(self):
        """
        Calculate the total tax amount for the invoice.
        """
        return sum(line.tax_amount()[0] for line in self.invoice_lines.all())

    def total_inclusive(self):
        """
        Calculate the total invoice amount including tax.
        """
        return Decimal(
            sum(line.line_total_inclusive() for line in self.invoice_lines.all())
        )

    def total_by_tax_type(self):
        """
        Calculate the total amount by tax type.
        Returns a dictionary where the keys are tax rates and the values are the total amounts for that tax rate.
        """
        tax_totals = {}
        for line in self.invoice_lines.all():
            tax_rate = line.vat_rate
            if tax_rate not in tax_totals:
                tax_totals[tax_rate] = Decimal(0)

            tax_totals[tax_rate] += line.tax_amount()[0]

        # print(tax_totals)
        return tax_totals

    # work flow methods

    def is_draft(self):
        return Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.DRAFT

    @property
    def is_posted(self):
        return Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_PAYMENT

    @property
    def is_overdue(self):
        return all(
            [
                self.is_posted,
                self.due_date < date.today(),
            ]
        )

    @property
    def is_paid(self):
        return Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.PAID

    def is_awaiting_approval(self):
        return (
            Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_APPROVAL
        )

    def is_awaiting_payment(self):
        return Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_PAYMENT

    # def is_partial_paid(self):
    #     return self.total_inclusive() > self.total_amount

    def is_fully_paid(self):
        return all(
            [
                Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.PAID,
                self.is_paid,
            ]
        )

    def can_approve(self):
        return Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.DRAFT

    def can_unapprove(self):
        return self.status != self.InvoiceStatus.PAID

    def can_redraft(self):
        return (
            Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_APPROVAL
        )

    def can_cancel(self):
        return any(
            [
                Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.DRAFT,
                Invoice.InvoiceStatus(self.status)
                == self.InvoiceStatus.AWAITING_PAYMENT,
            ]
        )

    def can_edit(self):
        return all(
            [
                Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.DRAFT,
                not self.is_locked,
            ]
        )

    def can_record(self):
        return all(
            [
                Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.DRAFT,
                self.is_active,
                not self.is_locked,
            ]
        )

    # @TODO this is a placeholder for some check that the
    # invoice can be progressed to a payable state
    # this should probably be something like ready-for-customer
    def can_pay(self):
        return self.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_APPROVAL

    def can_send(self):
        return (
            Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_APPROVAL
        )

    def can_post(self):
        return (
            Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_APPROVAL
        )

    def can_unpost(self):
        return Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_PAYMENT

    def can_prev(self):
        """
        Check if the invoice can be moved to the previous status.
        :return:
        """
        if Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_APPROVAL:
            return self.can_redraft()
        if Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_PAYMENT:
            return self.can_unpost()
        if Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.PAID:
            return False

    def can_next(self):
        """
        Check if the invoice can be moved to the next status.
        :return:
        """
        if any(
            [
                self.is_locked,
                self.is_paid,
                Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.PAID,
            ]
        ):
            return False
        if Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.DRAFT:
            return self.can_approve()
        if Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_APPROVAL:
            return self.can_pay()
        if Invoice.InvoiceStatus(self.status) == self.InvoiceStatus.AWAITING_PAYMENT:
            return self.is_paid

    def mark_approved(self):
        self.status = self.InvoiceStatus.AWAITING_PAYMENT
        self.save()

    def reconcile(self):
        self.mark_paid()

    def mark_paid(self):
        self.status = self.InvoiceStatus.PAID
        self.save()

    def mark_draft(self):
        self.status = self.InvoiceStatus.DRAFT
        self.save()

    def mark_awaiting_approval(self):
        self.status = self.InvoiceStatus.AWAITING_APPROVAL
        self.save()

    def do_next(self):
        self.status = self.next_status
        self.save()

    def do_prev(self):
        self.status = self.prev_status
        self.save()

    def do_posted(self):
        if self.is_draft() and self.can_record():
            self.do_next()
        if self.is_awaiting_approval() and self.can_post():
            self.do_next()

