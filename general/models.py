from __future__ import unicode_literals
import uuid
# DJANGO
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from . import utils
# PROJECT

from app.fields import UUIDField
from app.utils import validate_get_phone, random_with_N_digits


class File(models.Model):
    """
    Used to store files on S3 at the moment
    Based on the architecture suggested at https://devcenter.heroku.com/articles/s3-upload-python
    Helps to generate secure URLs to upload/obtain files
    """
    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250)
    type = models.CharField(max_length=250, help_text="The MIME type of the file")
    url = models.TextField(null=True, blank=True)
    bucket = models.CharField(max_length=250, null=True, blank=True)

    def __unicode__(self):
        return self.file_name

    @classmethod
    def get_obj(cls, unique_id):
        try:
            obj = cls.objects.get(uuid=unique_id)
        except ObjectDoesNotExist:
            raise ValueError('No File found')
        return obj

    @staticmethod
    def store_public_file(bucket, file_name):
        file = File.objects.create()
        file.name = file_name
        file.bucket = bucket
        file.save()
        if bucket == 'event':
            S3_BUCKET = 'cmn-event-thumbnail'
        elif bucket == 'story':
            S3_BUCKET = 'cmn-story-thumbnail'
        else:
            file.delete()
            raise ValueError('No bucket found')
        access_control = 'public-read';
        AWSAccessKeyId = 'AKIAJVMG2OZHAAZP44AA';
        AWSSecretKey = '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';
        url = 'https://%s.s3.amazonaws.com/%s?AWSAccessKeyId=%s' % (S3_BUCKET, file.uuid, AWSAccessKeyId)

        file.set_url()
        data = {
            'access_control': access_control,
            'signed_request': url,
            'name': file.name,
            'uuid': file.uuid,
            'url': file.url
        }
        return data

    def set_url(self):
        url = 'https://s3.ap-south-1.amazonaws.com/%s/%s'
        if self.bucket == 'event':
            url = url % ('cmn-event-thumbnail', self.uuid)
        elif self.bucket == 'story':
            url = url % ('cmn-story-thumbnail', self.uuid)
        else:
            return

        self.url = url
        self.save()

    @staticmethod
    def get_url(bucket, uuid):
        url = 'https://s3.ap-south-1.amazonaws.com/%s/%s'
        if bucket == 'event':
            url = url % ('cmn-event-thumbnail', uuid)
        elif bucket == 'story':
            url = url % ('cmn-story-thumbnail', uuid)
        else:
            return None
        return url


class Phone(models.Model):
    number = models.CharField(max_length=250)
    code = models.CharField(max_length=250)
    otp = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    class Meta:
        unique_together = (('number', 'code'),)

    @staticmethod
    def create(phone, send_otp=False):
        phone_data = validate_get_phone(phone)
        try:
            obj = Phone.objects.get(number=phone_data['phone_number'], code=phone_data['phone_code'])
        except ObjectDoesNotExist:

            obj = Phone.objects.create(number=phone_data['phone_number'],
                                   code=phone_data['phone_code'], otp=random_with_N_digits(4))
        if send_otp:
            utils.msg91_phone_otp_verification(phone=obj.number, OTP=obj.otp)
        return obj


class Tag(models.Model):
    code = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)


class Category(models.Model):
    code = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    def __str__(self):
        return self.name + ' (' + self.code + ')'

    @classmethod
    def get_categories(cls):
        categories = cls.objects.all().order_by('name')
        data = {'categories': categories, 'count': categories.count()}
        return data


class City(models.Model):
    code = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    def __str__(self):
        return self.name + ' (' + self.code + ')'

    @classmethod
    def get_cities(cls):
        cities = cls.objects.all().order_by('name')
        data = {'cities': cities, 'count': cities.count()}
        return data


class ContactQuery(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=500)
    subject = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    resolved = models.NullBooleanField(blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.subject + ': from ' + self.name + '(' + self.email + ')'

    @classmethod
    def create(cls, email, name, subject, message):
        obj = cls.objects.create(email=email, name=name, subject=subject, message=message)
        return obj


class NewsletterSubscriber(models.Model):
    email = models.EmailField(max_length=500)
    subscribed = models.NullBooleanField(blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.email

    @classmethod
    def create(cls, email):
        valid_email = email.lower()
        try:
            obj = cls.objects.get(email=valid_email)
        except ObjectDoesNotExist:
            obj = cls.objects.create(email=valid_email)
        return obj