# django-svg-sprite

A Django template tag for easy use of SVG sprites in templates.

## Quick start

1. Add `django_svg_sprite` to your `INSTALLED_APPS` setting like this:

    ```python
    INSTALLED_APPS = [
        ...,
        'django_svg_sprite',
    ]
    ```

2. Set the `SVG_SPRITE` setting to the SVG sprite file in your static files to be used, e.g.:

    ```python
    SVG_SPRITE = 'bootstrap-icons.svg'
    ```

3. Use the tag in your template, e.g.:

    ```django
    {% load svg_sprite %}
    {% svg_sprite 'hand-thumbs-up' fill='yellow' class='bi' %}
    ```

See [settings](https://tmb.codeberg.page/django-svg-sprite/settings/) and [template tags documentation](https://tmb.codeberg.page/django-svg-sprite/templatetags/) for details.

## License

This project is licensed under the MIT license.
