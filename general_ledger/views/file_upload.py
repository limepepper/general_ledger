import codecs

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.views.generic import (
    ListView,
    UpdateView,
    DetailView,
)
from general_ledger.forms.file_upload import FileUploadForm
from general_ledger.models import FileUpload
from ofxparse import OfxParser

from general_ledger.views import GeneralLedgerSecurityMixIn
from general_ledger.views.generic import GenericListView
from general_ledger.views.mixins import ActiveBookRequiredMixin


class FileUploadListView(GenericListView):
    model = FileUpload
    # template_name = "gl/file_upload_list.html.j2"


class FileUploadCreateView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    FormView,
):
    model = FileUpload
    form_class = FileUploadForm
    template_name = "gl/file_upload.html.j2"
    success_url = reverse_lazy("general_ledger:file-upload-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        # obj = form.save(commit=False)
        if self.request.FILES:
            for f in self.request.FILES.getlist("file"):
                obj = self.model.objects.create(
                    file=f,
                    book=self.request.active_book,
                )
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
