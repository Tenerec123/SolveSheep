from django.contrib import admin
from .models import *
# Register your models here.
from django.urls import path
from django.shortcuts import redirect


class SolutionInline(admin.TabularInline):
    model = Solution
    extra = 1  # cuántos formularios vacíos mostrar por defecto
    fields = ('text',) 

class ProblemInline(admin.TabularInline):
    model = Bundle.problems.through
    extra = 1  # cuántos formularios vacíos mostrar por defecto


class ProblemAdmin(admin.ModelAdmin):

    only_read = ("created", "updated")
    list_filter = ("dif_tag", "type_tags")
    inlines = [SolutionInline,]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('AI_generator/', self.admin_site.admin_view(self.ia_generator_view), name='AI_generator'),
        ]
        return custom_urls + urls

    def ia_generator_view(self, request, bund_id):
 
        return redirect("Create_Problem", )

class BundleAdmin(admin.ModelAdmin):
    change_form_template = "admin/ai_button.html"
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