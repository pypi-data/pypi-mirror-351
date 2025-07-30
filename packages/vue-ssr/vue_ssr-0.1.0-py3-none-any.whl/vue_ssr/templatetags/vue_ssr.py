import json
from typing import Any

from django import template
from django.utils.safestring import mark_safe

from ..services import render

register = template.Library()


@register.simple_tag
def render_vue(entry: str, props: dict[str, Any] | None = None, **kwargs):
    """
    Render a Vue SSR entry with the given props.
    :param entry: The server entry name.
    :param props: The props passed to the entry.
    :param kwargs: The props passed to the entry. Takes precedence over the props argument.
    :return: The rendered HTML.

    Example:
    ```django
    {% load vue_ssr %}
    <my-app>{% render_vue "app" myProp="value" %}</my-app>
    ```
    """

    props = props or {}
    props = {**props, **kwargs}

    data: dict[str, Any] = {}

    if props:
        data["props"] = props

    rendered = render(entry, props)

    if rendered is None:
        # SSR rendering failed, fall back to client-side rendering
        data["forceClientRender"] = True

    output = ""

    if data:
        output += '<script type="application/json">%s</script>' % json.dumps(data)

    if rendered:
        output += rendered

    return mark_safe(output)
