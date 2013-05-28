from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponse
from django.core.serializers import serialize
from django.utils import simplejson as json

from rdb_app.forms import UserCreateForm, AuthenticateForm, ReceptForm, IngredientForm, HoeveelheidForm, SearchForm, TypeForm
from rdb_app.models import Recept, Ingredient, Hoeveelheid, Foto, Type

def home(request, auth_form=None, user_form=None, search_form=None):
  """
  Homepage
  """
  # Check if logged in
  if request.user.is_authenticated():
    user = request.user
    search_form = search_form or SearchForm()
    return render(request,"recepten.html",
                  {'recepten': Recept.objects.all(),
                   'user': user,
                   'search_form': search_form, } )
  # If not logged in
  else:
    auth_form = auth_form or AuthenticateForm()
    user_form = user_form or UserCreateForm()
    return render(request,"home.html", {'auth_form': auth_form, 'user_form': user_form, })

def signup(request):
  """
  Sign up a new user
  """
  user_form = UserCreateForm(request.POST)
  if request.method=="POST":
    if user_form.is_valid():
      username = user_form.clean_username()
      password = user_form.clean_password2()
      user_form.save()
      user = authenticate(username=username,password=password)
      login(request, user)
      return redirect('/')
    else:
      return home(request, user_form=user_form)
  return render(request, "home.html", { 'user_form': user_form, })

def loginview(request):
  if request.method=="POST":
    form = AuthenticateForm(data=request.POST)
    if form.is_valid():
      login(request, form.get_user())
      return redirect('/')
    else:
      return home(request, auth_form=form)
  return redirect('/')

def logoutview(request):
  logout(request)
  return redirect('/')

@login_required
def toevoegen(request, recept_form=None, hoeveelheid_formset=None):
  '''
  Generates the page and forms used to submit a recipe
  '''
  recept_form = recept_form or ReceptForm()
  HoeveelheidFormset = formset_factory(HoeveelheidForm)
  hoeveelheid_formset = hoeveelheid_formset or HoeveelheidFormset()
  context = { 'recept_form': recept_form,
              'hoeveelheid_formset': hoeveelheid_formset,
              'user': request.user, }
  return render(request, 'toevoegen.html', context)

@login_required
def ingredient_toevoegen(request):
  '''
  Submit a new ingredient
  Should be called by AJAX
  '''
  if request.method=="POST":
    try:
      ingredient_form = IngredientForm(request.POST)
    except:
      return HttpResponseServerError('Error in ingredient_toevoegen.')
    if ingredient_form.is_valid():
      data = ingredient_form.cleaned_data
      ingredient_naam = data['ingredient_naam'][0].upper() + data['ingredient_naam'][1:].lower()
      ingredient_seizoen = data['ingredient_seizoen']
      # Check if the ingredient is already in the database
      if Ingredient.objects.filter(naam=ingredient_naam).count()==0:
        Ingredient.objects.create(naam=ingredient_naam, seizoen=ingredient_seizoen)
  return HttpResponse(serialize('json', (Ingredient.objects.latest('id'),)), mimetype="application/json")

@login_required
def type_toevoegen(request):
  '''
  Submit a new type
  Should be called be AJAX
  '''
  if request.method=="POST":
    try:
      type_form = TypeForm(request.POST)
    except:
      return HttpResponseServerError('Error in type_toevoegen')
    if type_form.is_valid():
      data = type_form.cleaned_data
      type_naam = data['type_naam'][0].upper() + data['type_naam'][1:].lower()
      Type.objects.create(doel=type_naam)
  return HttpResponse(serialize('json', (Type.objects.latest('id'),)), mimetype="application/json")

@login_required
def submit_recipe(request):
  '''
  Handle a submitted recipe form
  '''
  HoeveelheidFormset = formset_factory(HoeveelheidForm)
  if request.method=='POST' and 'submit_recipe' in request.POST:
    recept_form = ReceptForm(request.POST, request.FILES)
    hoeveelheid_formset = HoeveelheidFormset(request.POST)
    # Check if the forms are valid, and add the recipe. Redirect to home page
    # afterwards
    if recept_form.is_valid():
      if hoeveelheid_formset.is_valid():
        data = recept_form.cleaned_data
        hoeveelheid_data = hoeveelheid_formset.cleaned_data
        recept = Recept.objects.create(naam=data['recept_naam'],
                                       user=request.user,
                                       bereidingstijd=data['bereidingstijd'],
                                       aantal_personen=data['aantalpersonen'],
                                       bereiding=data['bereiding'],
                                       seizoen=data['seizoen'],
                                       vegetarisch=data['vegetarisch'])
        if 'fotos' in request.FILES.keys():
          foto = Foto.objects.create(image=request.FILES['fotos'], naam=data['recept_naam'])
          recept.fotos.add(foto)
        if 'doel' in request.POST:
          recept.doel.add(request.POST['doel'])
        for h_data in hoeveelheid_data:
          try:
            h = Hoeveelheid.objects.create(hoeveelheid=h_data['hoeveelheid'],
                                           recept=recept,
                                           ingredient=h_data['ingredient'])
          except:
            continue
        return redirect('/')
      else:
        # TODO: Return some useful error message.
        pass
  else:
    recept_form = ReceptForm()
    hoeveelheid_formset = HoeveelheidFormset()
  return toevoegen(request, recept_form=recept_form, hoeveelheid_formset=hoeveelheid_formset)

@login_required
def recept(request, recept_id):
  recept = get_object_or_404(Recept, pk=recept_id)
  hoeveelheden = get_list_or_404(Hoeveelheid, recept=Recept.objects.get(pk=recept_id))
  context = {'recept': recept, 'hoeveelheden': hoeveelheden}
  return render_to_response('recept.html', context_instance=RequestContext(request, context))

@login_required
def ingredient(request, ingredient_id):
  '''
  View one ingredient
  TODO add the list of recipes that include this ingredient
  '''
  ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
  context = {'ingredient': ingredient}
  return render_to_response('ingredient.html', context_instance=RequestContext(request, context))

@login_required
def ingredienten(request):
  ingredienten = Ingredient.objects.all()
  context = {'ingredienten': ingredienten}
  return render_to_response('ingredienten.html', context_instance=RequestContext(request, context))
