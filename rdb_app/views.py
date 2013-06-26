from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponse
from django.core.serializers import serialize
from django.utils import simplejson as json
from django.db.models import Q

import re

from rdb_app.forms import UserCreateForm, AuthenticateForm, ReceptForm, IngredientForm, HoeveelheidForm, SearchForm, TypeForm, ImageForm
from rdb_app.models import Recept, Ingredient, Hoeveelheid, Foto, Type

def home(request, ingredienten_ids=None, types_ids=None, seizoenen=None, vegetarisch=None, tijd=None, auth_form=None, user_form=None, search_form=None):
  """
  Homepage
  """
  # Check if logged in
  if request.user.is_authenticated():
    # Setting up the search form
    user = request.user
    search_form = search_form or SearchForm()
    
    # Are there ingredients requested?
    ingredienten = list()		# Default empty list
    if ingredienten_ids != None and ingredienten_ids != "":
      ingredienten = re.sub("/$", "", ingredienten_ids).split(",")
    
    # Are there types requested?
    types = list()          # Default empty list
    if types_ids != None and types_ids != "":
       types = types_ids.split(",")
    
    # Is a season requested?
    seizoen = list()        # Default empty list
    if seizoenen != None and seizoenen != "":
      seizoen = seizoenen.split(",")
    
    # All recipes
    recipes = Recept.objects.all()
    
    # Retrieve all recipes containing the desired ingredients
    recipes = reduce(lambda recipes, ingredient: \
      recipes.filter(ingredienten__id__exact=ingredient), \
      ingredienten, \
      recipes)
    
    # Retrieve all recipes of the desired types
    recipes = reduce(lambda recipes, t: recipes.filter(doel__id__exact=t), \
      types, recipes)
    
    # Retrieve all recipes in the desired season (or without season)
    recipes = reduce(lambda recipes, s: \
      recipes.filter(Q(seizoen=s)|Q(seizoen__isnull=True)|Q(seizoen="")),\
      seizoen, recipes)
    
    # Retrieve only vegetarian recipes if requested
    if vegetarisch != None:
      recipes = recipes.filter(vegetarisch="1")
    
    # Retrieve only recipes faster than requested time
    if tijd != None:
      recipes = recipes.filter(bereidingstijd__lt=tijd)
    
    return render(request,"recepten.html",
                  {'recepten': recipes,
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
def toevoegen(request, recept_form=None, hoeveelheid_formset=None, image_formset=None):
  '''
  Generates the page and forms used to submit a recipe
  '''
  recept_form = recept_form or ReceptForm()
  HoeveelheidFormset = formset_factory(HoeveelheidForm)
  hoeveelheid_formset = hoeveelheid_formset or HoeveelheidFormset()
  ImageFormset = formset_factory(ImageForm)
  image_formset = image_formset or ImageFormset(prefix="image_form")
  context = { 'recept_form': recept_form,
              'hoeveelheid_formset': hoeveelheid_formset,
              'image_formset': image_formset,
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
  ImageFormset = formset_factory(ImageForm)
  if request.method=='POST' and 'submit_recipe' in request.POST:
    recept_form = ReceptForm(request.POST, request.FILES)
    hoeveelheid_formset = HoeveelheidFormset(request.POST)
    image_formset = ImageFormset(request.POST, request.FILES, prefix="image_form")
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
        if image_formset.is_valid():
          for (i, f) in enumerate(request.FILES.keys()):
            foto = Foto.objects.create(image=request.FILES[f], naam=data['recept_naam']+'image_' + str(i))
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
    image_formset = ImageFormset(prefix="image_form")
  return toevoegen(request, recept_form=recept_form, hoeveelheid_formset=hoeveelheid_formset, image_formset=image_formset)

@login_required
def recept(request, recept_id, personen=None):  
  # Fetch recipe and quantities
  recept = get_object_or_404(Recept, pk=recept_id)
  hoeveelheden = \
    get_list_or_404(Hoeveelheid, recept=Recept.objects.get(pk=recept_id))
  
  # If a number of persons is given, adjust the quantities
  if personen != None:
    # Conversion factor
    factor = float(personen) / float(recept.aantal_personen)
    
    for hoeveelheid in hoeveelheden:
      # Get the number out
      m = re.search("[0-9\.,]+", hoeveelheid.hoeveelheid)
      
      if m != None:
        # Convert number
        num = float(m.group()) * factor
        if num.is_integer():
          num = "%d" % num
        else:
          num = "%.1f" % num
        
        # Put it back
        hoeveelheid.hoeveelheid = \
          re.sub("[0-9\.,]+", num, hoeveelheid.hoeveelheid)
        
  
  # Passing values and render
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
  '''
  View a list of all ingredients
  '''
  ingredienten = Ingredient.objects.all()
  context = {'ingredienten': ingredienten}
  return render_to_response('ingredienten.html', context_instance=RequestContext(request, context))

@login_required
def profile(request):
  '''
  User profile page
  '''
  recipes = get_list_or_404(Recept, user=request.user)
  context = { 'recipes': recipes }
  return render_to_response('profile.html', context_instance=RequestContext(request, context))

@login_required
def edit_recipe(request, recept_id):
  if request.method == "POST":
    # TODO: Handle submitted form
    pass
  recept = get_object_or_404(Recept, pk=recept_id)
  context = { 'recept': recept }
  return render_to_response('edit_recipe.html', context_instance=RequestContext(request, context))

@login_required
def delete_recipe(request, recept_id):
  recept = Recept.objects.filter(user=request.user).get(pk=recept_id).delete()
  return redirect('/')
