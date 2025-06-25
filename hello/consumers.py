from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Document
import json

class DocumentConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time collaborative editing of documents.
    """

    async def connect(self):
        """
        Handles a new WebSocket connection.
        - Authenticates the user.
        - Adds the user to a document-specific group.
        - Notifies the group of the user's connection.
        """
        # Retrieve the document ID from the URL and generate a group name
        self.doc_id = self.scope['url_route']['kwargs']['doc_id']
        self.group_name = f'document_{self.doc_id}'
        self.user = self.scope['user']

        print(f'User attempting to connect: {self.user} (Authenticated: {self.user.is_authenticated})')

        # Check if the user has permission to access the document
        has_permission = await self.user_has_permission()

        if has_permission:
            # Add the user to the group and accept the WebSocket connection
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            # Notify the group that the user has connected
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_connected',
                    'user': self.user.username,
                }
            )
        else:
            # Close the connection if the user does not have permission
            await self.close()

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        - Saves the current document content.
        - Notifies the group of the user's disconnection.
        - Removes the user from the document-specific group.
        """
        # Save the current content of the document
        content = await self.get_current_content()
        await self.save_document_content(content)

        # Notify the group that the user has disconnected
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'user_disconnected',
                'user': self.user.username,
            }
        )

        # Remove the user from the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Handles incoming messages from the WebSocket client.
        - Processes actions such as 'edit' or 'typing'.
        - Broadcasts updates to the group.
        """
        try:
            # Parse the received JSON data
            data = json.loads(text_data)
            action = data.get('action')
            user = self.user.username

            if action == 'edit':
                # Handle document editing actions
                content = data.get('content', '')
                cursor_position = data.get('cursor_position', None)

                # Broadcast the updated content and cursor position to the group
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'document_update',
                        'content': content,
                        'cursor_position': cursor_position,
                        'user': user,
                    }
                )

            elif action == 'typing':
                # Handle typing indicator actions
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'typing_indicator',
                        'user': user,
                    }
                )
        except Exception as e:
            # Handle any errors and send an error message to the client
            await self.send(text_data=json.dumps({"action": "error", "message": str(e)}))

    async def typing_indicator(self, event):
        """
        Broadcasts a typing indicator to all group members.
        """
        user = event['user']
        await self.send(text_data=json.dumps({
            'action': 'typing',
            'user': user,
        }))

    async def document_update(self, event):
        """
        Broadcasts document updates (content and cursor position) to all group members.
        """
        content = event['content']
        cursor_position = event.get('cursor_position', None)
        user = event['user']

        await self.send(text_data=json.dumps({
            'action': 'edit',
            'content': content,
            'cursor_position': cursor_position,
            'user': user,
        }))

    async def user_connected(self, event):
        """
        Notifies all group members when a new user connects.
        """
        user = event['user']
        await self.send(text_data=json.dumps({
            'action': 'user_connected',
            'user': user,
        }))

    async def user_disconnected(self, event):
        """
        Notifies all group members when a user disconnects.
        """
        user = event['user']
        await self.send(text_data=json.dumps({
            'action': 'user_disconnected',
            'user': user,
        }))

    @database_sync_to_async
    def user_has_permission(self):
        """
        Checks if the connected user has permission to access the document.
        - Returns True if the user is the owner or is shared with them.
        - Returns False otherwise.
        """
        try:
            document = Document.objects.get(id=self.doc_id)
            return document.owner == self.user or self.user in document.shared_with.all()
        except Document.DoesNotExist:
            return False

    @database_sync_to_async
    def get_current_content(self):
        """
        Retrieves the current content of the document.
        """
        try:
            document = Document.objects.get(id=self.doc_id)
            return document.content
        except Document.DoesNotExist:
            return ""

    @database_sync_to_async
    def save_document_content(self, content):
        """
        Saves the provided content to the document.
        """
        try:
            document = Document.objects.get(id=self.doc_id)
            document.content = content
            document.save()
            return True
        except Document.DoesNotExist:
            return False
