from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from urllib.parse import urlparse
import hashlib

from .services.turso_client import run_turso_query

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def categorize_job(title):
    categories_map = {
        'გაყიდვები': ['გაყიდვები', 'ბიზნესი', 'მენეჯერი', 'კონსულტანტი'],
        'UI/UX დიზაინი': ['ui', 'ux', 'დიზაინერი', '3d'],
        'პროგრამირება': ['python', 'დეველოპერი', '.net', 'java'],
        'არქიტექტურა': ['არქიტექტორი']
    }
    text = (title or "").lower()
    for category, keywords in categories_map.items():
        if any(keyword.lower() in text for keyword in keywords):
            return category
    return "სხვა"

def job_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('auth_view')

    user_interest_rows = run_turso_query(
        "SELECT i.name FROM interest i JOIN user_interest ui ON ui.interest_id = i.id WHERE ui.user_id = ?",
        [user_id]
    )
    user_interests = [row[0] for row in user_interest_rows]

    hr_jobs = run_turso_query("SELECT * FROM hr_ge")
    jobs_ge = run_turso_query("SELECT * FROM jobs_ge")
    myjobs_ge = run_turso_query("SELECT * FROM myjobs_ge")

    all_jobs = hr_jobs + jobs_ge + myjobs_ge

    filtered_jobs = []
    for job in all_jobs:
        title = job.get('position', '') or job.get('title', '')
        category = categorize_job(title)
        if category in user_interests:
            filtered_jobs.append(job)

    context = {
        'jobs': filtered_jobs,
    }
    return render(request, 'core/index.html', context)

def auth_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'register':
            email = request.POST.get('email')
            name = request.POST.get('name')
            password = request.POST.get('password1')

            existing = run_turso_query("SELECT id FROM user WHERE email = ?", [email])
            if existing:
                messages.error(request, "Email уже зарегистрирован")
                return redirect('auth_view')

            password_hash = hash_password(password)
            run_turso_query(
                "INSERT INTO user (email, name, password_hash, is_active) VALUES (?, ?, ?, ?)",
                [email, name, password_hash, 0]
            )
            user_row = run_turso_query("SELECT id FROM user WHERE email = ?", [email])
            user_id = user_row[0][0]
            request.session['user_id'] = user_id
            send_verification_email(request, user_id, email, name)
            messages.success(request, "Проверьте почту для подтверждения аккаунта")
            return redirect('auth_view')

        elif form_type == 'login':
            email = request.POST.get('email')
            password = request.POST.get('password')
            password_hash = hash_password(password)
            user_row = run_turso_query(
                "SELECT id, is_active FROM user WHERE email = ? AND password_hash = ?",
                [email, password_hash]
            )
            if not user_row:
                messages.error(request, "Неверные учетные данные")
                return redirect('auth_view')
            user_id, is_active = user_row[0]
            if not is_active:
                messages.error(request, "Аккаунт не активирован")
                return redirect('auth_view')
            request.session['user_id'] = user_id
            return redirect('job_list')

    return render(request, 'core/auth.html')

def send_verification_email(request, user_id, email, name):
    token = default_token_generator.make_token(user_id)
    uid = urlsafe_base64_encode(force_bytes(user_id))
    domain = get_current_site(request).domain
    link = reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
    activate_url = f'http://{domain}{link}'
    message = render_to_string('core/verify_email.html', {
        'name': name,
        'activate_url': activate_url,
    })
    send_mail(
        'Активация аккаунта',
        message,
        None,
        [email],
        fail_silently=False,
    )

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
    except:
        uid = None
    if not uid:
        return render(request, 'core/verify_failed.html')
    user_row = run_turso_query("SELECT id FROM user WHERE id = ?", [uid])
    if not user_row:
        return render(request, 'core/verify_failed.html')
    if default_token_generator.check_token(uid, token):
        run_turso_query("UPDATE user SET is_active = 1 WHERE id = ?", [uid])
        request.session['user_id'] = int(uid)
        return redirect('job_list')
    return render(request, 'core/verify_failed.html')

def interests_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('auth_view')

    if request.method == 'POST':
        selected = request.POST.getlist('interests')
        if len(selected) == 3:
            run_turso_query("DELETE FROM user_interest WHERE user_id = ?", [user_id])
            for interest_id in selected:
                run_turso_query(
                    "INSERT INTO user_interest (user_id, interest_id) VALUES (?, ?)",
                    [user_id, interest_id]
                )
            return redirect('job_list')
        else:
            messages.error(request, "Выберите ровно 3 интереса")

    interests = run_turso_query("SELECT id, name FROM interest")
    return render(request, 'core/interests.html', {'interests': interests})

def logout_view(request):
    request.session.flush()
    return redirect('auth_view')
