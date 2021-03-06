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
  naam = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Naam'}),label="Recept naam")
  bereidingstijd = forms.IntegerField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Bereidingstijd'}))
  aantal_personen = forms.IntegerField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Aantal personen'}),label="Aantal personen")
  doel = chosenforms.ChosenModelChoiceField(overlay="Type gerecht...",queryset=Type.objects.order_by('doel'), empty_label='')
  seizoen = chosenforms.ChosenChoiceField(overlay="Kies een seizoen (optioneel)...",choices=SEIZOENEN, required=False)
  vegetarisch = forms.BooleanField(required=False)
  bereiding = forms.CharField(widget=forms.widgets.Textarea(attrs={'class':'ckeditor'}))
  def __init__(self, *args, **kwargs):
    super(ReceptForm, self).__init__(*args,**kwargs)
    self.fields['doel'].widget.attrs.update({'label':'Type gerecht','style':'width:350px;','class':'chzn-select-type'})
    self.fields['seizoen'].widget.attrs.update({'class': 'chzn-select-seizoen', 'style':'width:350px;'})

class IngredientForm(forms.Form):
  ingredient_naam = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Naam'}))
  ingredient_seizoen = chosenforms.ChosenChoiceField(choices=SEIZOENEN, required=False, overlay="Kies een seizoen (optioneel)...")
  def __init__(self, *args, **kwargs):
    super(IngredientForm, self).__init__(*args, **kwargs)
    self.fields['ingredient_seizoen'].widget.attrs.update({'style': 'width:350px;',})

class HoeveelheidForm(forms.Form):
  ingredient = chosenforms.ChosenModelChoiceField(overlay="Ingredient...",queryset=Ingredient.objects.order_by('naam'), empty_label='')
  hoeveelheid = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Hoeveelheid'}))
  def __init__(self, *args, **kwargs):
    super(HoeveelheidForm, self).__init__(*args, **kwargs)
    self.fields['ingredient'].widget.attrs.update({'class': 'chzn-select-hoeveelheid', 'style': 'width:62%'})

class TypeForm(forms.Form):
  type_naam = forms.CharField()

class ImageForm(forms.Form):
  foto = forms.ImageField(required=False)
  
  def __init__(self, *args, **kwargs):
    super(ImageForm, self).__init__(*args, **kwargs)
    self.fields['foto'].widget.attrs.update({'style': 'width: 70%',})

class SearchForm(forms.Form):
  ingredienten = chosenforms.ChosenModelMultipleChoiceField(\
    overlay="Selecteer ingredienten...", \
    queryset=Ingredient.objects.order_by('naam'))
  types = chosenforms.ChosenModelMultipleChoiceField(\
    overlay="Selecteer type gerecht ...",\
    queryset=Type.objects.order_by('doel'))
  seizoenen = chosenforms.ChosenChoiceField(\
    overlay="Selecteer seizoen ...",\
    choices=SEIZOENEN)
  tijd = chosenforms.ChosenChoiceField(\
    overlay="Selecteer tijd ...",\
    choices=(\
      ('', ' '), \
      ("15", "< 15 minuten"), \
      ("30", "< 30 minuten"), \
      ("45", "< 45 minuten"), \
      ("60", "< 60 minuten")))
  vegetarisch = forms.BooleanField(help_text="Vegetarisch?")
  
  def __init__(self, *args, **kwargs):
    super(SearchForm, self).__init__(*args, **kwargs)
    self.fields['ingredienten'].widget.attrs.update({'style': 'width:350px;',})
    self.fields['types'].widget.attrs.update({'style': 'width:350px',})
    self.fields['seizoenen'].widget.attrs.update({'style': 'width:350px',})
    self.fields['tijd'].widget.attrs.update({'style': 'width:350px',})
