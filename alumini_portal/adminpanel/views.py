import pandas as pd
from django.shortcuts import render, redirect
from django.views import View
from .forms import UploadExcelForm
from users.models import CustomUser, UserPersonalProfile
from .models import Department, Batch

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
