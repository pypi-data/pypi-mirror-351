from django.contrib import messages
from django.http import Http404, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from pretalx.common.views.mixins import PermissionRequired

from .forms import VimeoUrlForm
from .models import VimeoLink


class VimeoSettings(PermissionRequired, FormView):
    permission_required = "event.update_event"
    template_name = "pretalx_vimeo/settings.html"
    form_class = VimeoUrlForm

    def get_success_url(self):
        return self.request.path

    def get_object(self):
        return self.request.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["event"] = self.request.event
        return kwargs

    def post(self, *args, **kwargs):
        if not self.request.event.current_schedule:
            messages.error(self.request, _("Please create a schedule first!"))
            return self.get(self.request, *args, **kwargs)
        form = self.get_form()
        if not form.is_valid():
            messages.error(self.request, _("Please fix the errors below."))
            return self.get(self.request, *args, **kwargs)
        form.save()
        messages.success(self.request, _("The Vimeo URLs were updated."))
        return super().get(self.request, *args, **kwargs)


def check_api_access(request):
    if "pretalx_vimeo" not in request.event.plugin_list:
        raise Http404()
    if not (
        request.user.has_perm("schedule.list_schedule", request.event)
        or request.user.has_perm("submission.orga_list_submission")
    ):
        raise Http404()


def api_list(request, event):
    check_api_access(request)
    return JsonResponse(
        {
            "results": [
                link.serialize()
                for link in VimeoLink.objects.filter(submission__event=request.event)
            ]
        }
    )


def api_single(request, event, code):
    check_api_access(request)
    submission = request.event.submissions.filter(code__iexact=code).first()
    if not submission:
        raise Http404()
    link = getattr(submission, "vimeo_link", None)
    return JsonResponse(link.serialize() if link else {})
