from django.shortcuts import render, redirect, get_object_or_404
from store.models import Vendor, Product
from .models import Conversation, Message
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import send_mail
from django.db.models import Q 
from django.contrib import messages
# Create your views here.


@login_required
def start_conversation(request, vendor_id, product_id=None):
    
    vendor = get_object_or_404(Vendor, id=vendor_id)
    product = get_object_or_404(Product, id=product_id) if product_id else None

    # moved this check ABOVE get_or_create — see note below
    if request.user == getattr(vendor, 'user', None):
        messages.error(request, "You can't message your own store.")
        return redirect('store_detail', pk=vendor.id)

    conversation, created = Conversation.objects.get_or_create(buyer=request.user, vendor=vendor, product=product)
    
    if created and product:
        conversation.product_name_snapshot = product.vinyl_name
        conversation.save()
        
    return redirect('conversation_detail', pk=conversation.id)

@login_required
def conversation_detail(request, pk):
    
    conversation = get_object_or_404(Conversation, pk=pk)
    
    if request.user != conversation.buyer and request.user != getattr(conversation.vendor, 'user', None):
        return redirect('home')
    
    if request.method == "POST":
        body = request.POST.get('body', '').strip()
        
        if body:
            Message.objects.create(conversation=conversation, sender=request.user, body=body)
            conversation.save()
            
            recipient_email= conversation.vendor.email if request.user == conversation.buyer else conversation.buyer.email
            send_mail(subject=f"New message from {request.user}",
                      message=body,
                      from_email=None,
                      recipient_list=[recipient_email],
                      fail_silently=True,
                      )
            
        return redirect('conversation_detail', pk=pk)  # fixed — was 'messaging/conversation_detail'
    
    return render(request, 'messaging/conversation_detail.html', {'conversation': conversation, 'messages': conversation.messages.all()})


@login_required
def inbox(request):
    
    conversation = Conversation.objects.filter(
        buyer=request.user
    ) | Conversation.objects.filter(
        vendor__user=request.user
    )
    
    conversations = conversation.distinct().order_by('-updated_at')
    
    return render(request, 'messaging/inbox.html', {'conversations': conversations})  # fixed — was 'inbox.html'

@login_required
def poll_messages(request, pk):
    
    conversation = get_object_or_404(Conversation, pk=pk)
    since_id = request.GET.get('since', 0)
    new_messages = conversation.messages.filter(id__gt=since_id).exclude(sender=request.user)
    data = [{'id': message.id,
             'sender': str(message.sender),
             'body' : message.body,
             'created_at':message.created_at.strftime('%H:%M'),
             }
            for message in new_messages]
    
    return JsonResponse({'messages' : data})


@login_required
def unread_count(request):
    
    conversations = Conversation.objects.filter(Q(buyer=request.user) | Q(vendor__user=request.user))
    count = Message.objects.filter(conversation__in=conversations,
                                   is_read=False,).exclude(sender=request.user).count()
    
    return JsonResponse({'count': count})

@login_required
def edit_message(request, pk):
    
    message = get_object_or_404(Message, pk=pk)
    
    if message.sender != request.user:
        return redirect('conversation_detail', pk=message.conversation.id)  # fixed
    
    if request.method == "POST":
        
        new_body = request.POST.get('body', '').strip()
        if new_body:
            message.body = new_body
            message.is_edited = True
            message.save()
            
        return redirect('conversation_detail', pk=message.conversation.id) 
    
    return render(request, 'messaging/edit_message.html', {'message': message})

@login_required
def delete_message(request, pk):
    message = get_object_or_404(Message, pk=pk)
    
    if message.sender != request.user:
        return redirect('conversation_detail', pk=message.conversation.id) 
    
    conversation_id = message.conversation.id
    
    if request.method == 'POST':
        message.delete()
        return redirect('conversation_detail', pk=conversation_id)  # fixed
    
    return render(request, 'messaging/delete_message.html', {'message': message})  