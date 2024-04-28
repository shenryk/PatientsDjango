from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template import Context
from .models import Patient, Doctor, Nurse, Hospital, Appointment
from .forms import BaseUserForm, UserForm, ProfileForm, MedicalForm, AppointmentForm
from django.views.decorators.csrf import csrf_exempt
import datetime, itertools, csv

"""
The views are essentially the intermediary step between the logic of the models and
database and the front facing html pages. These are what is being called in the urls.py
page. The format of each is fairly simple: At a minimum, the method needs to take a request,
however, as seen in the methods dealing with the patient, optional additional parameters can
be passed in through the urls.py page.
There are two types of request; GET and POST. Get is when the user is pulling the page and
Post is when they have entered some information and are submitting it to our side. When
dealing with a page that requires the user to input information, the general flow is to first
check what method the request is, displaying the blank forms if it is get, or pulling in the data
and using it somehow.
These @csrf_exempt lines above each view is a workaround solution for csrf missing token
errors. The error has something to do with a csrf tag not being placed properly in the
html files.
"""

#array that is used during patient registration in drop down selector
STATE_CHOICES = (
    ('AL', 'Alabama'),
    ('AK', 'Alaska'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DE', 'Delaware'),
    ('DC', 'District of Columbia'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('IA', 'Iowa'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('ME', 'Maine'),
    ('MD', 'Maryland'),
    ('MA', 'Massachusetts'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MS', 'Mississippi'),
    ('MO', 'Missouri'),
    ('MT', 'Montana'),
    ('NE', 'Nebraska'),
    ('NV', 'Nevada'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NY', 'New York'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('WA', 'Washington'),
    ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming'),
)

diseaseChecks = [
    'Allergies',
    'Anemia',
    'Arthritis',
    'Chickenpox',
    'Coxsackie',
    'Diphtheria',
    'Epilepsy',
    'Frequent Colds',
    'German Measles',
    'High Blood Pressure',
    'Influenza',
    'Kidney Disease',
    'Measles',
    'Migraines',
    'Mumps',
    'Obesity',
    'Pneumonia',
    'Polio',
    'Rheumatic Fever',
    'Scarlatina',
    'Scarlet Fever',
    'Strokes',
    'Syphilis',
    'Tonsillitis',
    'Tuberculosis',
    'Whooping Cough'
]


@csrf_exempt
def updateUser(request, username):
    if not request.user.is_authenticated():
        return redirect('/login/')

    requestedPatient = Patient.objects.get(user=User.objects.get(username=username))
    print(requestedPatient)

    return HttpResponseRedirect('/%s/profile' % request.user.username, {'patient': requestedPatient})


@csrf_exempt
def export(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    else:
        patient = Patient.objects.get(user=request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="MedicalInformation.csv"'

    writer = csv.writer(response)
    writer.writerow(['User Info:', 'Usename', patient.user.username, 'Policy Number', patient.userInfo.policyNumber, 'Provider', patient.userInfo.provider, 'Group Number', patient.userInfo.groupNumber])
    writer.writerow(['Profile Info:', 'Firstname', patient.profileInfo.firstName, 'Middlename', patient.profileInfo.middleName, 'LastName', patient.profileInfo.lastName, 'Address', patient.profileInfo.address, 'City', patient.profileInfo.city, 'State', patient.profileInfo.state, 'Date of Birth', patient.profileInfo.dateOfBirth, 'Zipcode', patient.profileInfo.zipcode, 'Phone Number', patient.profileInfo.phoneNumber, 'Email', patient.profileInfo.email, 'Emergency contact', patient.profileInfo.eName, 'Emergency Phone', patient.profileInfo.ePhoneNumber ])
    writer.writerow(['Medical Info:', 'Allergies', patient.medicalInfo.allergies, 'Anemia', patient.medicalInfo.anemia, 'Arthritis', patient.medicalInfo.arthritis, 'Chickenpox', patient.medicalInfo.chickenpox, 'Coxsackie', patient.medicalInfo.coxsackie, 'Diphtheria', patient.medicalInfo.diphtheria, 'Epilepsy', patient.medicalInfo.epilepsy, 'Frequent Colds', patient.medicalInfo.frequentColds, 'German Measeles', patient.medicalInfo.germanMeasles, 'High Blood Pressure', patient.medicalInfo.highBloodPressure, 'Influenza', patient.medicalInfo.influenza, 'Kidney Disease', patient.medicalInfo.kidneyDisease, 'Measles', patient.medicalInfo.measles, 'Migraines', patient.medicalInfo.migraines, 'Mumps', patient.medicalInfo.mumps, 'Obesity', patient.medicalInfo.obesity, 'Pneumonia', patient.medicalInfo.pneumonia, 'Polio', patient.medicalInfo.polio, 'Rheumatic Fever', patient.medicalInfo.rheumaticFever, 'Scarlatina', patient.medicalInfo.scarlatina, 'Scarlet Fever', patient.medicalInfo.scarletFever, 'Strokes', patient.medicalInfo.strokes, 'Syphilis', patient.medicalInfo.syphilis, 'Tonsillitis', patient.medicalInfo.tonsillitis, 'Tuberculosis', patient.medicalInfo.tuberculosis, 'Whooping Cough', patient.medicalInfo.whoopingCough, 'Other', patient.medicalInfo.otherText])

    return response


@csrf_exempt
def createApp(request):
    if not request.user.is_authenticated():
        return redirect('/login/')

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            cleanData = form.cleaned_data
            apt = Appointment(
				doctor=cleanData['doctor'],
				userName = request.user.username,
				date=cleanData['date'] + "T" + cleanData['time'],
				description=cleanData['description']
			)
            apt.save()

    return HttpResponseRedirect('/%s/profile/' % request.user.username)


@csrf_exempt
def deleteApp(request, id):
    if not request.user.is_authenticated():
        return redirect('/login/')

    Appointment.objects.filter(pk=id).delete()

    return HttpResponseRedirect('/%s/profile' % request.user.username)


def editApp(request, id):
    if not request.user.is_authenticated():
        return redirect('/login/')

    apt = Appointment.objects.filter(pk=id)
    apt.description = "newdesc"
    apt.save()

    return HttpResponseRedirect('/%s/profile' % request.user.username)


@csrf_exempt
def userLogin(request):
    auth = 3
    if request.method == 'POST':
        #This is how data can be pulled from a post request. The 'username' and 'password' are assigned names for
        #the fields in the html page.
        username = request.POST.get('username')
        password = request.POST.get('password')
        #authenticate returns true or false based on whether the username and password match in the database
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                auth = 0
                if user.is_staff:
                    return HttpResponseRedirect('/%s/staffProfile' % username)
                else:
                    return HttpResponseRedirect('/%s/profile' % username)
            else:
                auth = 1
                #all users have a is_valid field that can be toggled for expiration or transfers etc.
                return render(request, 'login.html', {'authenticated': auth , 'username' : username, 'password' : password})
        else:
            auth = 2
            return render(request, 'login.html', {'authenticated': auth , 'username' : username, 'password' : password})
    else:
        return render(request, "login.html", {'authenticated':auth})


@csrf_exempt
def userLogout(request):
    logout(request)
    return HttpResponseRedirect('/')


@csrf_exempt
def register(request):
    registered = False

    if request.method == 'POST':
        #this is where all of the data the user input is gathered.
        baseUserForm = BaseUserForm(data=request.POST)

        userForm = UserForm(data=request.POST)
        profileForm = ProfileForm(data=request.POST)
        medicalForm = MedicalForm(data=request.POST)

        #The forms are checked to determine if they are valid. This is where required fields are checked.
        if  userForm.is_valid() and profileForm.is_valid() and medicalForm.is_valid():

            #creating the user object
            user = baseUserForm.save()
            user.set_password(user.password)

            #all adjusted values must be followed by a save call.
            user.save()

            patientUserInfo = userForm.save()
            patientProfileInfo = profileForm.save()
            patientMedicalInfo = medicalForm.save()

            patient = Patient(user=user, userInfo = patientUserInfo, profileInfo=patientProfileInfo, medicalInfo=patientMedicalInfo)

            patient.user.save()
            patient.userInfo.save()
            patient.profileInfo.save()
            patient.medicalInfo.save()

            patient.save()

            patient.hospital = Hospital.objects.get(name=request.POST['hospital'])
            userDoctor = User.objects.get(username=request.POST['doctor'])
            patient.doctor = Doctor.objects.get(user=userDoctor)
            patient.save()

            patient.user.first_name = patient.profileInfo.firstName
            patient.user.last_name = patient.profileInfo.lastName
            patient.user.email = patient.profileInfo.email
            patient.user.save()

            registered = True
            userLogin(request)
            return HttpResponseRedirect('/%s/profile' % patient.user.username)
        else:
            #TODO - these errors should be added into the registration.html so the user can see it
            print(baseUserForm.errors, userForm.errors, profileForm.errors, medicalForm.errors)

            baseUserForm = BaseUserForm(data=request.POST.copy())
            userForm = UserForm(data=request.POST.copy())
            profileForm = ProfileForm(data=request.POST.copy())
            medicalForm = MedicalForm(data=request.POST.copy())
            return render(request, 'registration.html', {'baseUserForm':baseUserForm, 'userForm':userForm, 'profileForm':profileForm, 'medicalForm':medicalForm, 'registered': registered, 'doctorlist' : Doctor.objects.all(), 'hospitallist': Hospital.objects.all(), 'states' : STATE_CHOICES, 'diseases' : diseaseChecks})

    else:
        #if the request is get, show blank forms.
        baseUserForm = BaseUserForm()
        userForm = UserForm()
        profileForm = ProfileForm()
        medicalForm = MedicalForm()
    return render(request, 'registration.html', {'baseUserForm':baseUserForm, 'userForm':userForm, 'profileForm':profileForm, 'medicalForm':medicalForm, 'registered': registered, 'doctorlist' : Doctor.objects.all(), 'hospitallist': Hospital.objects.all(), 'states' : STATE_CHOICES, 'diseases' : diseaseChecks})


@csrf_exempt
def profile(request, username):
    #check that the user is actually logged in so they can't access someone's profile just
    #by knowing the url. If they aren't authenticated they get redirected to the login page
    #using the reverse lookup which searches the urls in urls.py for a name of 'login'
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    else:
        #capture the user object and run checks on the account type to determine where to send them
        #In the future we may need to check for doctors and nurses and send them elsewhere.
        activeUser = Patient.objects.get(user=request.user)
        checklist = activeUser.medicalInfo._meta.get_fields()
        newchecklist = []
        for check in checklist:
            newchecklist.append(getattr(activeUser.medicalInfo, check.name))

        iterator = itertools.count()

    user = request.user
    appointments = Appointment.objects.filter(userName = user.username)

    return render(request, 'ProfilePage.html', {'user' : activeUser, 'checklist' : checklist, 'newchecklist' : newchecklist, 'iterator':iterator, 'appointments': appointments, 'appform': AppointmentForm,  'doctorlist' : Doctor.objects.all(), 'hospitallist': Hospital.objects.all()})


@csrf_exempt
def staffProfile(request, username):
    #check that the user is actually logged in so they can't access someone's profile just
    #by knowing the url. If they aren't authenticated they get redirected to the login page
    #using the reverse lookup which searches the urls in urls.py for a name of 'login'
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    else:
        #capture the user object and run checks on the account type to determine where to send them
        #In the future we may need to check for doctors and nurses and send them elsewhere.
        accountType = "Doctor"
        try:
            activeUser = Doctor.objects.get(user=request.user)
        except:
            try:
                activeUser = Nurse.objects.get(user=request.user)
            except:
                activeUser = None
        if activeUser:
            try:
                patients = Patient.objects.filter(doctor=Doctor.objects.get(user=request.user))
            except:
                accountType = "Nurse"
                try:
                    patients = Patient.objects.filter(hospital= Hospital.objects.get(name=activeUser.hospital))
                except:
                    patients = None

    return render(request, 'StaffProfile.html', {'user' : activeUser, 'accountType' : accountType, 'patients' : patients})


@csrf_exempt
def profileEdit(request):
    registered = False

    if request.method == 'POST':
        #this is where all of the data the user input is gathered.
        userForm = UserForm(data=request.POST)
        profileForm = ProfileForm(data=request.POST)

        #The forms are checked to determine if they are valid. This is where required fields are checked.
        if userForm.is_valid() and profileForm.is_valid():
            print("valid")
            patientUserInfo = userForm.save()
            patientProfileInfo = profileForm.save()

            patient = Patient.objects.get(user=User.objects.get(username=request.user.username))

            patient.userInfo = patientUserInfo
            patient.profileInfo = patientProfileInfo

            patient.userInfo.save()
            patient.profileInfo.save()
            patient.save()

            patient.user.first_name = patient.profileInfo.firstName
            patient.user.last_name = patient.profileInfo.lastName
            patient.user.email = patient.profileInfo.email
            patient.user.save()

            registered = True
            return HttpResponseRedirect('/%s/profile' % patient.user.username)
    else:
        #if the request is get, show blank forms.
        userForm = UserForm()
        profileForm = ProfileForm()

    return HttpResponseRedirect('/%s/profile' % request.user.username, {'userForm':userForm, 'profileForm':profileForm, 'doctorlist' : Doctor.objects.all(), 'hospitallist': Hospital.objects.all()})


@csrf_exempt
def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


@csrf_exempt
def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response