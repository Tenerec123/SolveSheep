from django.contrib import admin
from .models import *
# Register your models here.

class SolutionInline(admin.TabularInline):
    model = Solution
    extra = 1  # cuántos formularios vacíos mostrar por defecto
    fields = ('text',) 

class ProblemInline(admin.TabularInline):
    model = Bundle.problems.through
    extra = 1  # cuántos formularios vacíos mostrar por defecto

class ProblemAdmin(admin.ModelAdmin):
    only_read = ("created", "updated")
    list_filter = ("dif_tags", "type_tags")
    inlines = [SolutionInline,]

class BundleAdmin(admin.ModelAdmin):
    only_read = ("created", "updated")
    #list_filter = ("dif_tags", "type_tags")
    inlines = [ProblemInline,]
    exclude = ("problems",)


class TypeTagAdmin(admin.ModelAdmin):
    only_read = ()

class DifTagAdmin(admin.ModelAdmin):
    only_read = ()

class SolutionAdmin(admin.ModelAdmin):
    only_read = ()



admin.site.register(TypeTag, TypeTagAdmin)
admin.site.register(DifTag, DifTagAdmin)
admin.site.register(Solution, SolutionAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Bundle, BundleAdmin)