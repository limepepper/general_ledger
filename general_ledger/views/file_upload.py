import codecs

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import (
    ListView,
    UpdateView,
    DetailView,
)
from general_ledger.forms.file_upload import FileUploadForm
from general_ledger.models import FileUpload
from ofxparse import OfxParser


class FileUploadCreateView(CreateView):
    model = FileUpload
    form_class = FileUploadForm
    template_name = "gl/file_upload.html.j2"
    # success_url = reverse_lazy("success")

    def form_valid(self, form):
        response = super().form_valid(form)
        # Trigger the background task after the object is saved
        # process_file_task.delay(self.object.id)
        return response


class FileUploadDetailView(DetailView):
    model = FileUpload

    template_name = "gl/file_upload_detail.html.j2"
    # success_url = reverse_lazy("success")

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context["file_contents"] = self.object.file.read().decode("utf-8")
    #     with codecs.open(self.object.file.path) as fileobj:
    #         ofx = OfxParser.parse(fileobj)
    #         context["ofx"] = ofx
    #     return context
