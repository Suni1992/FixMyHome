#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    
    # ---- यहाँ अपना कोड डालिए ----
    import django
    django.setup()
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        if not User.objects.filter(username='sunilkumar').exists():
            User.objects.create_superuser('sunilkumar', 'admin@example.com', 'Sunil@1234')
            print("Superuser created successfully!")
    except Exception:
        pass  # अगर टेबल न हो, तो चुपचाप आगे बढ़ जाओ, बिल्ड फेल मत करो
    # ----------------------------

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '_main_':
    main()