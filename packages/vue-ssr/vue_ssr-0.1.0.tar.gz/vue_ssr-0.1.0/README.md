# Vue Server-Side Rendering in Python

[![Test Workflow](https://github.com/krmax44/vue-ssr-python/actions/workflows/test.yaml/badge.svg)](https://github.com/krmax44/vue-ssr-python/actions/workflows/test.yaml)
[![PyPI - Version](https://img.shields.io/pypi/v/vue-ssr)](https://pypi.org/project/vue-ssr/)
[![API documentation](https://img.shields.io/badge/-api%20docs-blue)](https://krmax44.github.io/vue-ssr-python/vue_ssr.html)


Client for [`vue-ssr-service`](https://github.com/krmax44/vue-ssr-service). See its documentation for a [quick start guide](https://github.com/krmax44/vue-ssr-service#getting-started-with-vite).

> [!WARNING]
> This project is in a proof-of-concept state.

## Stand-alone

```python
from vue_ssr import ServerRenderer

renderer = ServerRenderer()
renderer.render("myComponent", props={"name": "friend"})
# "<p>Hello, friend!</p>"
```

## With Django

Works well in conjunction with [`django-vite`](https://github.com/MrBin99/django-vite). Add it to your installed apps:

```py
INSTALLED_APPS = [
  "vue_ssr",
  ...
]
```

Then, you can simply use the provided template tag:

```django
{% load vue_ssr %}
<user-greeting>{% render_vue "userGreeting" name=request.user.username %}</user-greeting>
```

Or pass a dict with props:

```django
<my-app>{% render_vue "myApp" props=props %}</my-app>
```
