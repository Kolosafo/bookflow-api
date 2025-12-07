import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from ..models import ChatHistory
from .main import generate_ai_chat

User = get_user_model()
logger = logging.getLogger(__name__)


class BookChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for book chat AI.

    Client should send messages in this format:
    {
        "type": "chat_message",
        "book_id": "book_id_here",
        "book_title": "Book Title",
        "book_author": "Author Name",
        "summary": "Book summary text",
        "key_insights": "Key insights text",
        "practical_takeaways": "Practical takeaways text",
        "user_message": "User's question here"
    }

    Server will respond with:
    {
        "type": "chat_response",
        "data": {
            "id": "chat_id",
            "user_message": "...",
            "ai_response": "...",
            "noteable": "...",
            ...
        },
        "status": "success"
    }

    Or error:
    {
        "type": "error",
        "message": "Error description",
        "status": "error"
    }
    """

    async def connect(self):
        """Handle WebSocket connection"""
        # Get token from query string
        query_string = self.scope.get('query_string', b'').decode()
        token = None

        # Parse query string for token
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=', 1)[1]
                break

        if not token:
            logger.warning("WebSocket connection attempted without token")
            await self.close(code=4001)
            return

        # Authenticate user
        try:
            validated_token = UntypedToken(token)
            user_id = validated_token.get('user_id')
            self.user = await self.get_user(user_id)

            if not self.user:
                logger.warning(f"User not found for user_id: {user_id}")
                await self.close(code=4002)
                return

        except (InvalidToken, TokenError) as e:
            logger.warning(f"Invalid token: {e}")
            await self.close(code=4003)
            return

        # Accept the connection
        await self.accept()
        logger.info(f"WebSocket connected for user: {self.user.email}")

        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to BookFlow AI Chat',
            'status': 'success'
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        logger.info(f"WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages
        """
        try:
            # Parse incoming message
            data = json.loads(text_data)
            message_type = data.get('type', 'chat_message')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'status': 'success'
                }))
                return

            # Extract chat data
            book_id = data.get('book_id')
            book_title = data.get('book_title')
            book_author = data.get('book_author')
            summary = data.get('summary')
            key_insights = data.get('key_insights', '')
            practical_takeaways = data.get('practical_takeaways', '')
            user_message = data.get('user_message')

            # Validate required fields
            if not all([book_id, book_title, book_author, summary, user_message]):
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Missing required fields: book_id, book_title, book_author, summary, user_message',
                    'status': 'error'
                }))
                return

            # Send processing status
            await self.send(text_data=json.dumps({
                'type': 'processing',
                'message': 'Generating AI response...',
                'status': 'processing'
            }))

            # Generate AI response (run in thread pool to avoid blocking)
            try:
                ai_response_json = await sync_to_async(generate_ai_chat)(
                    user_input=user_message,
                    book_title=book_title,
                    author=book_author,
                    summary=summary,
                    key_insights=key_insights,
                    practical_takeaways=practical_takeaways
                )
            except Exception as ai_error:
                logger.error(f"AI Generation Error: {ai_error}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'AI generation failed: {str(ai_error)}',
                    'status': 'error'
                }))
                return

            # Parse AI response
            try:
                ai_response_data = json.loads(ai_response_json)
                ai_text = ai_response_data.get('text', '')
                noteable = ai_response_data.get('noteable', '')
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON Parse Error: {json_error}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Failed to parse AI response',
                    'status': 'error'
                }))
                return

            # Save chat history to database
            try:
                chat_history = await self.save_chat_history(
                    user=self.user,
                    book_id=book_id,
                    book_title=book_title,
                    book_author=book_author,
                    user_message=user_message,
                    ai_response=ai_text,
                    noteable=noteable
                )

                # Send successful response with saved data
                await self.send(text_data=json.dumps({
                    'type': 'chat_response',
                    'data': {
                        'id': chat_history.id,
                        'user': self.user.id,
                        'book_id': book_id,
                        'book_title': book_title,
                        'book_author': book_author,
                        'user_message': user_message,
                        'ai_response': ai_text,
                        'noteable': noteable,
                        'created_at': chat_history.created_at.isoformat(),
                        'updated_at': chat_history.updated_at.isoformat()
                    },
                    'message': 'Chat response generated successfully',
                    'status': 'success'
                }))

            except Exception as db_error:
                logger.error(f"Database Error: {db_error}")
                # Still send AI response even if saving fails
                await self.send(text_data=json.dumps({
                    'type': 'chat_response',
                    'data': {
                        'user_message': user_message,
                        'ai_response': ai_text,
                        'noteable': noteable,
                        'book_id': book_id,
                        'book_title': book_title,
                        'book_author': book_author
                    },
                    'message': 'Chat response generated but not saved to history',
                    'status': 'partial_success'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format',
                'status': 'error'
            }))
        except Exception as e:
            logger.error(f"Unexpected error in receive: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'An unexpected error occurred: {str(e)}',
                'status': 'error'
            }))

    @database_sync_to_async
    def get_user(self, user_id):
        """Get user from database"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_chat_history(self, user, book_id, book_title, book_author, user_message, ai_response, noteable):
        """Save chat history to database"""
        return ChatHistory.objects.create(
            user=user,
            book_id=book_id,
            book_title=book_title,
            book_author=book_author,
            user_message=user_message,
            ai_response=ai_response,
            noteable=noteable
        )
