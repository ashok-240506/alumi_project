from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Job, JobComment, JobLike
from .forms import JobForm, JobCommentForm

# ------------------ JOB CRUD ------------------

class JobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    ordering = ['-posted_at'] 
    def get_queryset(self):
        qs = super().get_queryset()
        for job in qs:
            job.is_liked = JobLike.objects.filter(job=job, user=self.request.user).exists()
        return qs
class JobDetailView(LoginRequiredMixin, DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = JobCommentForm()
        context['has_liked'] = self.object.likes.filter(id=self.request.user.id).exists()
        context["comments"] = JobComment.objects.filter(job=self.object).order_by("-commented_at")


        return context

class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('job_list') 
    def form_valid(self, form):
        print(form.errors)
        form.instance.posted_by = self.request.user
        return super().form_valid(form)

class JobUpdateView(LoginRequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'

class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('job_list')

# ------------------ JOB COMMENTS ------------------

from django.http import JsonResponse

class JobCommentCreateView(LoginRequiredMixin, CreateView):
    model = JobComment
    form_class = JobCommentForm

    def form_valid(self, form):
        job = get_object_or_404(Job, pk=self.kwargs["pk"])
        form.instance.user = self.request.user
        form.instance.job = job
        self.object = form.save()

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "user": self.object.user.userdetails.first.get_full_name(),
                "text": self.object.text,
                "commented_at": self.object.commented_at.strftime("%Y-%m-%d %H:%M"),
            })

        return redirect(job.get_absolute_url())

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": form.errors}, status=400)
        return super().form_invalid(form)

    def get_success_url(self):
        return self.object.job.get_absolute_url()

# ------------------ JOB LIKE ------------------

@login_required
def job_like(request, pk):
    job = get_object_or_404(Job, pk=pk)
    user = request.user

    like_obj, created = JobLike.objects.get_or_create(job=job, user=user)

    if not created:
        # Already liked → Unlike
        like_obj.delete()
        liked = False
    else:
        # New like
        liked = True

    return JsonResponse({
        "liked": liked,
        "count": JobLike.objects.filter(job=job).count()
    })



def job_stats(request, pk):
    job = Job.objects.get(pk=pk)
    return JsonResponse({
        "likes": job.likes.count(),
        "comments": job.comments.count()
    })
