# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests
import json
import os
from dotenv import load_dotenv
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# URL do endpoint da API
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={}".format(GOOGLE_API_KEY)
# Cabeçalhos para a requisição
headers = {
    'Content-Type': 'application/json',
}
# Dados (payload) para serem enviados na requisição POST
data = {
    "contents": [{
        "role":"user",
        "parts": [{
            "text": ""
        }]
    }]
}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        data["contents"][0]["parts"][0]["text"] = "Você será minha assistente de I.A. Te daria comandos e iremos interagir conforme lhe orientar e treinar."
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            text = (response_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Texto não encontrado"))
            speak_output = text + " Como posso te ajudar?"
            response_text = {
                "role": "model",
                "parts": [{
                    "text": text
                }]
            }
            data["contents"].append(response_text)
        else:
            speak_output = "Erro na requsição"
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class ChatIntentHandler(AbstractRequestHandler):
    """Handler for Chat Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ChatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        query = handler_input.request_envelope.request.intent.slots["query"].value
        query_text = {
                "role": "user",
                "parts": [{
                    "text": query
                }]
            }
        data["contents"].append(query_text)
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            text = (response_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Texto não encontrado"))
            speak_output = text
            response_text = {
                "role": "model",
                "parts": [{
                    "text": text
                }]
            }
            data["contents"].append(response_text)
        else:
            speak_output = "Não obtive uma resposta para sua solicitação"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Alguma outra pergunta?")
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ChatIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
