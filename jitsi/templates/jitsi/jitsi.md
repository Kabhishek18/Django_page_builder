# Jitsi Templates Setup Guide

## Template Directory Structure

Place all templates in this directory structure:

```
jitsi/
└── templates/
    └── jitsi/
        ├── dashboard.html
        ├── create_room.html
        ├── room_detail.html
        ├── join_meeting.html
        ├── meeting_embed.html
        └── customize_meeting.html
```

In your existing project structure, this would map to:

```
kabhishek-portfolio/
├── core/
├── portfolio/
├── pagebuilder/
├── themes/
├── media/
├── jitsi/                       # New Jitsi app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── services.py
│   ├── forms.py
│   ├── urls.py
│   ├── views.py
│   └── templates/              # Templates directory inside app
│       └── jitsi/              # Namespace for templates
│           ├── dashboard.html
│           ├── create_room.html
│           ├── room_detail.html
│           ├── join_meeting.html
│           ├── meeting_embed.html
│           └── customize_meeting.html
├── templates/
├── static/
├── media_files/
├── manage.py
└── requirements.txt
```

This approach uses app-specific templates, which Django will automatically find.