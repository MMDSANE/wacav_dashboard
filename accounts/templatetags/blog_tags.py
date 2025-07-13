# from ..models import *
# from django import template
# from django.db.models import Count
# from markdown import markdown
# register = template.Library()
#
# @register.simple_tag()
# def total_posts():
#     return Post.published.count()
#
# @register.simple_tag(name='tc')
# def total_comments():
#     return Comment.objects.count()
#
# @register.simple_tag()
# def last_post_date():
#     return Post.published.last().publish
#
# @register.simple_tag()
# def most_popular_post(count = 5):
#     return Post.published.annotate(comments_count= Count('Comments')).order_by('-comments_count')[:count]
#
# @register.inclusion_tag('partials/latest_posts.html')
# def latest_posts(count = 3):
#     l_p = Post.published.order_by('-publish')[:count]
#     context = {'l_p':l_p}
#     return context
#
# @register.filter(name='markdown')
# def to_markdown(text):
#     return markdown(text)