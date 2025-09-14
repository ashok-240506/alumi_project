from django.http import JsonResponse
import pandas as pd
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from .forms import RoleForm, UploadExcelForm
from users.models import CustomUser, RoleMapping, RoleMaster, UserPersonalProfile
from .models import Department, Batch
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Department, Batch
from .forms import DepartmentForm, BatchForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from users.models import RoleMaster
from django.views.generic import TemplateView

@login_required
def admin_home(request):
    return render(request, 'adminpanel/adminhome.html')
class SettingsView(TemplateView):
    template_name = 'adminpanel/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = RoleMaster.objects.all()
        return context
class RoleListView(ListView):
    model = RoleMaster
    template_name = 'adminpanel/role_list.html'
    context_object_name = 'roles'

class RoleCreateView(CreateView):
    model = RoleMaster
    form_class = RoleForm
    template_name = 'adminpanel/role_form.html'

    def form_valid(self, form):
        form.instance.modified_by = self.request.user.id 
        messages.success(self.request, "Role created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('role-list')


class RoleUpdateView(UpdateView):
    model = RoleMaster
    form_class = RoleForm
    template_name = 'adminpanel/role_form.html'

    def form_valid(self, form):
        form.instance.modified_by = self.request.user.id
        messages.success(self.request, "Role updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('role-list')


class RoleDeleteView(DeleteView):
    model = RoleMaster
    template_name = 'adminpanel/role_confirm_delete.html'
    success_url = reverse_lazy('role-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Role deleted successfully.")
        return super().delete(request, *args, **kwargs)

class UploadStudentView(View):
    def get(self, request):
        return render(request, 'adminpanel/upload.html', {'form': UploadExcelForm()})

    def post(self, request):
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = pd.read_excel(request.FILES['excel_file'])

                for _, row in df.iterrows():
                    mobile = str(row['mobilenumber']).strip()
                    roll_no = str(row['roll_no']).strip()
                    reg_no = str(row['reg_no']).strip()
                    dept_name = row['department'].strip()
                    start_year = int(row['year'])  
                    department, _ = Department.objects.get_or_create(name=dept_name)
                    end_year = start_year + 4
                    batch, _ = Batch.objects.get_or_create(
                        department=department,
                        start_year=start_year,
                        end_year=end_year
                    )
                    user, created = CustomUser.objects.get_or_create(
                        mobilenumber=mobile,
                        defaults={
                            'roll_no': roll_no,
                            'reg_no': reg_no,
                            'is_alumini': False,
                        }
                    )

                    if not created:
                        user.roll_no = roll_no
                        user.reg_no = reg_no
                        user.save()

                    UserPersonalProfile.objects.update_or_create(
                        user=user,
                        defaults={
                            'firstname': row.get('firstname', ''),
                            'lastname': row.get('lastname', ''),
                            'major': row.get('major', ''),
                            'batch': batch,
                            'college_name': row.get('college_name', ''),
                            'university_name': row.get('university_name', '')
                        }
                    )

                    role, _ = RoleMaster.objects.get_or_create(role_name='Student')
                    RoleMapping.objects.get_or_create(user=user, role=role)

                messages.success(request, "Student data uploaded successfully.")
                return redirect('upload-students')  

            except Exception as e:
                messages.error(request, f"Upload failed: {e}")
        else:
            messages.error(request, "Invalid form. Please check your file.")

        return render(request, 'adminpanel/upload.html', {'form': form})


# DEPARTMENT CRUD

class DepartmentListView(ListView):
    model = Department
    template_name = 'adminpanel/department_list.html'
    context_object_name = 'departments'

class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'adminpanel/department_form.html'
    success_url = reverse_lazy('department-list')
    def form_valid(self, form):
        messages.success(self.request, "Department created successfully.")
        return super().form_valid(form)
class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'adminpanel/department_form.html'
    success_url = reverse_lazy('department-list')
    def form_valid(self, form):
        messages.success(self.request, "Department updated successfully.")
        return super().form_valid(form)


class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'adminpanel/department_confirm_delete.html'
    success_url = reverse_lazy('department-list')
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Department deleted successfully.")
        return super().delete(request, *args, **kwargs)

# BATCH CRUD

class BatchListView(ListView):
    model = Batch
    template_name = 'adminpanel/batch_list.html'
    context_object_name = 'batches'

    def get_queryset(self):
        queryset = super().get_queryset()
        department_id = self.request.GET.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['selected_dept'] = self.request.GET.get('department')
        return context

class BatchCreateView(CreateView):
    model = Batch
    form_class = BatchForm
    template_name = 'adminpanel/batch_form.html'
    success_url = reverse_lazy('batch-list')
    def form_valid(self, form):
        messages.success(self.request, "Batch created successfully.")
        return super().form_valid(form)

class BatchUpdateView(UpdateView):
    model = Batch
    form_class = BatchForm
    template_name = 'adminpanel/batch_form.html'
    success_url = reverse_lazy('batch-list')
    def form_valid(self, form):
        messages.success(self.request, "Batch updated successfully.")
        return super().form_valid(form)

class BatchDeleteView(DeleteView):
    model = Batch
    template_name = 'adminpanel/batch_confirm_delete.html'
    success_url = reverse_lazy('batch-list')
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Batch deleted successfully.")
        return super().delete(request, *args, **kwargs)
    



def user_analytics(request):
    students_count = CustomUser.objects.filter(is_alumini=False).count()
    alumni_count = CustomUser.objects.filter(is_alumini=True).count()

    data = {
        "students": students_count,
        "alumni": alumni_count,
    }
    return JsonResponse(data)

def user_analytics_page(request):
    return render(request, "adminpanel/user_analytics.html")


def batch_detail(request, batch_id):
    # Get batch
    batch = get_object_or_404(Batch, id=batch_id)
    
    students = UserPersonalProfile.objects.filter(batch=batch, is_active=True)
    
    return render(request, "adminpanel/batch_detail.html", {
        "batch": batch,
        "students": students
    })


def batch_list(request):
    batches = Batch.objects.all().order_by('start_year')
    
    program_filter = request.GET.getlist('program')
    year_filter = request.GET.getlist('year')
    sort_order = request.GET.get('sort', 'asc')
    search_term = request.GET.get('search', '')
    year_filter = request.GET.getlist('year','')  # or however you get the filter
    if year_filter =='':
        year_filter =None
    if year_filter and year_filter[0]:
        start, end = map(int, year_filter[0].split('-'))
        batches = batches.filter(start_year__gte=start, end_year__lte=end)

    else :
        pass
    if program_filter:
        batches = batches.filter(department__name__icontains=program_filter[0])  # or a program_type field

    if search_term:
        batches = batches.filter(name__icontains=search_term)

    if sort_order == 'desc':
        batches = batches.order_by('-name')

    return render(request, "adminpanel/batch_all_details.html", {"batches": batches})
