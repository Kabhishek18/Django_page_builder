# Kabhishek Portfolio & Page Builder

A powerful Django-based content management system with an intuitive block-based page builder, template management, and media organization capabilities.

## Features

- **WordPress-like Page Builder**: Create dynamic pages using modular, reusable blocks
- **Template Management System**: Create, edit, and manage HTML templates via the admin interface
- **Media Management**: Organize and upload files with folder structure support
- **Theme Support**: Switch between multiple themes with customizable options
- **SEO Optimization**: Built-in SEO fields and metadata management
- **Contact Forms**: Ready-to-use contact and newsletter functionalities
- **Responsive Design**: Mobile-friendly design based on Bootstrap 5
- **Environment Configuration**: Secure credential storage using .env files
- **AWS S3 Integration**: Optional cloud storage for media and static files

## System Requirements

- Python 3.8+
- Django 4.2+
- PostgreSQL (recommended for production) or SQLite (development)
- Node.js and npm (for frontend asset management, optional)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Kabhishek18/Django_page_builder
cd Django_page_builder
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

### 7. Collect Static Files

```bash
python manage.py collectstatic
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

Access the site at http://127.0.0.1:8000/ and the admin panel at http://127.0.0.1:8000/admin/

## Project Structure

```
kabhishek-portfolio/
├── core/                      # Main project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── storage_backends.py
│   ├── urls.py
│   └── wsgi.py
├── portfolio/                 # Main portfolio app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── middleware.py
│   ├── models.py
│   ├── sitemaps.py
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
│   ├── context_processors.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── media/                     # Media management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── templates/                 # Global templates
│   ├── admin/
│   ├── base.html
│   ├── blocks/
│   └── pages/
├── static/                    # Static files
│   ├── css/
│   ├── js/
│   └── img/
├── media_files/               # Uploaded files
├── manage.py
├── requirements.txt
└── .env                       # Environment variables
```

## Configuration Options

### Environment Variables

Edit your `.env` file with the following options:

```
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings (leave empty to use SQLite)
DATABASE_URL=postgres://user:password@localhost:5432/dbname

# AWS S3 settings (for production file storage)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1

# Email settings
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@example.com

# Theme settings
ACTIVE_THEME=default
```

### Database Settings

By default, the project uses SQLite for development. For production, PostgreSQL is recommended:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# If DATABASE_URL is provided, use that instead (for production with PostgreSQL)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL)
```

## Usage Guide

### Admin Interface

The custom admin interface is organized into logical sections:

1. **Content**: Manage pages and blocks
2. **Media**: Upload and organize files
3. **Appearance**: Manage themes and templates
4. **Settings**: Configure site-wide settings

### Creating Pages

1. Log in to the admin interface
2. Go to "Content" > "Pages"
3. Click "Add Page" and fill in the basic information
4. Fill in SEO metadata and navigation settings
5. Save the page to create it

### Adding Blocks to Pages

1. On the page edit screen, scroll down to the "Blocks" section
2. Click "Add another Block"
3. Choose a block type:
   - **Template**: Uses predefined templates from your theme
   - **WYSIWYG**: Rich text editor for content
   - **Raw HTML**: Direct HTML/CSS/JS code
4. Fill in the content and settings for the block
5. Set the block's position to control its order on the page
6. Save the page to apply your changes

### Managing Templates

1. Go to "Appearance" > "Templates"
2. Create, edit, preview, or delete templates
3. Templates are organized by type (Page, Block, Partial)
4. Use the template editor with syntax highlighting

### Template Creation

When creating templates, you can use Django template syntax with these available variables:

#### Page Templates:
```
{{ page }} - The current page object
{{ page.title }} - The page title
{{ blocks }} - All blocks for this page
```

#### Block Templates:
```
{{ block }} - The current block object
{{ block.content }} - Block content
{{ block.get_settings }} - Block JSON settings
```

### Media Management

1. Go to "Media" > "Media Folders" to create folders
2. Go to "Media" > "Media Items" to upload and manage files
3. Images are automatically optimized and metadata is extracted

### Theme Management

1. Go to "Appearance" > "Themes"
2. Create a new theme by providing name, description, and template directory
3. Set a theme as active to apply it to your site
4. Customize theme options to control colors, fonts, and more

## Advanced Usage

### Custom Block Templates

1. Create a new HTML template in the `templates/blocks/` directory or use the template manager
2. The template will be automatically available in the block type dropdown
3. Access block data using the `{{ block }}` variable

Example block template:
```html
<div id="block-{{ block.id }}" class="my-custom-block">
    <h2>{{ block.get_settings.title }}</h2>
    <div class="content">
        {{ block.content|safe }}
    </div>
</div>
```

### Custom Page Templates

1. Create a new HTML template in the `templates/pages/` directory or use the template manager
2. The template will be automatically available for pages with matching slug or as a default template
3. Access page data using the `{{ page }}` variable and blocks using `{{ blocks }}`

Example page template:
```html
{% extends "base.html" %}

{% block content %}
<div class="custom-page-layout">
    <h1>{{ page.title }}</h1>
    
    {% for block in blocks %}
        {% include block.get_template with block=block %}
    {% endfor %}
</div>
{% endblock %}
```

### Working with Block Settings

Block settings are stored as JSON and can be accessed in templates using `{{ block.get_settings }}`.

Example JSON settings for a slider block:
```json
{
  "autoplay": true,
  "speed": 500,
  "slides": [
    {"image": "/media/slide1.jpg", "title": "Slide 1", "caption": "Description text"},
    {"image": "/media/slide2.jpg", "title": "Slide 2", "caption": "Description text"},
    {"image": "/media/slide3.jpg", "title": "Slide 3", "caption": "Description text"}
  ]
}
```

Access in template:
```html
<div class="slider" data-autoplay="{{ block.get_settings.autoplay }}" data-speed="{{ block.get_settings.speed }}">
    {% for slide in block.get_settings.slides %}
    <div class="slide">
        <img src="{{ slide.image }}" alt="{{ slide.title }}">
        <div class="caption">
            <h3>{{ slide.title }}</h3>
            <p>{{ slide.caption }}</p>
        </div>
    </div>
    {% endfor %}
</div>
```

## Deployment

### Preparing for Production

1. Set `DEBUG=False` in your `.env` file
2. Configure a proper database (PostgreSQL recommended)
3. Set up AWS S3 for static and media file storage
4. Update `ALLOWED_HOSTS` with your domain
5. Generate a new `SECRET_KEY`

### Deploying to a VPS or Dedicated Server

1. Set up a production-ready web server (Nginx, Apache)
2. Configure Gunicorn or uWSGI as the WSGI server
3. Set up SSL certificates (Let's Encrypt recommended)
4. Configure database backups

Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/mediafiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/yourdomain.sock;
    }
}
```

### Deploying to PaaS (Heroku, etc.)

1. Create a `Procfile`:
```
web: gunicorn core.wsgi --log-file -
```

2. Configure your platform's environment variables
3. Set up PostgreSQL add-on
4. Configure your platform to run migrations on deploy

## Extending the System

### Adding New Block Types

1. Update the `BLOCK_TYPE_CHOICES` in the `Block` model
2. Create corresponding template files
3. Update the admin interface to handle the new block type

### Adding New Apps

1. Create a new Django app:
```bash
python manage.py startapp myapp
```

2. Add to `INSTALLED_APPS` in `settings.py`
3. Create models, views, templates, and URLs
4. Update the main `urls.py` to include your app's URLs

### Custom Admin Extensions

Extend the admin interface by customizing the `admin.py` files in your apps.

Example of adding a custom admin action:
```python
@admin.action(description="Publish selected pages")
def make_published(modeladmin, request, queryset):
    queryset.update(status='published')

class PageAdmin(admin.ModelAdmin):
    # ...existing code...
    actions = [make_published]
```

## Troubleshooting

### Common Issues

1. **Template Not Found**: Ensure templates are in the correct directory, and the template loader can find them.
2. **Static Files Not Loading**: Run `collectstatic` and check your static file settings.
3. **Database Migrations**: Run `python manage.py makemigrations` followed by `python manage.py migrate`.
4. **Media File Uploads**: Ensure media directory permissions are correct and the directory exists.
5. **AWS S3 Access**: Verify your credentials and bucket permissions.

### Debug Mode

For development, set `DEBUG=True` in your `.env` file to see detailed error pages.

### Logging

Configure Django's logging to track errors:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

## Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

### Coding Standards

- Follow PEP 8 Python style guide
- Use Django coding style for templates and models
- Document your code with docstrings
- Write meaningful commit messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

Developed by [Kabhishek18](https://github.com/kabhishek18)

### Third-party Libraries

- Django
- Django CKEditor
- Django Colorfield
- Django Storages
- Bootstrap 5
- Font Awesome
- CodeMirror

## Contact

For questions, feature requests, or issues, please contact:
- Email: [kabhishek18@gmail.com]
- GitHub: [kabhishek18](https://github.com/kabhishek18)