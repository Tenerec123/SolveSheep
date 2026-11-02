from django import template


register = template.Library()
AREA_KINDS = ("cognitive", "mathematical")


def get_problem_area_tags(problem):
    """Return up to two weighted area names per axis, ordered by weight."""
    groups = {kind: [] for kind in AREA_KINDS}
    prefetched_weights = getattr(problem, "_prefetched_objects_cache", {}).get("area_weights")
    if prefetched_weights is None:
        weights = problem.area_weights.select_related("area").all()
    else:
        weights = prefetched_weights

    ordered_weights = sorted(
        weights,
        key=lambda item: (
            item.area.kind,
            -item.weight,
            item.area.name.casefold(),
            item.pk,
        ),
    )
    for item in ordered_weights:
        names = groups.get(item.area.kind)
        if names is not None and len(names) < 2:
            names.append(item.area.name)
    return groups


@register.simple_tag
def problem_area_tags(problem):
    return get_problem_area_tags(problem)
