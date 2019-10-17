from django.db import models

from encrypted_model_fields.fields import EncryptedCharField

from users.models import User


class Credentials(models.Model):
    class Meta:
        verbose_name_plural = "Credentials"
        verbose_name = "Credentials"

    name = models.CharField(max_length=100, blank=False, unique=True)

    def __str__(self):
        return self.name


class CredentialsFieldsMixin(models.Model):
    class Meta:
        abstract = True

    username = models.CharField(verbose_name="Username",
                                max_length=50, blank=True)
    password = EncryptedCharField(verbose_name="Password",
                                max_length=50, blank=True)
    domain = models.CharField(verbose_name="Domain",
                              max_length=50, blank=True)

    private_key = models.TextField(verbose_name="Private Key", blank=True)
    passphrase = models.CharField(verbose_name="Passphrase", blank=True,
                                  max_length=32)

    # save password on init,
    # so we know how to revert on saving provided blank password
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cred_password_original = self.password

        # check if provided password is blank. If it is, save old password

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = self.cred_password_original

        super().save(*args, **kwargs)


class StaticCredentials(Credentials, CredentialsFieldsMixin):
    class Meta:
        verbose_name_plural = "Static credentials"
        verbose_name = "Static credentials"


class NamedCredentials(Credentials):
    class Meta:
        verbose_name_plural = "Named Credentials"
        verbose_name = "Named Credentials"

    default_domain = models.CharField(verbose_name="Default domain",
                                      max_length=50, blank=True)

    def save(self, *args, **kwargs):
        # if the first character is not '@' add '@' as the first character
        if self.name[0] != '@':
            self.name = '@' + self.name

        super(NamedCredentials, self).save(*args, **kwargs)


class PersonalNamedCredentials(CredentialsFieldsMixin):
    class Meta:
        verbose_name_plural = "Personal Named Credentials"
        verbose_name = "Personal Named Credentials"

    reference = models.ForeignKey(NamedCredentials,
                                  on_delete=models.PROTECT,
                                  # do not let reference
                                  # to be deleted if it has credentials
                                  blank=False,
                                  related_name="instances")

    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              blank=False,
                              null=True,
                              related_name="+")

    def save(self, *args, **kwargs):
        if self.domain == "":
            self.domain = self.reference.default_domain;
        super(PersonalNamedCredentials, self).save(*args, **kwargs);

    def __str__(self):
        return self.reference.__str__() + " => " + (
            self.owner.__str__() if self.owner is not None else "") + ""
