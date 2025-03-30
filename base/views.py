from django.shortcuts import render, redirect
import requests
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import UserSerializer
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login,logout, get_user_model
from django.db import IntegrityError
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import UserSubscription 
from django.urls import reverse
from .models import Advertisement
from .serializers import AdvertisementSerializer

API_KEY = '8d165c24e1c84969a0502b91e3977f3b'

# Create your views here.
@login_required(login_url='login')  # ✅ Redirects to login page if not logged in
def home(request):
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}'
    
    response = requests.get(url)
    data = response.json()

    # Ensure 'articles' exists in the API response before passing it to the template
    articles = data.get("articles", [])  
    ads = Advertisement.objects.all()
    return render(request, "base/home.html", {
    "articles": articles,
    "ads": ads
})


def category(request,category):

    url = f'https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    articles = data['articles']
    ads = Advertisement.objects.all()
    context = {
        'category' : category.capitalize,
        'articles' : articles,
        "ads": ads,

    }
    
    return render(request,'base/category.html',context)

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")  # ✅ Redirect to home page after login
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "base/login.html")

CustomUser = get_user_model()  # ✅ Get the custom user model dynamically

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, "base/register.html")

        # Check if username exists
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, "base/register.html")

        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered")
            return render(request, "base/register.html")

        try:
            # Create and save the user
            user = CustomUser.objects.create_user(username=username, email=email, password=password1)
            user.save()

            # Log the user in
            login(request, user)
            messages.success(request, "Registration successful!")

            return redirect("/")  # Redirect to home page after signup

        except IntegrityError:  # Catch any unexpected integrity errors
            messages.error(request, "An error occurred. Please try again.")
            return render(request, "base/register.html")

    return render(request, "base/register.html")

def logout_view(request):
    logout(request)
    return redirect("login")  # ✅ Redirect to login page after logout


def subscribe_user(user):
    """Helper function to subscribe a user"""
    subscription, created = Subscription.objects.get_or_create(user=user)
    if not subscription.is_subscribed:
        subscription.is_subscribed = True
        subscription.save()
        return True
    return False  # Already subscribed

@login_required
def unsubscribe(request):
    if request.method == "POST":
        try:
            subscription = UserSubscription.objects.get(user=request.user)
            subscription.is_subscribed = False
            subscription.save()
            messages.success(request, "You have successfully unsubscribed.")
        except UserSubscription.DoesNotExist:
            messages.error(request, "You are not subscribed.")
    
    return redirect("home")  # Redirect back to home after unsubscribing

@login_required
def subscription_page(request):
    return render(request, 'base/payment.html')

@login_required
def process_payment(request):
    if request.method == "POST":
        # Assume the payment is successful
        subscription, created = UserSubscription.objects.get_or_create(user=request.user)
        subscription.is_subscribed = True
        subscription.save()

        messages.success(request, "Successfully Subscribed!")
        return redirect(reverse("subscription_success"))  # ✅ Use reverse to resolve URL name

    return redirect(reverse("subscription_page"))  # ✅ Use reverse here too

@login_required
def subscription_success(request):
    return render(request, "base/subscription_success.html")

@api_view(['GET'])
def advertisement_list(request):
    ads = Advertisement.objects.all()
    serializer = AdvertisementSerializer(ads, many=True)
    return Response(serializer.data)

def music_recommendations(request):
    # Replace this with your real API URL or local data
    response = requests.get("https://te26gj7kmc.execute-api.eu-west-1.amazonaws.com/Music_application")
    songs = response.json()
    return render(request, "base/music.html", {"songs": songs})

