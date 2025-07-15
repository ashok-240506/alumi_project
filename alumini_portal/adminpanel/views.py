import pandas as pd
from django.shortcuts import render, redirect
from django.views import View
from .forms import UploadExcelForm
from users.models import CustomUser, UserPersonalProfile
from .models import Department, Batch
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Department, Batch
from .forms import DepartmentForm, BatchForm
class UploadStudentView(View):
    def get(self, request):
        return render(request, 'adminpanel/upload.html', {'form': UploadExcelForm()})

    def post(self, request):
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            df = pd.read_excel(request.FILES['excel_file'])

            for _, row in df.iterrows():
                mobile = str(row['mobilenumber']).strip()
                roll_no = str(row['roll_no']).strip()
                reg_no = str(row['reg_no']).strip()
                dept_name = row['department'].strip()
                start_year = int(row['year'])  # or adjust this as per your logic
                department, _ = Department.objects.get_or_create(name=dept_name)
                end_year = start_year + 4
                batch, _ = Batch.objects.get_or_create(
                    department=department,
                    start_year=start_year,
                    end_year=end_year
                )


                # Create or update user
                user, created = CustomUser.objects.get_or_create(
                    mobilenumber=mobile,
                    defaults={
                        'roll_no': roll_no,
                        'reg_no': reg_no,
                        'is_alumini': False,
                    }
                )

                if not created:
                    # Update roll/reg number if needed
                    user.roll_no = roll_no
                    user.reg_no = reg_no
                    user.save()

                # Create or update user profile
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

            return redirect('upload-students')

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

class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'adminpanel/department_form.html'
    success_url = reverse_lazy('department-list')

class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'adminpanel/department_confirm_delete.html'
    success_url = reverse_lazy('department-list')


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

class BatchUpdateView(UpdateView):
    model = Batch
    form_class = BatchForm
    template_name = 'adminpanel/batch_form.html'
    success_url = reverse_lazy('batch-list')

class BatchDeleteView(DeleteView):
    model = Batch
    template_name = 'adminpanel/batch_confirm_delete.html'
    success_url = reverse_lazy('batch-list')
