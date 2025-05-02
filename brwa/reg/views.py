from .models import *
from .forms import *
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login ,logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.core.paginator import Paginator


def home(request):
    query = request.GET.get('q')
    sort = request.GET.get('s')
    books = Book.objects.annotate(avg_rating=Avg('review__rating'))  # Add average ratings
    
    if query:
        books = books.filter(title__icontains=query) | books.filter(author__icontains=query)
    elif sort:  # Only filter by genre if 'sort' is provided
        books = books.filter(genre__icontains=sort)
    else:
        pass
    
    paginator = Paginator(books, 4)  # Show 4 books per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    genres = Book.objects.values_list('genre', flat=True).distinct()
    con = {
        'page_obj': page_obj,
        'content': page_obj,
        'books': books,
        'genres': genres,
    }
    return render(request, 'home.html', con)


    # content = Book.objects.annotate(avg_rating=Avg('review__rating'))
    # return render(request,'home.html',{'content':content})

# login 
def log_in(request):
    if request.method=='POST':
        form=AuthenticationForm(request,data=request.POST)

        # if the user is valid it will redirect to home page

        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('home')
    else:
        form=AuthenticationForm()
    return render(request,'login.html',{'form':form})

# logout
def log_out(request):
    logout(request)
    return redirect('home')

# registration
def register(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()  # this saves to auth_user table
            return redirect('login')
    else:
        form=UserCreationForm()
    return render(request,'register.html',{'form':form})

#MUST LOGIN TO WRITE REVIEW
@login_required

#book review , avg ratings ,recommendations

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = Review.objects.filter(book=book)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    recommendations = Book.objects.filter(genre=book.genre).exclude(pk=book.pk).order_by('?')[:3]

    if request.user.is_authenticated:
        existing_review = Review.objects.filter(book=book, user=request.user).first()
        if request.method == 'POST' and not existing_review:
            form = ReviewForm(request.POST)
            if form.is_valid():
                new_review = form.save(commit=False)
                new_review.book = book
                new_review.user = request.user
                new_review.save()

                return redirect('book_detail', pk=book.pk)
        else:
            form = ReviewForm()
    else:
        form = None
        existing_review = None
    context={
        'book': book, 'reviews': reviews, 'avg_rating': avg_rating,'form': form, 
        'existing_review': existing_review, 'recommendations': recommendations
    }
    return render(request, 'book_review.html', context)

# for profile 

def profile_view(request):
    reviews = Review.objects.filter(user=request.user)
    return render(request, 'profile.html', {'reviews': reviews})