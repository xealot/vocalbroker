from django.db import models

class Caller(models.Model):
    """
    A caller is uniquely identified by the number they
    dial in with or that they enter into the keypad.
    """
    number = models.CharField(unique=True, max_length=50, help_text='The normalized number the user uses to call in.')
    name_recording = models.URLField(verify_exists=False, null=True, blank=True, help_text='The recording of the users name.')
    name_transcription = models.CharField(max_length=200, null=True, blank=True, help_text='The transcription of the user\'s name.')
    name_transcription_url = models.URLField(verify_exists=False, null=True, blank=True, help_text='The URL resource of the transcription.')


class Call(models.Model):
    """
    A Call is sort of like a session. The only difference
    is that they are not reusable.
    """
    caller = models.ForeignKey(Caller)
    call_sid = models.CharField(max_length=75, unique=True)
    account_sid = models.CharField(max_length=75)
    call_from = models.CharField(max_length=75, null=True, blank=True)
    call_to = models.CharField(max_length=75)
    status = models.CharField(max_length=25, choices=[(i, i) for i in ('queued', 'ringing', 'in-progress', 'completed', 'busy', 'failed', 'no-answer')])
    direction = models.CharField(max_length=25, choices=[(i, i) for i in ('inbound', 'outbound-dial')])
    forwarded = models.CharField(max_length=75, null=True, blank=True)
    caller_name = models.CharField(max_length=100, null=True, blank=True)

    from_city = models.CharField(max_length=75, null=True, blank=True, help_text="The city of the caller.")
    from_state = models.CharField(max_length=75, null=True, blank=True, help_text="The state or province of the caller.")
    from_zip = models.CharField(max_length=75, null=True, blank=True, help_text="The postal code of the caller.")
    from_country = models.CharField(max_length=75, null=True, blank=True, help_text="The country of the caller.")
    to_city = models.CharField(max_length=75, null=True, blank=True, help_text="The city of the called party.")
    to_state = models.CharField(max_length=75, null=True, blank=True, help_text="The state or province of the called party.")
    to_zip = models.CharField(max_length=75, null=True, blank=True, help_text="The postal code of the called party.")
    to_country = models.CharField(max_length=75, null=True, blank=True, help_text="The country of the called party.")

    duration = models.IntegerField(default=0)

    session_data = models.TextField()