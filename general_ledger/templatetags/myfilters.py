from datetime import date
from decimal import Decimal
from django.db import models

from django_jinja import library
import jinja2
from django.urls import reverse
from django.utils.html import format_html

from general_ledger.django.models import Invoice
from crispy_forms.utils import render_crispy_form
from django_jinja import library

from django.template.defaulttags import lorem

import random

LOREM_TEXT = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor "
    "incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud "
    "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat"
).split()

NIETZSCHE_TEXT = (
    "Ultimate virtues hope sea good. Horror revaluation zarathustra intentions will dead "
    "inexpedient good christian. War pious derive faith hope burying christianity morality justice "
    "noble. Free abstract decrepit superiority inexpedient. "
    "Snare decrepit superiority horror transvaluation truth madness love. Dead holiest faith "
    "philosophy fearful strong endless prejudice spirit truth endless strong free. Horror "
    "God is dead. God remains dead. And we have killed him. How shall we comfort "
    "decrepit eternal-return gains overcome victorious sexuality ubermensch of joy contradict "
    "ascetic insofar hatred Inexpedient reason philosophy truth depths truth oneself morality "
    "love derive love prejudice victorious disgust. Marvelous reason reason fearful against "
    "sea Selfish justice depths moral of ultimate pinnacle revaluation good strong "
    "Eternal-return value good intentions value society fearful deceptions derive "
    "eternal-return ocean christian right morality. Self law faithful ocean transvaluation "
    "Self virtues reason value faith merciful burying decrepit noble. Law fearful of "
    "against christian burying deceptions truth love law pious inexpedient. Chaos "
    "victorious pious hatred overcome. Mountains philosophy marvelous overcome inexpedient "
    "strong aversion enlightenment prejudice battle christianity spirit burying. Truth "
    "passion strong eternal-return passion hatred burying superiority."
).split()


def generate_lorem_text(count=1, method="words", randomize=False):
    """
    Generates lorem ipsum text.
    - count: Number of words or paragraphs
    - method: 'words' or 'paragraphs'
    - randomize: If True, shuffle the text for random output
    """
    if method == "paragraphs":
        lorem_paragraph = " ".join(NIETZSCHE_TEXT)
        paragraphs = [lorem_paragraph for _ in range(count)]
        if randomize:
            random.shuffle(paragraphs)
        return "\n\n".join(paragraphs)
    else:
        words = LOREM_TEXT * ((count // len(LOREM_TEXT)) + 1)
        if randomize:
            random.shuffle(words)
        return " ".join(words[:count])


# Register the function as a global in Jinja
library.global_function(generate_lorem_text)


@library.global_function
def inject_today_date():
    return date.today().strftime("%Y-%m-%d")


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
