# Kabhishek18 Portfolio Website

A Django-based portfolio website with WordPress-like functionality.



## Project Structure
portfolio_project/
    ├── core/                      # Main project settings
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── portfolio/                 # Main portfolio app
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── urls.py
    │   └── views.py
    ├── pagebuilder/               # Block-based page builder
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── templatetags/
    │   ├── urls.py
    │   └── views.py
    ├── themes/                    # Theme management
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   └── views.py
    ├── media/                     # Media management
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   └── views.py
    ├── templates/                 # Global templates
    │   ├── admin/
    │   │   └── base_site.html     # Customized admin template
    │   ├── base.html
    │   ├── blocks/                # Block templates
    │   │   ├── hero.html
    │   │   ├── text.html
    │   │   ├── gallery.html
    │   │   └── custom.html
    │   └── pages/                 # Page templates
    │       ├── default.html
    │       └── home.html
    ├── static/                    # Static files
    │   ├── css/
    │   ├── js/
    │   └── img/
    ├── media_files/               # Uploaded files
    ├── manage.py
    ├── requirements.txt
    └── .env                       # Environment variables

## Development

- Use `python manage.py makemigrations` to create new migrations
- Use `python manage.py migrate` to apply migrations
- Use `python manage.py collectstatic` to collect static files

## Deployment

The project is configured for deployment on platforms like Heroku, AWS, or DigitalOcean. See the deployment documentation for specific instructions. # Django_page_builder
# Django_page_builder
# Django_page_builder
