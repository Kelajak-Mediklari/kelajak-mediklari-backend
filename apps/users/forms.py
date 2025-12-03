from django.forms import TextInput
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib import admin

from apps.users.models import GroupMember, User


class GroupMemberInlineForm(forms.ModelForm):
    """Custom form for GroupMember inline with phone number field"""
    phone_number = forms.CharField(
        label=_('Phone Number'),
        max_length=20,
        required=False,
        widget=TextInput(attrs={'placeholder': '+998901234567', 'style': 'width: 200px;'})
    )

    class Meta:
        model = GroupMember
        fields = ('phone_number', 'is_active')
        exclude = ('user',)  # Exclude user - it will be set from phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing instance, populate phone_number
        # Safely check if user exists by checking user_id
        if self.instance and self.instance.pk and hasattr(self.instance, 'user_id') and self.instance.user_id:
            try:
                self.fields['phone_number'].initial = str(self.instance.user.phone)
            except (AttributeError, User.DoesNotExist):
                # User doesn't exist or was deleted, leave phone_number empty
                pass
            except Exception:
                # Catch any other exception (like RelatedObjectDoesNotExist) when accessing user
                pass

    def clean_phone_number(self):
        """Validate and format phone number"""
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            return None

        # Format phone number
        phone_str = str(phone_number).strip()
        phone_clean = ''.join(c for c in phone_str if c.isdigit() or c == '+')

        if not phone_clean.startswith('+998'):
            phone_clean = phone_clean.lstrip('+')
            if phone_clean.startswith('998'):
                phone_clean = phone_clean[3:]
            phone_clean = '+998' + phone_clean

        # Find user by phone
        try:
            user = User.objects.get(phone=phone_clean)
            # Store user in form for later use in clean()
            self._user = user
            return phone_clean
        except User.DoesNotExist:
            raise ValidationError(
                _("User with phone number %(phone)s does not exist.") % {'phone': phone_number}
            )

    def clean(self):
        """Validate that user is not already in another group with the same course"""
        cleaned_data = super().clean()

        # Get the user from phone_number validation
        user = getattr(self, '_user', None)
        # Safely check if user exists on existing instance
        if not user and self.instance and hasattr(self.instance, 'user_id') and self.instance.user_id:
            try:
                user = self.instance.user
            except (User.DoesNotExist, Exception):
                # User doesn't exist or related object doesn't exist, will be set from phone_number if provided
                user = None

        # If editing existing instance without user, require phone_number
        phone_number = cleaned_data.get('phone_number')
        if self.instance and self.instance.pk and not user and not phone_number:
            raise ValidationError({
                'phone_number': ValidationError(
                    _("Phone number is required. This group member does not have a user assigned.")
                )
            })

        # Get the group from the parent (inline)
        group = self.instance.group if self.instance else None

        if user and group and group.course:
            # Check if user is already in another group with the same course
            existing_member = GroupMember.objects.filter(
                user=user,
                group__course=group.course,
                is_active=True
            ).exclude(pk=self.instance.pk if self.instance.pk else None).first()

            if existing_member:
                raise ValidationError({
                    'phone_number': ValidationError(
                        _("User %(user)s is already a member of group '%(group)s' for course '%(course)s'. "
                          "A user can only be in one group per course.") % {
                            'user': user.full_name or str(user.phone),
                            'group': existing_member.group.name,
                            'course': group.course.title
                        }
                    )
                })

        return cleaned_data

    def save(self, commit=True):
        """Convert phone number to user before saving"""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            try:
                user = User.objects.get(phone=phone_number)
                self.instance.user = user
            except User.DoesNotExist:
                # If user doesn't exist, we can't save - but validation should have caught this
                pass
        elif self.instance and self.instance.pk:
            # If no phone_number provided and this is an existing instance,
            # check if it has a user - if not, we need to require phone_number
            if not (hasattr(self.instance, 'user_id') and self.instance.user_id):
                # Existing instance without user and no phone provided - validation should catch this
                pass

        return super().save(commit=commit)


class GroupMemberInline(admin.TabularInline):
    """Tabular inline for GroupMember with phone number input"""
    model = GroupMember
    form = GroupMemberInlineForm
    extra = 1
    fields = ('phone_number', 'is_active')
    verbose_name = _("Group Member")
    verbose_name_plural = _("Group Members")

    def get_queryset(self, request):
        """Filter to show only members of groups belonging to the logged-in user"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group__teacher=request.user)
