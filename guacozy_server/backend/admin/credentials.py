from django.contrib import admin
from django.forms import ModelForm, CharField, PasswordInput, HiddenInput, TextInput

from rules.contrib.admin import ObjectPermissionsModelAdmin

from backend.models import StaticCredentials, PersonalNamedCredentials, NamedCredentials


class CredentialsForm(ModelForm):
    class Meta:
        fields = '__all__'
        help_texts = {
            "passphrase": "Passphrase if private key has a passphrase",
            "domain": "Active Directory Domain name"
        }

        widgets = {
            'name': TextInput(attrs={'autocomplete': 'off', 'data-lpignore': 'true'}),
            'username': TextInput(attrs={'autocomplete': 'off', 'data-lpignore': 'true'}),
            'domain': TextInput(attrs={'autocomplete': 'off', 'data-lpignore': 'true'}),
            'password': PasswordInput(attrs={'autocomplete': 'off', 'data-lpignore': 'true'}),
            'passphrase': TextInput(attrs={'autocomplete': 'off', 'data-lpignore': 'true'}),
        }


@admin.register(StaticCredentials)
class StaticCredentialsAdmin(admin.ModelAdmin):
    form = CredentialsForm


class PersonalNamedCredentialsInline(admin.TabularInline):
    model = PersonalNamedCredentials
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    fields = ['owner']
    readonly_fields = ['owner']


@admin.register(NamedCredentials)
class NamedCredentialsAdmin(admin.ModelAdmin):
    model = NamedCredentials
    inlines = [
        PersonalNamedCredentialsInline
    ]

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            return obj.instances.count() == 0
        else:
            return False


@admin.register(PersonalNamedCredentials)
class PersonalNamedCredentialsAdmin(ObjectPermissionsModelAdmin):
    model = PersonalNamedCredentials

    form = CredentialsForm

    fieldsets = (
        (None, {
            'fields': ('reference', 'owner',)
        }),
        ('Password login', {
            'fields': ('username', 'password', 'domain')
        }),
        ('Key login', {
            'fields': ('private_key', 'passphrase')
        })
    )

    readonly_fields = ['owner']

    def save_model(self, request, obj, form, change):
        if not change:
            # the object is being created, so set the owner
            obj.owner = request.user
        obj.save()

    # It is PERSONAL credentials, so any user, even superuser
    # shoul see only his own credentials
    def get_queryset(self, request):
        return super().get_queryset(request).filter(owner=request.user)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(PersonalNamedCredentialsAdmin, self).get_form(request, obj, change, **kwargs)
        form.Meta.help_texts["domain"] = "Active Directory domain name. If left blank, domain name from Reference " \
                                         "will be used."
        return form
