from django import template
import markdown2

register = template.Library()

@register.filter
def markdownify(text):
    return markdown2.markdown(text, extras=[
        "fenced-code-blocks",
        "tables",
        "strike",
        "footnotes",
        "cuddled-lists",
        "metadata",
        "smarty-pants",
        "wiki-tables",
        "task_list",
        "header-ids",
    ])