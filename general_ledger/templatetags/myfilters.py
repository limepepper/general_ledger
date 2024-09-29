from datetime import date
from decimal import Decimal
from django.db import models

from django_jinja import library
import jinja2
from django.urls import reverse
from django.utils.html import format_html

from general_ledger.models import Invoice
from crispy_forms.utils import render_crispy_form
from django_jinja import library


@library.global_function()
def crispy(form, helper, context=None):
    return render_crispy_form(
        form,
        helper=helper,
        context=context,
    )


@library.filter
def itype(value):
    """
    Usage: {{ myvar|itype }}
    """
    return Invoice.InvoiceStatus(value)


@library.filter
def itypelab(value):
    """
    Usage: {{ myvar|itype }}
    """
    return Invoice.InvoiceStatus(value).label


@library.global_function()
def cancall(obj):
    return callable(obj)


@library.filter
def gen_field(value):
    """
    Usage: {[ field|gen_field() }}
    """
    if isinstance(value, date):
        return f"{value}"
    if isinstance(value, Decimal):
        return f"{curr(value)}"
    if isinstance(value, bool):
        return format_html(
            '<span class="fa fa-check-square"  style="font-size:24px;color:green"></span>'
            if value
            else '<span class="fa fa-window-close"  style="font-size:24px;color:red"></span>'
        )
    return value


@library.global_function
def fixthing():
    """
    Usage: {{ myecho('foo') }}
    """
    return '{"name": "#items", "options": {"prefix": "items", "addText": "Add One", "deleteText": "Remove"}}'


@library.filter
def dropdownmenu(title, name, query="", path=""):
    """
    Usage: {{ 'Hello'|dropdownmenu() }}
    """
    rv = reverse(name)
    is_active = rv == path
    return format_html(
        f"""
    <li><a class="dropdown-item {"active1" if is_active else ""}" href="{ rv }">{title}</a></li>
    """
    )


@library.filter
def curr(value):
    """
    Usage: {{ 100|currency }}
    """
    return f"£{value:,.2f}"
