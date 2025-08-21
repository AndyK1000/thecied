from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import ChatSession, ChatMessage
import json
import uuid
import requests

def chat_page(request):
    """Serve the chat page"""
    return render(request, 'chat.html')

@csrf_exempt
@require_POST
def chat_api(request):
    """Handle chat API requests"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get or create chat session
        session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={'user': request.user if request.user.is_authenticated else None}
        )
        
        # Save user message
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=message
        )
        
        # Get chat history for context
        messages = list(session.messages.all().values('role', 'content'))
        
        # Call OpenAI API
        response = call_openai_api(messages)
        
        if response:
            # Save assistant response
            ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=response
            )
            
            return JsonResponse({
                'response': response,
                'session_id': session_id
            })
        else:
            return JsonResponse({'error': 'Failed to get response from AI'}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def call_openai_api(messages):
    """Call OpenAI API to get chat response"""
    try:
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key:
            return "Sorry, the chat service is not configured. Please contact an administrator."
            
        # Prepare messages for OpenAI API format
        openai_messages = []
        
        # Add system message
        openai_messages.append({
            "role": "system",
            "content": "You are a helpful assistant for The CIED (Center for Innovation and Economic Development). You can help with questions about events, venue bookings, and general inquiries."
        })
        
        # Add conversation history
        for msg in messages[-10:]:  # Limit to last 10 messages for context
            openai_messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': openai_messages,
            'max_tokens': 500,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data['choices'][0]['message']['content'].strip()
        else:
            print(f"OpenAI API error: {response.status_code} - {response.text}")
            return "Sorry, I'm having trouble connecting to the chat service. Please try again later."
            
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return "Sorry, there was a network error. Please try again later."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Sorry, something went wrong. Please try again later."

@csrf_exempt
def get_chat_history(request):
    """Get chat history for a session"""
    session_id = request.GET.get('session_id')
    if not session_id:
        return JsonResponse({'error': 'Session ID is required'}, status=400)
    
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = list(session.messages.all().values('role', 'content', 'created_at'))
        
        return JsonResponse({
            'session_id': session_id,
            'messages': messages
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({'messages': []})
