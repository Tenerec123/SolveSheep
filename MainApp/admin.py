from collections import defaultdict
from decimal import Decimal

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import *
# Register your models here.


class SolutionInline(admin.TabularInline):
    model = Solution
    extra = 1  # cuántos formularios vacíos mostrar por defecto
    fields = ('text',) 

class ProblemInline(admin.TabularInline):
    model = Bundle.problems.through
    extra = 1  # cuántos formularios vacíos mostrar por defecto


class ProblemAreaWeightInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        totals = defaultdict(Decimal)
        for form in self.forms:
            data = form.cleaned_data
            if not data or data.get("DELETE"):
                continue
            area = data.get("area")
            weight = data.get("weight")
            if area is not None and weight is not None:
                totals[area.kind] += weight

        if any(total != Decimal("1.0000") for total in totals.values()):
            raise ValidationError(
                "Weights must total exactly 1.0000 for each populated classification."
            )


class ProblemAreaWeightInline(admin.TabularInline):
    model = ProblemAreaWeight
    formset = ProblemAreaWeightInlineFormSet
    extra = 1


class ProblemAdmin(admin.ModelAdmin):

    only_read = ("created", "updated")
    list_filter = ("dif_tag", "type_tags")
    inlines = [SolutionInline, ProblemAreaWeightInline]

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
    actions = ["accept_solutions", "reject_solutions"]

    @admin.action(description="Accept selected solutions (visible on the problem page)")
    def accept_solutions(self, request, queryset):
        queryset.update(accepted=True)

    @admin.action(description="Reject selected solutions (delete)")
    def reject_solutions(self, request, queryset):
        queryset.delete()



admin.site.register(TypeTag, TypeTagAdmin)
admin.site.register(DifTag, DifTagAdmin)
admin.site.register(AreaTag)
admin.site.register(ProblemAreaWeight)
admin.site.register(ProblemProgress)
admin.site.register(ProblemAttempt)
admin.site.register(AreaRating)
admin.site.register(ProblemHint)
admin.site.register(Solution, SolutionAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Bundle, BundleAdmin)