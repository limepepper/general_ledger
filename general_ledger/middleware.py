from .models import Book
import uuid
import time
from loguru import logger


def logging_middleware(get_response):
    def middleware(request):
        # Create a request ID
        request_id = str(uuid.uuid4())

        # Add context to all loggers in all views
        with logger.contextualize(request_id=request_id):

            request.start_time = time.time()

            response = get_response(request)

            elapsed = time.time() - request.start_time

            # After the response is received
            logger.bind(
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                elapsed=elapsed,
            ).info(
                "incoming '{method}' request to '{path}'",
                method=request.method,
                path=request.path,
            )

            response["X-Request-ID"] = request_id

            return response

    return middleware


class ActiveBookMiddleware:
    """
    Middleware to set the active book for the request
    """

    logger.trace("ActiveBookMiddleware")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            active_book_pk = request.session.get("active_book_pk")
            if active_book_pk:
                try:
                    logger.trace(f"middleware setting active book: {active_book_pk}")
                    # @todo this needs to check the user has access to the book
                    request.active_book = Book.objects.get(pk=active_book_pk)
                except Book.DoesNotExist:
                    request.active_book = None
            else:
                request.active_book = None
        else:
            request.active_book = None

        response = self.get_response(request)
        # print(f"processed middleware {request.active_book}")
        return response
