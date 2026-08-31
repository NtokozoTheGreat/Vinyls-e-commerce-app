from django.db import models

# Create your models here

from django.conf import settings
from django.urls import reverse


class Conversation(models.Model):
    """
    Represents a conversation between a buyer and a vendor.

    Conversations provide a dedicated messaging thread that
    may optionally be associated with a product listing.
    The product name is stored separately to preserve
    historical context if the product is later removed.
    """

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='buyer_conversations',
        on_delete=models.CASCADE 
    )

    vendor = models.ForeignKey(
        'store.Vendor',
        related_name='vendor_conversations',
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        'store.Product',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
        )

    # Preserve the original product name after
    # the associated Product has been deleted.
    product_name_snapshot = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:                      
        ordering = ['-updated_at']     
                                       
    def __str__(self):                 
        return f"{self.buyer} <-> {self.vendor.store_name}"

    def get_absolute_url(self):        
        return reverse('conversation_detail', args=[self.id])


class Message(models.Model):
    """
    Represents an individual message within a conversation.

    Stores the sender, message content, timestamps,
    and read/edit status.
    """

    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender} ({self.created_at:%Y-%m-%d %H:%M})"
