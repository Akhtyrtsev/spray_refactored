from datetime import datetime, date

from django import forms
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.forms.models import BaseInlineFormSet
from django_json_widget.widgets import JSONEditorWidget

from spray.utils.parse_schedule import parse_schedule, closest_to_now

from spray.schedule.models import ValetScheduleDay

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #
admin.site.register(ValetScheduleDay)


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

class WorkingDayForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorkingDayForm, self).__init__(*args, **kwargs)
        working_time = self.instance.working_hours
        if working_time:
            time = parse_schedule(working_time)
            if time:
                time = time[0]
                self.initial['start_working_hours'] = time[0]
                self.initial['end_working_hours'] = time[1]
                if time[1] == datetime(1900, 1, 1, 23, 59).time():
                    self.initial['end_working_hours'] = datetime(1900, 1, 1, 0, 0).time()
            else:
                self.initial['start_working_hours'] = None
                self.initial['end_working_hours'] = None
        break_time = self.instance.break_hours
        if break_time:
            time = parse_schedule(break_time)
            if time:
                time = time[0]
                self.initial['start_break_hours'] = time[0]
                self.initial['end_break_hours'] = time[1]
                if time[1] == datetime(1900, 1, 1, 23, 59).time():
                    self.initial['end_break_hours'] = datetime(1900, 1, 1, 0, 0).time()
            else:
                self.initial['start_break_hours'] = None
                self.initial['end_break_hours'] = None


class WorkingDaysInlineFormSet(BaseInlineFormSet):
    def save_new_objects(self, commit=True):
        saved_instances = super(WorkingDaysInlineFormSet, self).save_new_objects(commit)
        for instance in saved_instances:
            base = date(1900, 1, 1)
            start = instance.start_working_hours
            end = instance.end_working_hours

            if start and end:
                start = datetime.combine(base, start)
                end = datetime.combine(base, end)
                start = closest_to_now(start)
                end = closest_to_now(end)
                working_hours = {'data': [{'start': start, 'to': end}]}
                instance.working_hours = working_hours
            else:
                working_hours = {'data': [{'start': None, 'to': None}]}
                instance.working_hours = working_hours

            start = instance.start_break_hours
            end = instance.end_break_hours

            if start and end:
                start = datetime.combine(base, start)
                end = datetime.combine(base, end)
                start = closest_to_now(start)
                end = closest_to_now(end)
                break_hours = {'data': [{'start': start, 'to': end}]}
                instance.break_hours = break_hours
            else:
                break_hours = {'data': [{'start': None, 'to': None}]}
                instance.break_hours = break_hours
            instance.save()
        return saved_instances

    def save_existing_objects(self, commit=True):
        saved_instances = super(WorkingDaysInlineFormSet, self).save_existing_objects(commit)
        for instance in saved_instances:
            base = date(1900, 1, 1)
            start = instance.start_working_hours
            end = instance.end_working_hours
            if start and end:
                start = datetime.combine(base, start)
                end = datetime.combine(base, end)
                start = closest_to_now(start)
                end = closest_to_now(end)
                working_hours = {'data': [{'start': start, 'to': end}]}
                instance.working_hours = working_hours
            else:
                working_hours = {'data': [{'start': None, 'to': None}]}
                instance.working_hours = working_hours
            start = instance.start_break_hours
            end = instance.end_break_hours
            if start and end:
                start = datetime.combine(base, start)
                end = datetime.combine(base, end)
                start = closest_to_now(start)
                end = closest_to_now(end)
                break_hours = {'data': [{'start': start, 'to': end}]}
                instance.break_hours = break_hours
            else:
                break_hours = {'data': [{'start': None, 'to': None}]}
                instance.break_hours = break_hours
            instance.save()
            print(instance.working_hours)
        return saved_instances


class WorkingDaysInline(admin.TabularInline):  # CantDeleteMixin, CantAddMixin
    model = ValetScheduleDay
    form = WorkingDayForm
    formset = WorkingDaysInlineFormSet
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    exclude = ('break_hours', 'working_hours')

