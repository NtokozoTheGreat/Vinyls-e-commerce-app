# messaging/context_processors.py

from django.db.models import Q
from .models import Conversation, Message

def unread_messages(request):
    # context processors run automatically on EVERY template render across the whole site —
    # this makes 'unread_message_count' available in every template without passing it manually

    if not request.user.is_authenticated:
        return {'unread_message_count': 0}  # skip the database query entirely for anonymous visitors

    conversations = Conversation.objects.filter(
        Q(buyer=request.user) | Q(vendor__user=request.user)
    )

    count = Message.objects.filter(
        conversation__in=conversations,
        is_read=False,
    ).exclude(sender=request.user).count()

    # the dict key returned here becomes the variable name usable in templates: {{ unread_message_count }}
    return {'unread_message_count': count}