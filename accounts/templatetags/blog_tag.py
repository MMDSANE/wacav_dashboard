# from django.utils.safestring import mark_safe
# from markdown import markdown
# from django.db.models import Count
#
# from ..models import *
# from django import template
#
# register = template.Library() # sakht obj az class template
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
#
# @register.inclusion_tag('partials/latest_posts.html')
# def latest_posts(count = 3): # 3 is default
#     l_p = Post.published.order_by('-publish')[:count]
#     context = {'l_p': l_p}
#     return context
#
# @register.simple_tag()
# def most_popular_post(count=5):
#     return Post.published.annotate(comments_count=Count('Comments')).order_by('-comments_count')[:count]
#
#
# @register.filter(name='markdown')
# def to_markdown(text):
#     return mark_safe(markdown(text))