from django.db import models
from django.contrib.auth.models import User

SEIZOENEN = (
  ('', ''),
  ('Lente','Lente'),
  ('Zomer','Zomer'),
  ('Herfst','Herfst'),
  ('Winter','Winter')
  )

class Recept(models.Model):
  naam = models.CharField(verbose_name="Naam",max_length=512)
  user = models.ForeignKey(User)
  creation_date = models.DateTimeField(auto_now=True, blank=True)
  bereidingstijd = models.IntegerField()
  ingredienten = models.ManyToManyField('Ingredient', through='Hoeveelheid', related_name='contained_in', symmetrical=False) # gebruik contained_in om te vinden welke recepten een ingredient bevatten
  aantal_personen = models.IntegerField()
  fotos = models.ManyToManyField('Foto',blank=True)
  bereiding = models.TextField()
  doel = models.ManyToManyField('Type')
  seizoen = models.CharField(max_length=20,choices=SEIZOENEN, blank=True)
  vegetarisch = models.BooleanField()
  
  def __unicode__(self):
    return self.naam
    
  def photoAvailable(self):
    """
    Is er een foto bij dit recept?
    """
    return self.fotos.count() > 0
    
  def getAnyPhoto(self):
    """
    Geef een foto terug (default: de eerste foto)
    """
    return self.fotos.all()[0]
      
class Ingredient(models.Model):
  naam = models.CharField(max_length=180)
  seizoen = models.CharField(max_length=20,choices=SEIZOENEN,blank=True)
  
  def getSeizoen(self):
    """
    Geeft het seizoen van dit ingredient terug (kan leeg zijn)
    """
    return self.seizoen
    
    def __unicode__(self):
      return self.naam
      
class Hoeveelheid(models.Model):
  ingredient = models.ForeignKey(Ingredient)
  recept = models.ForeignKey(Recept)
  hoeveelheid = models.CharField(max_length=120)
  
  def __unicode__(self):
    return self.ingredient.__unicode__() + u' in ' + self.recept.__unicode__()
    
class Type(models.Model):
  doel = models.CharField(max_length=180)
  
  def __unicode__(self):
    return self.doel
    
class Foto(models.Model):
  naam = models.CharField(max_length=180)
  image = models.ImageField(upload_to='.')
  
  def __unicode__(self):
    return self.naam
    
class Nota(models.Model):
  user = models.ForeignKey(User)
  recept = models.ForeignKey(Recept)
  nota = models.TextField()
  
  def __unicode__(self):
    return self.user.__unicode__() +" zegt over "+ self.recept.__unicode__() +\
            ": "+self.nota
  

