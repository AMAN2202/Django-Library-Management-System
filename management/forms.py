from django import forms

from .models import *


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'


class BorrowForm(forms.ModelForm):
    class Meta:
        model = Borrower
        exclude = ['issue_date', 'return_date']


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
class RatingForm(forms.ModelForm):
    class Meta:
        model = Reviews
        exclude=['student','book']