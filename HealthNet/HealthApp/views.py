from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from .models import Patient, UserInfo, ProfileInfo, MedicalInfo, Doctor, Nurse, Hospital, Prescription, MedTest, LogItem, Appointment
from .forms import BaseUserForm, UserForm, ProfileForm, MedicalForm, AppointmentForm
from .models import Patient, UserInfo, ProfileInfo, MedicalInfo, Doctor, Nurse, Hospital, Prescription, MedTest, LogItem
from .forms import BaseUserForm, UserForm, ProfileForm, MedicalForm
from django.views.decorators.csrf import csrf_exempt
import datetime
import itertools
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
				
		print("failed")
		return HttpResponseRedirect('/%s/profile' % request.user.username)
		
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
                    try:
                        newlogitem = LogItem(user=user, datetime=datetime.datetime.now(), action="Staff has logged in")
                        newlogitem.save()
                    except:
                        newlogitem = LogItem(datetime=datetime.datetime.now(), action="Staff has logged in")
                        newlogitem.save()
                    return HttpResponseRedirect('/%s/staffProfile' % username)
                else:
                    try:
                        newlogitem = LogItem(user=user, datetime=datetime.datetime.now(), action="User has logged in")
                        newlogitem.save()
                    except:
                        newlogitem = LogItem(datetime=datetime.datetime.now(), action="User has logged in")
                        newlogitem.save()
                    return HttpResponseRedirect('/%s/profile' % username)
            else:
                auth = 1
                try:
                    newlogitem = LogItem(user=user, datetime=datetime.datetime.now(), action="User has attemtped to log in with expired account")
                    newlogitem.save()
                except:
                    newlogitem = LogItem(datetime=datetime.datetime.now(), action="User has attemtped to log in with expired account")
                    newlogitem.save()
                #all users have a is_valid field that can be toggled for expiration or transfers etc.
                return render(request, 'login.html', {'authenticated': auth , 'username' : username, 'password' : password})
        else:
            auth = 2
            try:
                newlogitem = LogItem(user=user, datetime=datetime.datetime.now(), action="Invalid user has attempted to log in")
                newlogitem.save()
            except:
                newlogitem = LogItem(datetime=datetime.datetime.now(), action="Invalid user has attempted to log in")
                newlogitem.save()
            return render(request, 'login.html', {'authenticated': auth , 'username' : username, 'password' : password})
    else:
        try:
            newlogitem = LogItem(user=None, datetime=datetime.datetime.now(), action="Login page accessed")
            newlogitem.save()
        except:
            newlogitem = LogItem(datetime=datetime.datetime.now(), action="Login page accessed")
            newlogitem.save()
        return render(request, "login.html", {'authenticated':auth})

@csrf_exempt
def userLogout(request):
    logout(request)
    try:
        newlogitem = LogItem(user=request.user, datetime=datetime.datetime.now(), action="User has logged out")
        newlogitem.save()
    except:
        newlogitem = LogItem(datetime=datetime.datetime.now(), action="User has logged out")
        newlogitem.save()
    return HttpResponseRedirect('/')

@csrf_exempt
def register(request):
    registered = False
    print("\nregister view entered")

    if request.method == 'POST':
        print("\nregister entered with POST")
        #this is where all of the data the user input is gathered.
        baseUserForm = BaseUserForm(data=request.POST)

        print("\nregister POST baseUserFormCreated")
        userForm = UserForm(data=request.POST)
        print("\nregister POST userFormCreated")
        profileForm = ProfileForm(data=request.POST)
        print("\nregister POST profileFormCreated")
        medicalForm = MedicalForm(data=request.POST)
        print("\nregister POST medicalFormCreated")

        print("\nregister POST outside is_valid if")

        #The forms are checked to determine if they are valid. This is where required fields are checked.
        if  userForm.is_valid() and profileForm.is_valid() and medicalForm.is_valid():

            print("\nregister POST inside is_valid if")

            #creating the user object
            user = baseUserForm.save()
            user.set_password(user.password)

            #all adjusted values must be followed by a save call.
            user.save()
            print("\nregister POST user object created")

            patientUserInfo = userForm.save()
            patientProfileInfo = profileForm.save()
            patientMedicalInfo = medicalForm.save()
            print("\nregister POST 3 info objects created")

            patient = Patient(user=user, userInfo = patientUserInfo, profileInfo=patientProfileInfo, medicalInfo=patientMedicalInfo)
            print("\nregister POST patient created")

            patient.user.save()
            patient.userInfo.save()
            patient.profileInfo.save()
            patient.medicalInfo.save()

            patient.save()
            print("\nregister POST patient info objects assigned")

            print("\nAttempting to add hospital and doctor object to patient with lookups")
            patient.hospital = Hospital.objects.get(name=request.POST['hospital'])
            userDoctor = User.objects.get(username=request.POST['doctor'])
            patient.doctor = Doctor.objects.get(user=userDoctor)
            patient.save()

            patient.user.first_name = patient.profileInfo.firstName
            patient.user.last_name = patient.profileInfo.lastName
            patient.user.email = patient.profileInfo.email
            patient.user.save()
            print("\nregister POST user first/last name updated")

            registered = True

            print("\nregister POST about to call profile")
            try:
                newlogitem = LogItem(user=request.user, datetime=datetime.datetime.now(), action="New Patient registered")
                newlogitem.save()
            except:
                newlogitem = LogItem(datetime=datetime.datetime.now(), action="New Patient registered")
                newlogitem.save()
            userLogin(request)
            print("\nThe following will not be reached but needs to be there to prevent errors:wq")
            return HttpResponseRedirect('/%s/profile' % patient.user.username)
        else:
            #these errors should be added into the registration.html so the user can see it
            print(baseUserForm.errors, userForm.errors, profileForm.errors, medicalForm.errors)
            try:
                newlogitem = LogItem(user=request.user, datetime=datetime.datetime.now(), action="Registration POST data invalid")
                newlogitem.save()
            except:
                newlogitem = LogItem(datetime=datetime.datetime.now(), action="Registration POST data invalid")
                newlogitem.save()
    else:
        print("\nregister GET creating blank forms")
        #if the request is get, show blank forms.
        baseUserForm = BaseUserForm()
        userForm = UserForm()
        profileForm = ProfileForm()
        medicalForm = MedicalForm()
        print(Doctor.objects.all())
        print(Hospital.objects.all())
        print("\nregister GET blank forms created")
        try:
            newlogitem = LogItem(user=request.user, datetime=datetime.datetime.now(), action="Registration page accessed")
            newlogitem.save()
        except:
            newlogitem = LogItem(datetime=datetime.datetime.now(), action="Registration page accessed")
            newlogitem.save()
    return render(request, 'registration.html', {'baseUserForm':baseUserForm, 'userForm':userForm, 'profileForm':profileForm, 'medicalForm':medicalForm, 'registered': registered, 'doctorlist' : Doctor.objects.all(), 'hospitallist': Hospital.objects.all()})

@csrf_exempt
def profile(request, username):
    #check that the user is actually logged in so they can't access someone's profile just
    #by knowing the url. If they aren't authenticated they get redirected to the login page
    #using the reverse lookup which searches the urls in urls.py for a name of 'login'
    if not request.user.is_authenticated():
        try:
            newlogitem = LogItem(user=request.user, datetime=datetime.datetime.now(), action="Patient profile page access attempt by unathenticated user")
            newlogitem.save()
        except:
            newlogitem = LogItem(datetime=datetime.datetime.now(), action="Patient profile page access attempt by unathenticated user")
            newlogitem.save()
        return HttpResponseRedirect(reverse('login'))
    else:
        #capture the user object and run checks on the account type to determine where to send them
        #In the future we may need to check for doctors and nurses and send them elsewhere.
        activeUser = Patient.objects.get(user=request.user)
        checklist = activeUser.medicalInfo._meta.get_fields()
        newchecklist = []
        try:
            newlogitem = LogItem(user=request.user, datetime=datetime.datetime.now(), action="Patient profile page accessed")
            newlogitem.save()
        except:
            newlogitem = LogItem(datetime=datetime.datetime.now(), action="Patient profile page accessed")
            newlogitem.save()
        print (activeUser.doctor)
        for check in checklist:
            newchecklist.append(getattr(activeUser.medicalInfo, check.name))

        #print(newchecklist)
        iterator = itertools.count()
        #print(iterator)

    user = request.user
    appointments = Appointment.objects.filter(userName = user.username)
		
    return render(request, 'ProfilePage.html', {'user' : activeUser, 'checklist' : checklist, 'newchecklist' : newchecklist, 'iterator':iterator, 'appointments': appointments, 'appform': AppointmentForm })
    return render(request, 'ProfilePage.html', {'user' : activeUser, 'checklist' : checklist, 'newchecklist' : newchecklist, 'iterator':iterator })

@csrf_exempt
def staffProfile(request, username):
    #check that the user is actually logged in so they can't access someone's profile just
    #by knowing the url. If they aren't authenticated they get redirected to the login page
    #using the reverse lookup which searches the urls in urls.py for a name of 'login'
    if not request.user.is_authenticated():
        try:
            newlogitem = LogItem(user=request.user, datetime=datetime.datetime.now(), action="Staff profile page access attempt by unathenticated user")
            newlogitem.save()
        except:
            newlogitem = LogItem(datetime=datetime.datetime.now(), action="Staff profile page access attempt by unathenticated user")
            newlogitem.save()
        return HttpResponseRedirect(reverse('login'))
    else:
        #capture the user object and run checks on the account type to determine where to send them
        #In the future we may need to check for doctors and nurses and send them elsewhere.
        accountType = "Doctor"
        activeUser = Doctor.objects.get(user=request.user)
        if activeUser:
            try:
                newlogitem = LogItem(user=request.user, datetime=datetime.datetime.now(), action="Staff profile page accessed by Doctor")
                newlogitem.save()
            except:
                newlogitem = LogItem(datetime=datetime.datetime.now(), action="Staff profile page accessed by Doctor")
                newlogitem.save()
            try:
                patients = Patient.objects.get(doctor=activeUser)
            except Patient.DoesNotExist:
                patients = None

        else:
            try:
                newlogitem = LogItem(user=request.user, datetime=datetime.datetime.now(), action="Staff profile page accessed by Nurse")
                newlogitem.save()
            except:
                newlogitem = LogItem(datetime=datetime.datetime.now(), action="Staff profile page accessed by Nurse")
                newlogitem.save()
            activeUser = Nurse.objects.get(user=request.user)
            accountType = "Nurse"
            try:
                patients = Patient.objects.get(hospital=activeUser.hospital)
            except Patient.DoesNotExist:
                patients = None

    return render(request, 'StaffProfile.html', {'user' : activeUser, 'accountType' : accountType, 'patients' : patients})
@csrf_exempt
def profileEdit(request, username):
    registered = False
    print("\nEdit profile view entered")
    if request.method == 'POST':
        print("\nregister entered with POST")
        #this is where all of the data the user input is gathered.
        baseUserForm = BaseUserForm(data=request.POST)

        print("\nregister POST baseUserFormCreated")
        userForm = UserForm(data=request.POST)
        print("\nregister POST userFormCreated")
        profileForm = ProfileForm(data=request.POST)
        print("\nregister POST profileFormCreated")
        medicalForm = MedicalForm(data=request.POST)
        print("\nregister POST medicalFormCreated")

        print("\nregister POST outside is_valid if")
        #The forms are checked to determine if they are valid. This is where required fields are checked.
        if  userForm.is_valid() and profileForm.is_valid() and medicalForm.is_valid():

            print("\nregister POST inside is_valid if")

            #creating the user object
            user = baseUserForm.save()
            user.set_password(user.password)

            #all adjusted values must be followed by a save call.
            user.save()
            print("\nregister POST user object created")

            patientUserInfo = userForm.save()
            patientProfileInfo = profileForm.save()
            patientMedicalInfo = medicalForm.save()
            print("\nregister POST 3 info objects created")

            patient = Patient(user=user, userInfo = patientUserInfo, profileInfo=patientProfileInfo, medicalInfo=patientMedicalInfo)
            print("\nregister POST patient created")

            patient.user.save()
            patient.userInfo.save()
            patient.profileInfo.save()
            patient.medicalInfo.save()

            patient.save()
            print("\nregister POST patient info objects assigned")

            print("\nAttempting to add hospital and doctor object to patient with lookups")
            patient.hospital = Hospital.objects.get(name=request.POST['hospital'])
            userDoctor = User.objects.get(username=request.POST['doctor'])
            patient.doctor = Doctor.objects.get(user=userDoctor)
            patient.save()

            patient.user.first_name = patient.profileInfo.firstName
            patient.user.last_name = patient.profileInfo.lastName
            patient.user.email = patient.profileInfo.email
            patient.user.save()
            print("\nregister POST user first/last name updated")

            registered = True

            print("\nregister POST about to call profile")
            userLogin(request)
            print("\nThe following will not be reached but needs to be there to prevent errors:wq")
            return HttpResponseRedirect('/%s/profile' % patient.user.username)
        else:
            #these errors should be added into the registration.html so the user can see it
            print(baseUserForm.errors, userForm.errors, profileForm.errors, medicalForm.errors)
    else:
        print("\nregister GET creating blank forms")
        #if the request is get, show blank forms.
        userForm = UserForm()
        profileForm = ProfileForm()
        print(Doctor.objects.all())
        print(Hospital.objects.all())
        print("\nregister GET blank forms created")
    return render(request, 'ProfileEdit.html', {'userForm':userForm, 'profileForm':profileForm, 'doctorlist' : Doctor.objects.all(), 'hospitallist': Hospital.objects.all()})

@csrf_exempt
def fillDB():
    userone = User.objects.create_user("userone", "nomail@rit.edu", "qwerty")
    print(userone)
    userone.save()