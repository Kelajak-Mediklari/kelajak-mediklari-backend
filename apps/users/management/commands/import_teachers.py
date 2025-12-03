import os
from datetime import timedelta

import openpyxl
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.course.models import Course, UserCourse
from apps.users.models import User, KMTeacher, TeacherGlobalLimit


class Command(BaseCommand):
    help = "Import teachers from teacher-base.xlsx file"

    def handle(self, *args, **options):
        # Get the Excel file path
        excel_file_path = 'teacher-base.xlsx'

        if not os.path.exists(excel_file_path):
            self.stdout.write(self.style.ERROR(f"Excel file not found at {excel_file_path}"))
            return

        # Load workbook
        workbook = openpyxl.load_workbook(excel_file_path)
        sheet = workbook.active

        # Get header row to find column indices
        headers = [cell.value for cell in sheet[1]]

        # Find column indices
        try:
            full_name_idx = headers.index('Ism-familya')
            phone_idx = headers.index('Telefonraqam')
            km_id_idx = headers.index('KM ID')
            is_repetitor_idx = headers.index('Repititorligi haqida')
            kitob1_idx = headers.index('1-kitob')
            kitob2_idx = headers.index('2-kitob')
            oziga_idx = headers.index("O'ziga")
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Required column not found: {e}"))
            return

        # Get 'teacher' group
        try:
            teacher_group = Group.objects.get(name='teacher')
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR("'teacher' group not found. Please create it first."))
            return

        # Get courses
        try:
            course_1 = Course.objects.get(id=9)
            course_2 = Course.objects.get(id=7)
        except Course.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Course not found: {e}"))
            return

        # Process each row
        success_count = 0
        error_count = 0

        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=False), start=2):
            try:
                # Get cell values
                full_name = row[full_name_idx].value if row[full_name_idx].value else None
                phone_raw = row[phone_idx].value if row[phone_idx].value else None
                km_id = row[km_id_idx].value if row[km_id_idx].value else None
                is_repetitor_raw = row[is_repetitor_idx].value if row[is_repetitor_idx].value else None
                kitob1_value = row[kitob1_idx].value if row[kitob1_idx].value else None
                kitob2_value = row[kitob2_idx].value if row[kitob2_idx].value else None
                oziga_value = row[oziga_idx].value if row[oziga_idx].value else None

                # Skip empty rows
                if not full_name or not phone_raw or not km_id:
                    continue

                # Convert km_id to string and strip
                km_id = str(km_id).strip() if km_id else None
                if not km_id:
                    continue

                # Format phone number
                phone_str = str(phone_raw).strip()
                # Remove any non-digit characters except +
                phone_clean = ''.join(c for c in phone_str if c.isdigit() or c == '+')

                # If doesn't start with +998, add it
                if not phone_clean.startswith('+998'):
                    # Remove leading + if exists
                    phone_clean = phone_clean.lstrip('+')
                    # Remove leading 998 if exists
                    if phone_clean.startswith('998'):
                        phone_clean = phone_clean[3:]
                    phone_clean = '+998' + phone_clean

                formatted_phone = phone_clean

                # Generate password
                # Format: KM_ID + first letter of first name + first letter of last name + last two digits of phone
                name_parts = full_name.strip().split()
                if len(name_parts) < 2:
                    self.stdout.write(self.style.WARNING(
                        f"Row {row_idx}: Full name should have at least first and last name: {full_name}"))
                    error_count += 1
                    continue

                first_name = name_parts[0]
                last_name = name_parts[-1]

                # Get first letter of first name and last name
                first_letter_first = first_name[0].upper() if first_name else ''
                first_letter_last = last_name[0].upper() if last_name else ''

                # Get last two digits of phone (remove +998 and get last 2 digits)
                phone_digits = phone_clean.replace('+998', '')
                last_two_digits = phone_digits[-2:] if len(phone_digits) >= 2 else phone_digits

                password = f"{km_id}{first_letter_first}{first_letter_last}{last_two_digits}"

                # Check if user already exists
                if User.objects.filter(phone=formatted_phone).exists():
                    user = User.objects.get(phone=formatted_phone)
                    self.stdout.write(self.style.WARNING(
                        f"Row {row_idx}: User with phone {formatted_phone} already exists, updating related objects..."))
                    # Ensure user is in teacher group
                    if not user.groups.filter(name='teacher').exists():
                        user.groups.add(teacher_group)
                else:
                    # Create User
                    user = User.objects.create_user(
                        phone=formatted_phone,
                        password=password,
                        full_name=full_name.strip(),
                        role=User.Role.TEACHER,
                        is_staff=True,  # Override default is_staff=False
                    )
                    # Generate username
                    user.username = User.generate_username(full_name)
                    user.save(update_fields=['username'])

                    # Add to teacher group
                    user.groups.add(teacher_group)

                    self.stdout.write(
                        self.style.SUCCESS(f"Row {row_idx}: Created user {user.full_name} ({formatted_phone})"))

                # Create KMTeacher
                km_teacher, created = KMTeacher.objects.get_or_create(
                    km_id=km_id,
                    defaults={
                        'user': user,
                        'is_repetitor': bool(is_repetitor_raw) if is_repetitor_raw else False,
                    }
                )

                if not created:
                    # Update existing KMTeacher
                    km_teacher.user = user
                    km_teacher.is_repetitor = bool(is_repetitor_raw) if is_repetitor_raw else False
                    km_teacher.save(update_fields=['user', 'is_repetitor'])

                self.stdout.write(self.style.SUCCESS(f"Row {row_idx}: Created/Updated KMTeacher {km_teacher.km_id}"))

                # Create TeacherGlobalLimit for course 1
                limit_1 = int(kitob1_value) if kitob1_value and str(kitob1_value).strip() else 0
                teacher_limit_1, created = TeacherGlobalLimit.objects.get_or_create(
                    teacher=user,
                    course=course_1,
                    defaults={
                        'limit': limit_1,
                        'remaining': limit_1,
                    }
                )
                if not created:
                    teacher_limit_1.limit = limit_1
                    teacher_limit_1.remaining = limit_1 - teacher_limit_1.used
                    teacher_limit_1.save(update_fields=['limit', 'remaining'])

                self.stdout.write(
                    self.style.SUCCESS(f"Row {row_idx}: Created/Updated TeacherGlobalLimit for course 1: {limit_1}"))

                # Create TeacherGlobalLimit for course 2
                limit_2 = int(kitob2_value) if kitob2_value and str(kitob2_value).strip() else 0
                teacher_limit_2, created = TeacherGlobalLimit.objects.get_or_create(
                    teacher=user,
                    course=course_2,
                    defaults={
                        'limit': limit_2,
                        'remaining': limit_2,
                    }
                )
                if not created:
                    teacher_limit_2.limit = limit_2
                    teacher_limit_2.remaining = limit_2 - teacher_limit_2.used
                    teacher_limit_2.save(update_fields=['limit', 'remaining'])

                self.stdout.write(
                    self.style.SUCCESS(f"Row {row_idx}: Created/Updated TeacherGlobalLimit for course 2: {limit_2}"))

                # Calculate finish_date for courses
                start_date = timezone.now()
                finish_date_1 = None
                finish_date_2 = None

                if course_1.duration_months:
                    finish_date_1 = start_date + timedelta(days=course_1.duration_months * 30)

                if course_2.duration_months:
                    finish_date_2 = start_date + timedelta(days=course_2.duration_months * 30)

                # Create UserCourse for course 1 (for all teachers)
                user_course_1, created = UserCourse.objects.get_or_create(
                    user=user,
                    course=course_1,
                    defaults={
                        'finish_date': finish_date_1,
                    }
                )
                if not created and finish_date_1:
                    user_course_1.finish_date = finish_date_1
                    user_course_1.save(update_fields=['finish_date'])

                self.stdout.write(self.style.SUCCESS(f"Row {row_idx}: Created/Updated UserCourse for course 1"))

                # Create UserCourse for course 2 if O'ziga = 1
                if oziga_value and (str(oziga_value).strip() == '1' or oziga_value == 1):
                    user_course_2, created = UserCourse.objects.get_or_create(
                        user=user,
                        course=course_2,
                        defaults={
                            'finish_date': finish_date_2,
                        }
                    )
                    if not created and finish_date_2:
                        user_course_2.finish_date = finish_date_2
                        user_course_2.save(update_fields=['finish_date'])

                    self.stdout.write(
                        self.style.SUCCESS(f"Row {row_idx}: Created/Updated UserCourse for course 2 (O'ziga=1)"))

                success_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Row {row_idx}: Error processing row: {e}"))
                error_count += 1
                continue

        self.stdout.write(self.style.SUCCESS(f"\nImport completed!"))
        self.stdout.write(self.style.SUCCESS(f"Successfully processed: {success_count} teachers"))
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f"Errors encountered: {error_count} rows"))
