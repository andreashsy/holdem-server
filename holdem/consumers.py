import json
import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

from .models.Game import HoldemGameState
from .models.Player import HoldemPlayer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'test'
        self.user_id = None

        await (self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        if not cache.get('player_waiting_room'):
            player_waiting_room = []
            cache.set('player_waiting_room', player_waiting_room)
        else:
            waiting_room_list = cache.get('player_waiting_room')
            await self.send_waiting_room_update(message=", ".join(waiting_room_list))

        print(f"{str(datetime.now())} - Group {self.room_group_name} has {len(self.channel_layer.groups.get(self.room_group_name, {}).items())} connection(s)")
    #     asyncio.create_task(self.wait_and_send_msg(3))

    # async def wait_and_send_msg(self, seconds: int):
    #     await asyncio.sleep(seconds)

    #     await (self.channel_layer.group_send)(
    #     self.room_group_name,
    #     {
    #         'type':'server_message',
    #         'message':f"{seconds} seconds passed after login!",
    #     }
    # )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print(f'{str(datetime.now())} - Message received: ', text_data_json)
        
        msg_type = text_data_json['type']
        message = text_data_json['message']
        user_id = text_data_json['userId']
        
        if not self.user_id and not msg_type == 'server_message':
            self.user_id = user_id
        
        if msg_type == 'player_join':
            await self.handle_player_join(user_id)

        elif msg_type == 'player_leave':
            await self.handle_player_leave(user_id)

        elif msg_type == 'start_game':
            await self.handle_start_game()
            
        else:
            await self.send_chat_message(user_id, message)

    async def handle_player_join(self, user_id:str):
        waiting_room_list = cache.get('player_waiting_room')
        if user_id in waiting_room_list:
            await self.send_server_message(message=user_id + ' is already in the room!')
            return

        waiting_room_list.append(user_id)
        cache.set('player_waiting_room', waiting_room_list)
        await self.send_waiting_room_update(message=", ".join(waiting_room_list))

    async def handle_player_leave(self, user_id:str):
        waiting_room_list = cache.get('player_waiting_room')
        if not user_id in waiting_room_list:
            await self.send_server_message(message=user_id + ' is not in the room!')
            return

        waiting_room_list.remove(user_id)
        cache.set('player_waiting_room', waiting_room_list)
        await self.send_waiting_room_update(message=", ".join(waiting_room_list))

    async def handle_start_game(self):
        waiting_room_list = cache.get('player_waiting_room')
        if len(waiting_room_list) < 2:
            # not enough players
            return
        if cache.get('holdem_game'):
            # already a game in progress
            return
        cache.set('player_waiting_room', [])

        # update waiting list
        await self.send_waiting_room_update(message="Game has started")
        
        # start game
        players = [HoldemPlayer(stack=100, id=player_id) for player_id in waiting_room_list]
        holdem_game = HoldemGameState(players=players)
        for player in holdem_game.players:
            player.participate()
        holdem_game.start_preflop()
        cache.set('holdem_game', holdem_game)

    async def send_chat_message(self, user_id:str, message:str):
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

    async def send_waiting_room_update(self, message:str):
        await (self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'waiting_room_update',
                'message': message,
                'userId': 'Server'
            }
        )

    async def waiting_room_update(self, event):
        user_id = event['userId']
        message = event['message']

        await self.send(text_data=json.dumps({
            'type':'waiting_room_update',
            'message': message,
            'userId': user_id
        }))

    async def send_server_message(self, message):
        await (self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'server_message',
                'message':message,
        })

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
