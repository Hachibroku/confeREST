from datetime import datetime
import json
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import sys
import time


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendees_bc.settings")
django.setup()


from models import AccountVO


def update_AccountVO_object(ch, method, properties, body):
    content = json.loads(body)
    first_name = content["first_name"]
    last_name = content["last_name"]
    email = content["email"]
    is_active = content["is_active"]
    updated_string = content["updated"]
    updated = datetime.fromisoformat(updated_string)

    if is_active:
        obj, created = AccountVO.objects.update_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "is_active": is_active,
                "updated": updated,
            },
        )
    else:
        obj = AccountVO.objects.filter(email=email).first()
        if obj:
            obj.delete()

    while True:
        try:
            parameters = pika.ConnectionParameters(host="localhost")
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.exchange_declare(
                exchange="account_info", exchange_type="fanout"
            )
            result = channel.queue_declare(queue="", exclusive=True)
            queue_name = result.method.queue
            channel.queue_bind(exchange="account_info", queue=queue_name)
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=update_AccountVO_object,
                auto_ack=True,
            )
            channel.start_consuming()
        except AMQPConnectionError:
            print(
                "Could not connect to RabbitMQ. Trying again in a few seconds."
            )
            time.sleep(2)
