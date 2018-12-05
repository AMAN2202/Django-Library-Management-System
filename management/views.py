from django.shortcuts import render, redirect

from .models import *
from .forms import *
# .FORMS REFERS TO THE FORMS.PY IN CURRENT DIRECTORY AND * USED FOR IMPORTING EVERYTHING

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import datetime

# HOME PAGE
def index(request):
    return render(
        request,
        'index.html',
    )


# VIEW THAT WILL RETURN LIST OF ALL BOOKS IN LIBRARY
def BookListView(request):
    book_list = Book.objects.all()
    # MODELNAME.objects.all() is used to get all objects i.e. tuples from database
    return render(request, 'catalog/book_list.html', locals())

@login_required
def student_BookListView(request):
    student=Student.objects.get(roll_no=request.user)
    bor=Borrower.objects.filter(student=student)
    book_list=[]
    for b in bor:
        book_list.append(b.book)
    # MODELNAME.objects.all() is used to get all objects i.e. tuples from database
    return render(request, 'catalog/book_list.html', locals())

#This view return detail of a particular book
#it also accepts a parameter pk that is the id  i.e. primary_key of book to identify it
#get_object_404 if object is not found then return 404 server error
#locals return a dictionary of loacl varibles
def BookDetailView(request, pk):
    book = get_object_or_404(Book, id=pk)
    reviews=Reviews.objects.filter(book=book).exclude(review="none")
    try:
        stu = Student.objects.get(roll_no=request.user)
        rr=Reviews.objects.get(review="none")
    except:
        pass
    return render(request, 'catalog/book_detail.html', locals())



@login_required
def BookCreate(request):
    if not request.user.is_superuser:
        return redirect('index')
    form = BookForm()
    if request.method == 'POST':
        form = BookForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect(index)
    return render(request, 'catalog/form.html', locals())


@login_required
def BookUpdate(request, pk):
    if not request.user.is_superuser:
        return redirect('index')
    obj = Book.objects.get(id=pk)
    form = BookForm(instance=obj)
    if request.method == 'POST':
        form = BookForm(data=request.POST, files=request.FILES, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return redirect(index)
    return render(request, 'catalog/form.html', locals())


@login_required
def BookDelete(request, pk):
    if not request.user.is_superuser:
        return redirect('index')
    obj = get_object_or_404(Book, pk=pk)
    obj.delete()
    return redirect('index')



@login_required
def student_request_issue(request, pk):
    obj = Book.objects.get(id=pk)
    stu=Student.objects.get(roll_no=request.user)
    s = get_object_or_404(Student, roll_no=str(request.user))
    if s.total_books_due < 10:
        message = "book has been isuued, You can collect book from library"
        a = Borrower()
        a.student = s
        a.book = obj
        a.issue_date = datetime.datetime.now()
        obj.available_copies = obj.available_copies - 1
        obj.save()
        stu.total_books_due=stu.total_books_due+1
        stu.save()
        a.save()
    else:
        message = "you have exceeded limit."
    return render(request, 'catalog/result.html', locals())


@login_required
def StudentCreate(request):
    if not request.user.is_superuser:
        return redirect('index')
    form = StudentForm()
    if request.method == 'POST':
        form = StudentForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            s=form.cleaned_data['roll_no']
            form.save()
            u=User.objects.get(username=s)
            s=Student.objects.get(roll_no=s)
            u.email=s.email
            u.save()
            return redirect(index)
    return render(request, 'catalog/form.html', locals())


@login_required
def StudentUpdate(request, pk):
    if not request.user.is_superuser:
        return redirect('index')
    obj = Student.objects.get(id=pk)
    form = StudentForm(instance=obj)
    if request.method == 'POST':
        form = StudentForm(data=request.POST, files=request.FILES, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return redirect(index)
    return render(request, 'catalog/form.html', locals())


@login_required
def StudentDelete(request, pk):
    obj = get_object_or_404(Student, pk=pk)
    obj.delete()
    return redirect('index')

@login_required
def StudentList(request):
    students = Student.objects.all()
    return render(request, 'catalog/student_list.html', locals())

@login_required
def StudentDetail(request, pk):
    student = get_object_or_404(Student, id=pk)
    books=Borrower.objects.filter(student=student)
    return render(request, 'catalog/student_detail.html', locals())




@login_required
def ret(request, pk):
    if not request.user.is_superuser:
        return redirect('index')
    obj = Borrower.objects.get(id=pk)
    book_pk=obj.book.id
    student_pk=obj.student.id
    student = Student.objects.get(id=student_pk)
    student.total_books_due=student.total_books_due-1
    student.save()

    book=Book.objects.get(id=book_pk)
    rating = Reviews(review="none", book=book,student=student,rating='2.5')
    rating.save()
    book.available_copies=book.available_copies+1
    book.save()
    obj.delete()
    return redirect('index')


import re

from django.db.models import Q

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query
def search_book(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string, ['title', 'summary','author'])

        book_list= Book.objects.filter(entry_query)

    return render(request,'catalog/book_list.html',locals() )
def search_student(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string, ['roll_no','name','email'])

        students= Student.objects.filter(entry_query)

    return render(request,'catalog/student_list.html',locals())




@login_required
def RatingUpdate(request, pk):
    obj =Reviews.objects.get(id=pk)
    form = RatingForm(instance=obj)
    if request.method == 'POST':
        form = RatingForm(data=request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return redirect('book-detail',pk=obj.book.id)
    return render(request, 'catalog/form.html', locals())


@login_required
def RatingDelete(request, pk):
    obj = get_object_or_404(Reviews, pk=pk)
    st=Student.objects.get(roll_no=request.user)
    if not st==obj.student:
        return redirect('index')
    pk = obj.book.id
    obj.delete()
    return redirect('book_detail',pk)
