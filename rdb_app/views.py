from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404

from rdb_app.forms import UserCreateForm, AuthenticateForm, ReceptForm, IngredientForm, HoeveelheidForm
from rdb_app.models import Recept, Ingredient, Hoeveelheid, Foto

def home(request, auth_form=None, user_form=None):
  """
  Homepage
  """
  # Check if logged in
  if request.user.is_authenticated():
    user = request.user
    return render(request,"recepten.html",
                  {'recepten': Recept.objects.all(),
                   'user': user} )
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
def toevoegen(request):
  HoeveelheidFormSet = formset_factory(HoeveelheidForm)
  if request.method == "POST":
    recept_form = ReceptForm(request.POST, request.FILES)
    ingredient_form = IngredientForm(request.POST)
    hoeveelheid_formset = HoeveelheidFormSet(request.POST)
    if 'add' in request.POST:
      # Need to add an hoeveelheid form in the hoeveelheid_formset
      cp = request.POST.copy()
      cp['form-TOTAL_FORMS'] = int(cp['form-TOTAL_FORMS']) + 1
      hoeveelheid_formset = HoeveelheidFormSet(cp)
    else:
      if ingredient_form.is_valid():
        data = ingredient_form.cleaned_data
        Ingredient.objects.create(naam=data['ingredient_naam'], seizoen=data['ingredient_seizoen'])
        ingredient_form = IngredientForm()
      if recept_form.is_valid():
        if hoeveelheid_formset.is_valid():
          data = recept_form.cleaned_data
          hoeveelheid_data = hoeveelheid_formset.cleaned_data
          recept = Recept.objects.create(naam=data['recept_naam'],user=request.user,bereidingstijd=data['bereidingstijd'],aantal_personen=data['aantalpersonen'],bereiding=data['bereiding'],seizoen=data['seizoen'], vegetarisch=data['vegetarisch'])
          if 'fotos' in request.FILES.keys():
            foto = Foto.objects.create(image=request.FILES['fotos'], naam=data['recept_naam'])
            recept.fotos.add(foto)
          if 'doel' in request.POST:
            recept.doel.add(request.POST['doel'])
          for h_data in hoeveelheid_data:
            h = Hoeveelheid.objects.create(hoeveelheid=h_data['hoeveelheid'],recept=recept,ingredient=h_data['ingredient'])
          return redirect('/')
  else:
    hoeveelheid_formset = HoeveelheidFormSet()
    recept_form = ReceptForm()
    ingredient_form = IngredientForm()
  return render(request, "toevoegen.html", { 'recept_form': recept_form, 'ingredient_form': ingredient_form, 'hoeveelheid_formset': hoeveelheid_formset, 'user': request.user }, context_instance=RequestContext(request))

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
