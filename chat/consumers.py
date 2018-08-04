__author__ = 'lm'
from channels.consumer import AsyncConsumer
import json
import asyncio
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import Thread, ChatMessage


class ChatConsumer(AsyncConsumer):
    @asyncio.coroutine
    def websocket_connect(self, event):
        print("connected", event)
        yield from self.send({
            "type": "websocket.accept",
        })
        other_user = self.scope['url_route']['kwargs']['username']
        me = self.scope['user']

        thread_obj = yield from self.get_thread(me, other_user)
        print(me, thread_obj.id)
        chat_room = f'thread_{thread_obj.id}'
        self.chat_room = chat_room
        yield from self.channel_layer.group_add(chat_room, self.channel_name)
        # yield from self.send({
        #     'type': 'websocket.accept'
        # })
        # yield from asyncio.sleep(10)

    @asyncio.coroutine
    def websocket_receive(self, event):
        print("received", event)
        front_text = event.get('text', None)
        if front_text is not None:
            loaded_dic_data = json.loads(front_text)
            msg = loaded_dic_data.get("message")
            type = loaded_dic_data.get("type", "chat")
            print(msg)
            user = self.scope['user']
            username = 'default'
            if user.is_authenticated:
                username = user.username
            print(username + " Now")
            myResponse = {
                'message': msg,
                'username': username,
                'type': type,
            }
            #broadcast the message
            yield from self.channel_layer.group_send(
                self.chat_room,
                {
                    "type": "chat_message",
                    "text": json.dumps(myResponse)
                }
            )

    @asyncio.coroutine
    def chat_message(self, event):
        #send the actual message
        yield from self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    @asyncio.coroutine
    def websocket_disconnect(self, event):
        print("disconnected", event)

    @database_sync_to_async
    def get_thread(self, user, other_user):
        return Thread.objects.get_or_new(user, other_user)[0]