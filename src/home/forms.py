from django.core.exceptions import ValidationError
from django.db.models import Q
from django import forms
from .models import Booking
from datetime import timedelta
import datetime


"""
This form is used for booking the hall for an event by registered users and the request will be sent to the admin only
if the timing slot is available for booking.
"""
class BookingForm(forms.ModelForm):
	# This connects the 'Booking' model with this form and shows the specified fields on the html.
	class Meta:
		model = Booking 
		exclude = ['status', 'email']

	"""
	If the input date is not valid then it will show a validation message.
	The form will also raise a validation error if the start time or the end time of the event is between the timings 
	for	already booked or hall to be booked. e.g. If the hall is booked from 8AM to 10AM, then the user can't book 
	the hall from 9AM to 10AM.
	"""
	def clean(self):
		try:	
			form_data = self.cleaned_data
			event_date = form_data['date']
			event_hall = form_data['hall']
			event_start = form_data['start_time']
			event_end = form_data['end_time']

			# Getting the current date and time for comparing
			time_now = datetime.datetime.now().strftime('%H:%M:00')
			date_today = datetime.date.today()

			# FMP = '%H:%M %p'
			# duration = datetime.datetime.strptime(event_end, FMP) - datetime.datetime.strptime(event_start, FMP)
			# event_end = (event_start + timedelta(hours = event_hours)).strftime('%H:%M %p')

			
			# For checking if the start_time is less than end_time, valid timings
			if (event_start >= event_end):
				raise forms.ValidationError("Invalid Timings")

			# For checking event booking date and timings such that no past booking can be done such that for today's 
			# date and the start_time as well as end_time should be greater than current time whereas the isoformat is 
			# used for converting the time to the string and comparing the value with the form time values
			if (event_date == date_today and (event_start.isoformat() <= time_now or event_end.isoformat() <= \
				time_now)):
				raise forms.ValidationError("Please fill future timings")

			# Comparing the form_data with the values in database for checking already booked hall
			event_time = Booking.objects.filter(Q(start_time__range = (event_start, event_end)) | \
				Q(end_time__range = (event_start, event_end)) | \
				Q(start_time__lte = event_start, end_time__gte = event_end) | \
				Q(start_time__gte = event_start, end_time__lte = event_end), \
				date = event_date, hall = event_hall)

			for t in event_time:
				if t is not None:
					raise forms.ValidationError("Hall Already Booked")

			return form_data

		except KeyError:
			print ("Please fill the entries")
		# If the exception is raised for KeyError, then the statement will execute till the required entries are filled


"""
This form is used for viewing the future booking in various hall and the user can filter the bookings by selecting the
date and/or the hall such that the list of bookings will be shown.
"""
class ViewBookingsForm(forms.ModelForm):
	class Meta:
		model = Booking
		fields = ['hall', 'date']
