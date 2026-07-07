from django import template

register = template.Library()


@register.simple_tag
def star_display(rating):
    """Split a 0-5 rating into full/half/empty star counts for template iteration."""
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = 0

    full = max(0, min(5, int(rating)))
    half = 1 if (rating - full) >= 0.5 and full < 5 else 0
    empty = 5 - full - half
    return {"full": range(full), "half": range(half), "empty": range(empty)}
