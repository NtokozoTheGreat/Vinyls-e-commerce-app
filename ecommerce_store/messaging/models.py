from django.db import models

# Create your models here

from django.conf import settings
from django.urls import reverse
from store.models import Vendor, Product 
from django.utils import timezone


class Conversation(models.Model):      # models.Model = base class every Django model must inherit from

    # links this conversation to whichever user is the buyer
    # related_name='buyer_conversations' means you can do user.buyer_conversations.all()
    # to get every conversation where this user was the buyer
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='buyer_conversations',
        on_delete=models.CASCADE       # if the buyer's account is deleted, delete their conversations too
    )

    # links this conversation to a Vendor (string reference avoids circular import issues between apps)
    vendor = models.ForeignKey(
        'store.Vendor',
        related_name='vendor_conversations',
        on_delete=models.CASCADE       # if the vendor is deleted, delete conversations tied to them too
    )

    # optional link to the product this conversation was originally about
    # null=True → allowed to be empty in the database
    # blank=True → allowed to be empty in forms/admin (without this, Django admin would require it)
    product = models.ForeignKey(
        'store.Product',
        null=True,
        blank=True,
        on_delete=models.SET_NULL      # if the product is deleted, just clear this field — don't delete the conversation
    )

    # stores the product's name as plain text at the moment the conversation was created
    # this survives even after the actual Product row is deleted (product field goes to NULL, this stays)
    product_name_snapshot = models.CharField(max_length=255, blank=True)

    # auto_now_add=True: Django sets this ONCE, automatically, the first time the row is saved — never changes after
    created_at = models.DateTimeField(auto_now_add=True)

    # auto_now=True: Django updates this EVERY time .save() is called on this row
    # we use this to track "when was this conversation last active" for inbox sorting
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:                        # Meta holds model-level configuration, not a database field itself
        ordering = ['-updated_at']     # default sort order for any query on this model — newest activity first
                                        # the minus sign means descending order

    def __str__(self):                 # controls what prints when you do print(some_conversation) or view it in admin
        return f"{self.buyer} <-> {self.vendor.store_name}"

    def get_absolute_url(self):        # convenience method: conversation.get_absolute_url() instead of typing reverse() everywhere
        return reverse('conversation_detail', args=[self.id])


class Message(models.Model):

    # which conversation thread this message belongs to
    # related_name='messages' lets you do conversation.messages.all() to get every message in that thread
    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE       # if the conversation is deleted, delete all its messages too — orphaned messages make no sense
    )

    # who sent this specific message — could be the buyer or the vendor's linked user account
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE       # if the sender's account is deleted, delete messages they sent
    )

    body = models.TextField()          # the actual message content — TextField has no length limit (unlike CharField)

    created_at = models.DateTimeField(auto_now_add=True)  # set once, when the message is first sent
    updated_at = models.DateTimeField(auto_now=True)      # updates every time this row is saved (i.e. when edited)

    is_read = models.BooleanField(default=False)          # has the recipient seen this message yet? used for unread badge
    is_edited = models.BooleanField(default=False)        # was this message ever edited? lets templates show "(edited)"

    class Meta:
        ordering = ['created_at']      # oldest messages first — displays top-to-bottom like a normal chat log