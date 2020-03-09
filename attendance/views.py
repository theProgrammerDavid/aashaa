from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .forms import UserRegistrationForm, LostKidRegistrationForm, VerifyForm, KidRegistrationForm
from .models import Parent, LostKid, VerifyRequest, Kid
from django.contrib.auth.decorators import login_required
import face_recognition
from django.core.mail import EmailMultiAlternatives
import mimetypes
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone


def verify_requests_redo(image_q):
    verify_requests = VerifyRequest.objects.all()
    image = face_recognition.load_image_file(image_q.photo)
    unknown_encoding = face_recognition.face_encodings(image)
    if unknown_encoding:
        unknown_encoding = unknown_encoding[0]
        for i in verify_requests:
            image_known = face_recognition.load_image_file(i.photo)
            biden_encoding = face_recognition.face_encodings(image_known)[0]
            results = face_recognition.compare_faces([biden_encoding], unknown_encoding, tolerance=0.51)
            print(results)
            if results[0]:
                image_q.found = True
                image_q.found_location = i.location
                image_q.save()
                message = EmailMultiAlternatives("Congratulations !! Your kid {} is found".format(image_q.name),
                                                 "Your kid {} was found at the location {}".format(image_q.name,
                                                                                                   image_q.found_location),
                                                 "admin@ohuru.tech",
                                                 [image_q.email],
                                                 )
                message.attach(i.photo.name, i.photo.open().read(), mimetypes.guess_type(i.photo.name)[0])
                message.send()
                i.delete()
                break


# Create your views here.
def index(request):
    context = {
        'page': 'home'
    }
    return render(request,
                  template_name='attendance/index.html',
                  context=context)


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_parent = user_form.save(commit=False)
            new_parent.set_password(user_form.cleaned_data['password'])
            new_parent.save()
            parent = Parent()
            parent.user = new_parent
            parent.phone_number = user_form.cleaned_data['phone_number']
            parent.save()
            return render(request, 'attendance/register_done.html')

    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'attendance/register.html',
                  {'user_form': user_form,
                   'page': 'signup'})


@login_required
def dashboard(request):
    return render(request, 'attendance/dashboard.html', context={
        'name': request.user.first_name,
        'page': dashboard,
    })


def register_lost_kids(request):
    if request.method == 'POST':
        lost_kids_form = LostKidRegistrationForm(request.POST, request.FILES)
        if lost_kids_form.is_valid():
            instance = lost_kids_form.save(commit=True)
            verify_requests_redo(instance)
            return render(request, 'attendance/submitted.html')
    else:
        lost_kids_form = LostKidRegistrationForm()
    return render(request, 'attendance/registered_lost.html', context={
        'form': lost_kids_form,
        'page': 'lost_kid'
    })


def verify(request):
    if request.method == 'POST':
        found = False
        name = None
        verify_form = VerifyForm(request.POST, request.FILES)
        if verify_form.is_valid():
            vf = verify_form.save(commit=True)
            lost_kids = LostKid.objects.filter(found=False)
            image = face_recognition.load_image_file(verify_form.cleaned_data['photo'])
            file = vf.photo.read()
            name = verify_form.cleaned_data['photo'].name
            format_file = verify_form.cleaned_data['photo'].content_type
            unknown_encoding = face_recognition.face_encodings(image)
            if unknown_encoding:
                unknown_encoding = unknown_encoding[0]
                for i in lost_kids:
                    image_known = face_recognition.load_image_file(i.photo)
                    biden_encoding = face_recognition.face_encodings(image_known)[0]
                    results = face_recognition.compare_faces([biden_encoding], unknown_encoding, tolerance=0.51)
                    if results[0]:
                        print(results[0])
                        print(i.name)
                        i.found = True
                        i.found_location = verify_form.cleaned_data['location']
                        i.save()
                        message = EmailMultiAlternatives("Congratulations !! Your kid {} is found".format(i.name),
                                                         "Your kid {} was found at the location {}".format(i.name,
                                                                                                           i.found_location),
                                                         "admin@ohuru.tech",
                                                         [i.email],
                                                         )
                        message.attach(name, file, format_file)
                        message.send()
                        found = True
                        vf.delete()
                        name = i.name
                        contact = i.email + ' ' + i.phone_number
                        break
            if found:
                return render(request, 'attendance/thanks.html', context={
                    'found_name': name,
                    'contact': contact
                })
            else:
                print("here")
                lost_kids = LostKid.objects.filter(found=True)
                not_save = False
                for i in lost_kids:
                    image_known = face_recognition.load_image_file(i.photo)
                    biden_encoding = face_recognition.face_encodings(image_known)[0]
                    results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
                    if results[0]:
                        not_save = True
                        pass
                if not not_save:
                    print("committing changes")
                    verify_form.save(commit=True)
                return render(request, 'attendance/thanks.html')
        else:
            print(verify_form.errors)
            return HttpResponse(verify_form.errors)
    else:
        verify_form = VerifyForm()
        return render(request, 'attendance/verify.html', context={
            'verify_form': verify_form,
            'page': 'verify',
        })


@login_required
def register_kid_biometric(request):
    if request.method == 'POST':
        kid_form = KidRegistrationForm(request.POST, request.FILES)
        if kid_form.is_valid():
            kd = kid_form.save(commit=False)
            kd.parent = get_object_or_404(Parent, user=request.user)
            kd.save()
            return render(request, 'attendance/register_kid_done.html', context={
                'name': kd.name,
            })
    else:
        kid_form = KidRegistrationForm()
    return render(request, 'attendance/register_child.html', context={
        'form': kid_form,
    })


def view_kids(request):
    state = None
    if request.GET.get('state') and request.GET.get('state') != 'All':
        lost_kids = LostKid.objects.filter(found=False).filter(state=request.GET.get('state')).order_by('-id')
        state = request.GET.get('state')
    elif request.GET.get('state') and request.GET.get('state') == 'All':
        lost_kids = LostKid.objects.filter(found=False).order_by('-id')
        state = request.GET.get('state')
    else:
        lost_kids = LostKid.objects.filter(found=False).order_by('-id')
        state = 'All'
    paginator = Paginator(lost_kids, 4)
    page = request.GET.get('pge')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'attendance/show_kids.html', context={
        'kids': posts,
        'pge': page,
        'general': True,
        'placeholder': state,
    })


@login_required
def view_registered_biometric(request):
    parent = get_object_or_404(Parent, user=request.user)
    kids = Kid.objects.filter(parent=parent)
    for i in kids:
        if i.lost_instance:
            if i.lost_instance.found:
                i.lost = False
                i.lost_instance.delete()
                i.lost_instance = None
                i.save()
    return render(request, 'attendance/kids_biometric.html', context={
        'kids': kids,
        'page': 'all_biometric',
    })


@login_required
def make_lost(request):
    if request.method == 'POST':
        if request.POST.get('checkbox') == 'on':
            child_id = request.POST.get('id')
            child = get_object_or_404(Kid, id=child_id)
            child.lost = True
            lost = LostKid()
            lost.email = request.user.email
            lost.name = child.name
            lost.state = child.state
            lost.photo = child.photo_id
            lost.date = timezone.now()
            lost.description = child.description
            lost.phone_number = child.parent.phone_number
            lost.save()
            child.lost_instance = lost
            child.save()
            verify_requests_redo(lost)
            return redirect(to='attendance:all_biometric')
        else:
            child_id = request.POST.get('id')
            child = get_object_or_404(Kid, id=child_id)
            child.lost = False
            child.lost_instance.delete()
            child.lost_instance = None
            child.save()
            return redirect(to='attendance:all_biometric')
    else:
        return redirect(to='attendance:all_biometric')
