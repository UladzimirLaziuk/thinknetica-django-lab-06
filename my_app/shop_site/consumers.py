import datetime
import json

from asgiref.sync import sync_to_async
from channels.consumer import AsyncConsumer
from shop_site.models import Ad



class EchoConsumerAsync(AsyncConsumer):

    async def websocket_connect(self, event):
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        text_data_json = json.loads(event['text'])
        message = text_data_json["message"]
        datetime_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ads_title, index = await query_asinc(message)
        text_data = json.dumps({
            'message': ads_title,
            'index': index,
            'time_massage': datetime_str,
        })
        await self.send({
            "type": "websocket.send",
            "text": text_data,
        })


@sync_to_async
def query_asinc(data_message):
    queryset = Ad.objects.filter(title__icontains=data_message).values_list('title', 'id')
    if not queryset:
        return None, None
    ads_title, index = list(queryset)[0]
    return ads_title, index
