// static/js/template_admin.js
(function($) {
    $(document).ready(function() {
        // Initialize CodeMirror for syntax highlighting and auto-completion
        if ($("#id_content").length) {
            var editor = CodeMirror.fromTextArea(document.getElementById("id_content"), {
                mode: "htmlmixed",
                lineNumbers: true,
                matchBrackets: true,
                indentUnit: 4,
                theme: "default"
            });
            
            // Set initial height
            editor.setSize(null, 500);
            
            // Add a fullscreen toggle button
            var fullScreenBtn = $('<button type="button" class="button">Toggle Fullscreen</button>');
            $(editor.getWrapperElement()).before(fullScreenBtn);
            
            fullScreenBtn.on('click', function() {
                $(editor.getWrapperElement()).toggleClass('fullscreen');
                if ($(editor.getWrapperElement()).hasClass('fullscreen')) {
                    editor.setSize('100%', '100vh');
                } else {
                    editor.setSize(null, 500);
                }
                editor.refresh();
            });
            
            // Add common Django template tags as buttons
            var tagButtons = $('<div class="template-tag-buttons"></div>');
            var commonTags = [
                { label: 'for loop', snippet: '{% for item in items %}\n    \n{% endfor %}' },
                { label: 'if', snippet: '{% if condition %}\n    \n{% endif %}' },
                { label: 'block', snippet: '{% block name %}\n    \n{% endblock %}' },
                { label: 'extends', snippet: '{% extends "base.html" %}' },
                { label: 'include', snippet: '{% include "template.html" %}' },
                { label: 'variable', snippet: '{{ variable }}' },
            ];
            
            commonTags.forEach(function(tag) {
                var btn = $('<button type="button" class="button">' + tag.label + '</button>');
                btn.on('click', function() {
                    editor.replaceSelection(tag.snippet);
                    editor.focus();
                });
                tagButtons.append(btn);
            });
            
            $(editor.getWrapperElement()).before(tagButtons);
        }
    });
})(django.jQuery);