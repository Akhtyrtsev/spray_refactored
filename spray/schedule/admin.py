from datetime import datetime as dt

from django import forms
from django.contrib import admin

from spray.schedule.models import ValetScheduleDay, ValetScheduleOccupiedTime, ValetScheduleAdditionalTime, \
    ValetForSchedule
from spray.utils.parse_schedule import format_time


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class WorkingDayForm(forms.ModelForm):
    class Meta:
        model = ValetScheduleDay
        fields = "__all__"

    def save(self, commit=True):
        instance = super(WorkingDayForm, self).save(commit=False)
        working_hours = ''
        break_hours = ''
        try:
            start_working_hours = self.cleaned_data['start_working_hours']
            format_start_working_hours = format_time(date=dt.strptime(f'{start_working_hours}', '%H:%M:%S'))
            end_working_hours = self.cleaned_data['end_working_hours']
            format_end_working_hours = format_time(date=dt.strptime(f'{end_working_hours}', '%H:%M:%S'))
            start_break_hours = self.cleaned_data['start_break_hours']
            format_start_break_hours = format_time(date=dt.strptime(f'{start_break_hours}', '%H:%M:%S'))
            end_break_hours = self.cleaned_data['end_break_hours']
            format_end_break_hours = format_time(date=dt.strptime(f'{end_break_hours}', '%H:%M:%S'))
            working_hours = {
                "data": [{
                    "start": f'{format_start_working_hours}',
                    "to": f'{format_end_working_hours}'}]
            }
            break_hours = {
                "data": [{
                    "start": f'{format_start_break_hours}',
                    "to": f'{format_end_break_hours}'}]
            }
        except Exception:
            pass
        instance.working_hours = working_hours
        instance.break_hours = break_hours
        if commit:
            instance.save()
        return instance


class AdditionalTimeForm(forms.ModelForm):
    class Meta:
        model = ValetScheduleAdditionalTime
        fields = "__all__"

    def save(self, commit=True):
        instance = super(AdditionalTimeForm, self).save(commit=False)
        additional_hours = ''
        try:
            start_time = self.cleaned_data['start_time']
            format_start_time = format_time(date=dt.strptime(f'{start_time}', '%H:%M:%S'))
            end_time = self.cleaned_data['end_time']
            format_end_time = format_time(date=dt.strptime(f'{end_time}', '%H:%M:%S'))
            additional_hours = {
                "data": [{
                    "start": f'{format_start_time}',
                    "to": f'{format_end_time}'}]
            }
        except Exception:
            pass
        instance.additional_hours = additional_hours
        if commit:
            instance.save()
        return instance


class OccupiedTimeForm(forms.ModelForm):
    class Meta:
        model = ValetScheduleOccupiedTime
        fields = "__all__"

    def save(self, commit=True):
        instance = super(OccupiedTimeForm, self).save(commit=False)
        break_hours = ''
        try:
            start_time = self.cleaned_data['start_time']
            format_start_time = format_time(date=dt.strptime(f'{start_time}', '%H:%M:%S'))
            end_time = self.cleaned_data['end_time']
            format_end_time = format_time(date=dt.strptime(f'{end_time}', '%H:%M:%S'))
            break_hours = {
                "data": [{
                    "start": f'{format_start_time}',
                    "to": f'{format_end_time}'}]
            }
        except Exception:
            pass
        instance.break_hours = break_hours
        if commit:
            instance.save()
        return instance


class WorkingDaysInline(admin.TabularInline):
    model = ValetScheduleDay
    exclude = ('break_hours', 'working_hours',)
    form = WorkingDayForm


class ValetScheduleAdditionalTimeInline(admin.TabularInline):
    model = ValetScheduleAdditionalTime
    exclude = ('additional_hours',)
    form = AdditionalTimeForm


class ValetScheduleOccupiedTimeInline(admin.TabularInline):
    model = ValetScheduleOccupiedTime
    exclude = ('break_hours',)
    form = OccupiedTimeForm


@admin.register(ValetForSchedule)
class ValetScheduleTimeAdmin(admin.ModelAdmin):
    fields = ('email', 'city', 'is_confirmed',)
    inlines = [
        WorkingDaysInline,
        ValetScheduleAdditionalTimeInline,
        ValetScheduleOccupiedTimeInline
    ]
