import json
import pika
import django
import os
import sys
import time
from pika.exceptions import AMQPConnectionError
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()


def process_approval(ch, method, properties, body):
    data = json.loads(body)
    send_mail(
        "Your presentation has been accepted",
        f"{data['name']}, we're happy to tell you that your presentation {data['title']} has been accepted",
        "admin@conference.go",
        [{data["email"]}],
        fail_silently=False,
    )
    print("accepted")


def process_rejection(ch, method, properties, body):
    data = json.loads(body)
    send_mail(
        "Your presentation has been rejected",
        f"{data['name']}, we're happy to tell you that your presentation {data['title']} has been rejected",
        "admin@conference.go",
        [{data["email"]}],
        fail_silently=False,
    )
    print("\a")


while True:
    try:
        parameters = pika.ConnectionParameters(host="rabbitmq")
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue="presentation_approvals")
        channel.queue_declare(queue="presentation_rejections")

        channel.basic_consume(
            queue="presentation_approvals",
            on_message_callback=process_approval,
            auto_ack=True,
        )
        channel.basic_consume(
            queue="presentation_rejections",
            on_message_callback=process_rejection,
            auto_ack=True,
        )
        print(" [*] Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()
    except AMQPConnectionError:
        print("Could not connect to rabbitMQ")
        time.sleep(2.0)


# import json
# import pika
# import django
# import os
# import sys
# from django.core.mail import send_mail


# sys.path.append("")
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
# django.setup()


# def process_approval(ch, method, properties, body):
#     print("Received", body)
#     # send_mail(
#     #     "subject here",
#     #     "here is the message",
#     #     "from@example.com",
#     #     ["to@example.com"],
#     #     fail_silently=False,
#     # )


# parameters = pika.ConnectionParameters(host="rabbitmq")
# connection = pika.BlockingConnection(parameters)
# channel = connection.channel()
# channel.queue_declare(queue="presentation_approvals")
# channel.basic_consume(
#     queue="presentation_approvals",
#     on_message_callback=process_approval,
#     auto_ack=True,
# )
# channel.start_consuming()


# def process_rejection(ch, method, properties, body):
#     print("Received", body)
#     # send_mail(
#     #     "subject here",
#     #     "here is the message",
#     #     "from@example.com",
#     #     ["to@example.com"],
#     #     fail_silently=False,
#     # )


# parameters = pika.ConnectionParameters(host="rabbitmq")
# connection = pika.BlockingConnection(parameters)
# channel = connection.channel()
# channel.queue_declare(queue="presentation_rejection")
# channel.basic_consume(
#     queue="presentation_rejection",
#     on_message_callback=process_approval,
#     auto_ack=True,
# )
# channel.start_consuming()
