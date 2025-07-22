import pandas as pd
from django.shortcuts import render, redirect
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