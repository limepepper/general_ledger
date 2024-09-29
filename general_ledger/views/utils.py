import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from general_ledger.models import Book

logger = logging.getLogger(__name__)


@login_required
def select_active_entity(request):
    if request.method == "POST":
        book_pk = request.POST.get("book_pk")
        try:
            book = Book.objects.get(pk=book_pk)
            request.session["active_book_pk"] = str(book.pk)
            logger.debug("Active book set to %s", book.name)

        except Book.DoesNotExist:
            # Handle the case where the entity doesn't exist or the user doesn't have access
            logger.debug("no book ")
            pass
        next = request.POST.get("next")
        if next:

            return redirect(next)
        else:
            logger.debug("Redirecting to general ledger index")
            # @TODO this should redirect to the previous page
            return redirect("general_ledger:index")
    # books = request.user.accessible_books.all()
    books = Book.objects.for_user(request.user)
    active_book_pk = request.session.get("active_book_pk")
    logger.debug("Active book pk from session id %s", active_book_pk)
    return render(
        request,
        "gl/forms/select_active_entity.html.j2",
        {
            "books": books,
            "active_book_pk": active_book_pk,
            "next": request.GET.get("next"),
        },
    )
