from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.utils.html import strip_tags
from chosen import forms as chosenforms

from rdb_app.models import Recept, Ingredient, SEIZOENEN, Hoeveelheid, Type

class UserCreateForm(UserCreationForm):
  username = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Username', }))
  email = forms.EmailField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Email', }))
  password1 = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password', }))
  password2 = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password confirmation', }))

  def is_valid(self):
    form = super(UserCreateForm, self).is_valid()
    for f, error in self.errors.iteritems():
      self.errormessages = strip_tags(error)
    return form

  class Meta:
    fields = ["username","email","password1","password2"]
    model = User

class AuthenticateForm(AuthenticationForm):
  username = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Username',}))
  password = forms.CharField(max_length=100, widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password', }))

  def is_valid(self):
    form = super(AuthenticateForm, self).is_valid()
    for f, error in self.errors.iteritems():
      self.errormessages = strip_tags(error)
    return form

class ReceptForm(forms.Form):
  recept_naam = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Naam'}))
  bereidingstijd = forms.IntegerField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Bereidingstijd'}))
  aantalpersonen = forms.IntegerField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Aantal personen'}),label="Aantal personen")
  doel = forms.ModelChoiceField(queryset=Type.objects.all())
  seizoen = forms.ChoiceField(choices=SEIZOENEN, required=False)
  vegetarisch = forms.BooleanField(required=False)
  fotos = forms.ImageField(required=False)
  bereiding = forms.CharField(widget=forms.widgets.Textarea(attrs={'class':'ckeditor'}))

class IngredientForm(forms.Form):
  ingredient_naam = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Naam'}))
  ingredient_seizoen = forms.ChoiceField(choices=SEIZOENEN, required=False)

class HoeveelheidForm(forms.Form):
  #ingredient = forms.ChoiceField(choices=[(ingredient.id, ingredient.naam) for ingredient in Ingredient.objects.all()]) 
  ingredient = forms.ModelChoiceField(queryset=Ingredient.objects.all()) 
  hoeveelheid = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Hoeveelheid'}))

class SearchForm(forms.Form):
  ingredienten = chosenforms.ChosenModelMultipleChoiceField(queryset=Ingredient.objects.all())
  def __init__(self, *args, **kwargs):
    super(SearchForm, self).__init__(*args, **kwargs)
    self.fields['ingredienten'].widget.attrs = {'style': 'width:350px;', 'class': 'chzn-select', 'data-placeholder': 'Selecteer ingredienten...'}
