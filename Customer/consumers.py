from channels.generic.websocket import AsyncWebsocketConsumer
import json

class CustomerConsumer(AsyncWebsocketConsumer):

  async def connect(self):
    self.group_name = self.scope['url_route']['kwargs']['group_name']
    await self.channel_layer.group_add(self.group_name, self.channel_name)
    await self.accept()


  async def receive(self,  text_data=None, bytes_data=None):
    print('message: ', text_data)

  
  async def notify(self, event):
    await self.send(text_data=json.dumps(event['message']))


  async def disconnect(self, code):
    await self.channel_layer.group_discard(self.group_name, self.channel_name)