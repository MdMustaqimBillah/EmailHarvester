from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User
from .models import ScrapingHistory
from .serializers import UserSerializer, ScrapingHistorySerializer, URLInputSerializer
from .forms import UserRegistrationForm, UserLoginForm
import requests
import re
from bs4 import BeautifulSoup

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('App:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return JsonResponse({'token': token.key})
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('App:home')

@login_required
def dashboard(request):
    history = ScrapingHistory.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'history': history})

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def scrape_url(request):
    serializer = URLInputSerializer(data=request.data)
    if serializer.is_valid():
        url = serializer.validated_data['url']
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, soup.get_text())
            
            # Save scraping history
            history = ScrapingHistory.objects.create(
                user=request.user,
                url=url,
                email_count=len(emails)
            )
            
            return Response({
                'url': url,
                'emails': emails,
                'count': len(emails)
            })
        except requests.RequestException:
            return Response({'error': 'Failed to fetch the URL'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ScrapingHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScrapingHistorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return ScrapingHistory.objects.filter(user=self.request.user)