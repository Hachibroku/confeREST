import json
from django.http import JsonResponse
from .models import Presentation
from events.models import Conference
from common.json import ModelEncoder
from events.api_views import ConferenceListEncoder
from django.views.decorators.http import require_http_methods
import pika


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "title",
        "presenter_name",
        "company_name",
        "status",
    ]

    def get_extra_data(self, o):
        return {"status": o.status.name}


class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
        "conference",
        "status",
    ]
    encoders = {
        "conference": ConferenceListEncoder(),
    }

    def get_extra_data(self, o):
        return {"status": o.status.name}


@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):
    if request.method == "GET":
        presentations = Presentation.objects.all()
        return JsonResponse(
            {"presentations": presentations},
            encoder=PresentationListEncoder,
        )
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )
        presentation = Presentation.create(**content)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_presentation(request, id):
    if request.method == "GET":
        presentation = Presentation.objects.get(id=id)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "presentation" in content:
                presentation = Presentation.objects.get(
                    id=content["presentation"]
                )
                content["presentation"] = presentation
        except Presentation.DoesNotExist:
            return JsonResponse({"message": "Invalid presentation ID"})
        Presentation.objects.filter(id=id).update(**content)
        presentation = Presentation.objects.get(id=id)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


def send_message_to_queue(queue_name, message):
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=message,
    )
    connection.close()


@require_http_methods(["PUT"])
def api_approve_presentation(request, id):
    presentation = Presentation.objects.get(id=id)
    presentation.approve()
    message = {
        "name": presentation.presenter_name,
        "email": presentation.presenter_email,
        "title": presentation.title,
        "queue_name": "presentation_approvals",
    }
    message_json = json.dumps(message)
    send_message_to_queue(message["queue_name"], message_json)
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )


@require_http_methods(["PUT"])
def api_reject_presentation(request, id):
    presentation = Presentation.objects.get(id=id)
    presentation.reject()
    message = {
        "name": presentation.presenter_name,
        "email": presentation.presenter_email,
        "title": presentation.title,
        "queue_name": "presentation_rejections",
    }
    message_json = json.dumps(message)
    send_message_to_queue(message["queue_name"], message_json)
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )
