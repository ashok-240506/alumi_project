from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from django.views.decorators.http import require_POST

from notification.models import Notification
from users.models import CustomUser

from .templatetags.custom_timesince import short_timesince
from .models import Job, JobComment, JobLike
from .forms import JobForm, JobCommentForm
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied
# ------------------ JOB CRUD ------------------

class JobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    ordering = ['-posted_at'] 

    def get_queryset(self):
        qs = super().get_queryset()

        # 🔎 Get query params
        q = self.request.GET.get('q')
        location = self.request.GET.get('location')
        job_type = self.request.GET.get('type')
        # experience = self.request.GET.get('experience')

        # Apply filters
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | 
                Q(company_name__icontains=q)
            )

        if location:
            qs = qs.filter(location__icontains=location)

        if job_type:
            qs = qs.filter(job_type=job_type)

        # if experience:
        #     qs = qs.filter(experience=experience)

        # Add "is_liked" flag for each job
        for job in qs:
            job.is_liked = JobLike.objects.filter(job=job, user=self.request.user).exists()

        return qs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["details"] = self.request.user.userdetails.first()  # ✅ Pass user details
        return context
class MyJobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "jobs/my_jobs_list.html"  # ✅ separate template
    context_object_name = "jobs"  # this will be a queryset of jobs
    ordering = ["-posted_at"]

    def get_queryset(self):
        return Job.objects.filter(posted_by=self.request.user).order_by("-posted_at")

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
        form.instance.posted_by = self.request.user
        return super().form_valid(form)


class JobUpdateView(LoginRequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'

    def dispatch(self, request, *args, **kwargs):
        job = self.get_object()
        if job.posted_by != request.user:  # ✅ only creator allowed
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    def get_success_url(self):
        return reverse_lazy('my_jobs') 

class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('job_list')

    def dispatch(self, request, *args, **kwargs):
        job = self.get_object()
        if job.posted_by != request.user:  # ✅ only creator allowed
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
# ------------------ JOB COMMENTS ------------------

class JobCommentCreateView(LoginRequiredMixin, CreateView):
    model = JobComment
    form_class = JobCommentForm

    def form_valid(self, form):
        job = get_object_or_404(Job, pk=self.kwargs["pk"])
        form.instance.user = self.request.user
        form.instance.job = job
        self.object = form.save()

        # Always return JSON (no redirect)
        user_details = self.object.user.userdetails.first()
        user_name = user_details.get_full_name() if user_details else self.object.user.username

        return JsonResponse({
            "success": True,
            "user": user_name,
            "comment": self.object.comment,
            "commented_at": self.object.commented_at.strftime("%Y-%m-%d %H:%M"),
            "job_id": job.id,
        })

    def form_invalid(self, form):
        return JsonResponse({"success": False, "error": form.errors}, status=400)

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

def user_notification(request, pk):
    user = CustomUser.objects.get(id=pk, is_active=True)
    notifications = user.notifications.all().order_by('-created_at')  # latest first
    data = []
    count = {
        'all': notifications.count(),
        'read': notifications.filter(is_read=True).count(),
        'unread': notifications.filter(is_read=False).count()
    }
    for n in notifications:
        sender = n.created_by
        avatar = sender.profile_pic.url if getattr(sender, "profile_pic", None) else static("default-avatar.png")
        data.append({
            'id': n.id,
            'title': n.title,
            'sender_avatar':avatar,
            'message': n.message,
            'url': n.url,  # optional: link to details
            'created_at': n.created_at.strftime("%d/%m/%Y %I:%M %p"),
            'read': n.is_read,
            'count':count
        })
    return JsonResponse({'count':count, 'notifications': data})

def job_stats(request, pk):
    job = Job.objects.get(pk=pk)
    return JsonResponse({
        "likes": job.likes.count(),
        "comments": job.comments.count()
    })
@login_required
def job_all_comments(request, pk):
    job = Job.objects.get(pk=pk)
    comments = job.comments.all().order_by("created_at")
    data = {
        "comments": [
            {
                "user": c.posted_by.get_full_name(),
                "text": c.text,
                "timesince": short_timesince(c.posted_at),  # use your custom filter or Django timesince
            } for c in comments
        ]
    }
    return JsonResponse(data)

@require_POST
def mark_notification_read(request, pk):
    print('pk-----------------',pk)
    notif = get_object_or_404(Notification, pk=pk, recipient_id=request.user)
    print('notif----------------------------',notif)
    notif.is_read = True
    notif.save(update_fields=["is_read"])
    return JsonResponse({"success": True})