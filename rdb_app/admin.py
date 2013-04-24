from rdb_app.models import Recept, Ingredient, Type, Foto, Hoeveelheid
from django.contrib import admin

class HoeveelheidInline(admin.TabularInline):
  model = Hoeveelheid
  extra = 1

class Admin(admin.ModelAdmin):
  pass

admin.site.register(Recept)
admin.site.register(Ingredient)
admin.site.register(Type)
admin.site.register(Foto)
admin.site.register(Hoeveelheid)
