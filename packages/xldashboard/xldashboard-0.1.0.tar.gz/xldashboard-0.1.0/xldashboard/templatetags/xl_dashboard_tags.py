# xl_dashboard/templatetags/xl_dashboard_tags.py

from django import template
from django.apps import apps
from django.conf import settings
from django.contrib.admin.sites import site as admin_site
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('xl_dashboard/xl_dashboard.html', takes_context=True)
def show_xl_dashboard(context):
    """
    Показывает XL Dashboard.
    Вызывается в шаблоне как:
        {% load xl_dashboard_tags %}
        {% show_xl_dashboard %}
    """
    xl_dashboard = getattr(settings, 'XL_DASHBOARD', {})
    user = context['request'].user  # noqa

    sections = []
    actions = xl_dashboard.get('xl-actions', {})

    for section_name, models_map in xl_dashboard.items():
        if section_name == 'xl-actions':
            continue  # пропускаем экшены, они отдельно выводятся
        items = []
        for item_name, model_path in models_map.items():
            if isinstance(model_path, str):
                if model_path.startswith('/'):
                    # Если значение начинается с '/', считаем, что это готовая ссылка
                    admin_link = model_path
                    items.append((item_name, admin_link))
                    continue
                try:
                    # Пытаемся получить модель через apps.get_model
                    try:
                        model = apps.get_model(model_path)
                    except LookupError:
                        # Если не получилось – пробуем импортировать напрямую
                        module_path, class_name = model_path.rsplit('.', 1)
                        mod = __import__(module_path, fromlist=[class_name])
                        model = getattr(mod, class_name)
                    # Если модель не зарегистрирована в админке, генерировать URL не получится
                    if model not in admin_site._registry:  # noqa
                        raise Exception('Model not registered in admin')
                    admin_link = reverse(
                        f'admin:{model._meta.app_label}_{model._meta.model_name}_changelist'  # noqa
                    )
                    items.append((item_name, admin_link))
                except Exception as e:  # noqa
                    # print(f"Ошибка для модели {model_path}: {e}")  # Лог ошибки
                    items.append((item_name, '#invalid-model-path'))
            else:
                items.append((item_name, '#unknown-type'))
        sections.append((section_name, items))

    return {
        'sections': sections,
        'actions': actions,
        'request': context['request']
    }
