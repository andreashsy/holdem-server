import json
import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'test'
        self.user_id = None

        await (self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        print(f"{str(datetime.now())} - Group {self.room_group_name} has {len(self.channel_layer.groups.get(self.room_group_name, {}).items())} connection(s)")
        asyncio.create_task(self.wait_and_send_msg(3))

    async def wait_and_send_msg(self, seconds: int):
        await asyncio.sleep(seconds)

        await (self.channel_layer.group_send)(
        self.room_group_name,
        {
            'type':'chat_message',
            'message':f"{seconds} seconds passed after login!",
            'userId': "Server"
        }
    )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print(f'{str(datetime.now())} - Message received: ', text_data_json)
        
        msg_type = text_data_json['type']
        message = text_data_json['message']
        user_id = text_data_json['userId']
        if not self.user_id and not msg_type == 'server_message':
            self.user_id = user_id

        await (self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'userId': user_id
            }
        )

    async def chat_message(self, event):
        message = event['message']
        user_id = event['userId']

        await self.send(text_data=json.dumps({
            'type':'chat',
            'message':message,
            'userId': user_id
        }))

    async def server_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type':'chat',
            'message':message,
            'userId': "Server"
        }))
    
    async def disconnect(self, code=None):
        print(f'{str(datetime.now())} - {self.user_id} disconnecting!')

        await (self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'server_message',
                'message': f'{self.user_id} has disconnected!',
            }
        )
        await (self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        print(f"{str(datetime.now())} - Group <{self.room_group_name}> has {len(self.channel_layer.groups.get(self.room_group_name, {}).items())} connection(s)")
