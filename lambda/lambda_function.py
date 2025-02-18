# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils
import requests
import json
import os
import time
from datetime import datetime
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
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={}".format(GOOGLE_API_KEY)

# Cabeçalhos para a requisição
headers = {
    'Content-Type': 'application/json',
}

# Tempo limite para resetar o histórico (24 horas em segundos)
RESET_TIME = 24 * 60 * 60  

def should_reset_history(session_attr):
    """Verifica se já passou 24 horas desde a última interação."""
    last_timestamp = session_attr.get("last_interaction_time", 0)
    current_time = time.time()

    # Se não houver histórico (primeira interação ou após reset)
    if last_timestamp == 0:
        session_attr["last_interaction_time"] = current_time
        return True  # Deverá resetar o histórico

    if current_time - last_timestamp >= RESET_TIME:
        session_attr["last_interaction_time"] = current_time  # Atualiza o tempo
        return True  # Deve resetar o histórico
    
    return False  # Mantém o histórico

def get_time_of_day():
    """Retorna uma saudação com base na hora do dia."""
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "Bom dia!"
    elif 12 <= current_hour < 18:
        return "Boa tarde!"
    else:
        return "Boa noite!"
        
def get_saudation(session_attr):
    if should_reset_history(session_attr):
        return "Você será minha assistente de I.A. Te darei comandos e iremos interagir conforme lhe orientar e treinar."
    else: 
        return get_time_of_day()


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes

        # Verificar se o histórico deve ser resetado
        if should_reset_history(session_attr):
            session_attr["conversation_data"] = {  
                "contents": [{
                    "role": "user",
                    "parts": [{
                        "text": get_saudation(session_attr)
                    }]
                }]
            }

        data = session_attr["conversation_data"]

        # Requisição para a API
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # Levanta uma exceção para status não 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            speak_output = "Houve um erro ao tentar se comunicar com o serviço. Tente novamente mais tarde."
            return handler_input.response_builder.speak(speak_output).response

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
            speak_output = "Erro na requisição"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class ChatIntentHandler(AbstractRequestHandler):
    """Handler para o Intent de Chat."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ChatIntent")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes

        # Verificar se o histórico deve ser resetado
        if should_reset_history(session_attr):
            session_attr["conversation_data"] = {"contents": []}

        data = session_attr["conversation_data"]
        query = handler_input.request_envelope.request.intent.slots["query"].value
        query_text = {
            "role": "user",
            "parts": [{
                "text": query
            }]
        }
        data["contents"].append(query_text)

        # Requisição para a API
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # Levanta uma exceção para status não 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            speak_output = "Houve um erro ao tentar se comunicar com o serviço. Tente novamente mais tarde."
            return handler_input.response_builder.speak(speak_output).response

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
            
            session_attr["conversation_data"] = data  
        else:
            speak_output = "Não obtive uma resposta para sua solicitação"
            logger.error(f"Erro na API: {response.status_code} - {response.text}")

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Alguma outra pergunta?")
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler para os Intents de Cancelamento e Parada."""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Valeu, tamo junto!" 

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Handler para capturar erros genéricos."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        speak_output = "Desculpe, houve um problema na solicitação. Por favor, tente novamente mais tarde."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# SkillBuilder - Roteador principal da Skill Alexa
sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ChatIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
