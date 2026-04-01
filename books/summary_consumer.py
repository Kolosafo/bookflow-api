import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import BookAnalysisResponse, UserExtractedBooks
from .serializers import BookAnalysisResponseSerializer
from .gemini import generate_summary_keypoints
from .save_summary import save_book_analysis
from account.subscription_utils import update_subscription_usage
from account.models import UserSubscriptionUsage

logger = logging.getLogger(__name__)


class BookSummaryConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for book summary generation.

    Client connects with JWT token in query string:
        ws://domain/summarize/?token=<jwt_token>

    Client sends:
    {
        "type": "summarize",
        "book_id": "...",
        "title": "...",
        "author": "...",
        "img": "..."
    }

    Server emits:
    - { "type": "summary_status", "status": "pending",  "message": "..." }
    - { "type": "summary_status", "status": "success",  "data": { ... } }
    - { "type": "summary_status", "status": "failed",   "message": "..." }
    """

    async def connect(self):
        # JWTAuthMiddleware already validated the token and set scope["user"]
        user = self.scope.get('user')
        if not user or isinstance(user, AnonymousUser):
            await self.close(code=4001)
            return

        self.user = user
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'status': 'success'
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self._send_error('Invalid JSON format')
            return

        if data.get('type') == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong', 'status': 'success'}))
            return

        book_id = data.get('book_id')
        book_title = data.get('title')
        book_author = data.get('author')
        book_img = data.get('img', '')

        if not all([book_id, book_title, book_author]):
            await self._send_error('Missing required fields: book_id, title, author')
            return

        # Check subscription limit before doing any work
        has_quota = await self.check_summary_quota()
        if not has_quota:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'UsageLimitReached',
                'status': 'error',
            }))
            return

        # Track extracted book & decrement usage
        await self.track_extracted_book(book_id, book_title, book_author, book_img)
        await sync_to_async(update_subscription_usage)(self.user, 'summaries')

        # Return cached summary if it already exists
        existing = await self.get_existing_summary(book_id)
        if existing:
            await self.send(text_data=json.dumps({
                'type': 'summary_status',
                'status': 'success',
                'data': existing,
            }))
            return

        # Emit pending
        await self.send(text_data=json.dumps({
            'type': 'summary_status',
            'status': 'pending',
            'message': 'Generating summary...',
        }))

        # Generate and save
        try:
            raw = await sync_to_async(generate_summary_keypoints)(book_title, book_author)
            parsed = json.loads(raw)
            await sync_to_async(save_book_analysis)(parsed, book_title, book_author, book_id)
        except Exception as e:
            logger.error(f"Summary generation failed: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'summary_status',
                'status': 'failed',
                'message': 'Summary generation failed. Please try again.',
            }))
            return

        # Fetch and return the saved summary
        saved = await self.get_existing_summary(book_id)
        await self.send(text_data=json.dumps({
            'type': 'summary_status',
            'status': 'success',
            'data': saved,
        }))

    async def _send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
            'status': 'error',
        }))

    @database_sync_to_async
    def check_summary_quota(self):
        try:
            usage = UserSubscriptionUsage.objects.get(user=self.user)
            return usage.summaries > 0
        except UserSubscriptionUsage.DoesNotExist:
            return False

    @database_sync_to_async
    def get_existing_summary(self, book_id):
        try:
            book = BookAnalysisResponse.objects.get(book_id=book_id)
            return BookAnalysisResponseSerializer(book).data
        except BookAnalysisResponse.DoesNotExist:
            return None

    @database_sync_to_async
    def track_extracted_book(self, book_id, book_title, book_author, book_img):
        try:
            UserExtractedBooks.objects.get_or_create(
                user=self.user,
                book_id=book_id,
                defaults={
                    'book_author': book_author,
                    'book_title': book_title,
                    'book_img': book_img,
                }
            )
        except Exception as e:
            logger.warning(f"Could not track extracted book: {e}")
