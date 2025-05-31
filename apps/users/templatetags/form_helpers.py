# 🔧 Custom template tag to render form fields with consistent Bootstrap styling and optional disabling

from django import template  # Django's template system

# 🎯 Register a new template tag library
register = template.Library()

@register.simple_tag
def render_input(field, placeholder="", disable=False):
    """
    🧩 Renders a form input field with:
    - Bootstrap form-control classes
    - Custom placeholder
    - Optional disabled state

    📌 Usage in template:
        {% render_input form.username "Username" disable_fields %}
    """
    # 🖌️ Base attributes for styling
    attrs = {
        "class": "form-control form-control-app",  # Bootstrap + your custom class
        "placeholder": placeholder                 # Show placeholder text
    }

    # 🚫 If field should be disabled, add that attribute
    if disable:
        attrs["disabled"] = "disabled"

    # 📤 Render the field widget with custom attributes
    return field.as_widget(attrs=attrs)
