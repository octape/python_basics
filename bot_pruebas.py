from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from datetime import datetime, timedelta
import time
from pandas import DataFrame

def cita():
    now =datetime.now()
    horas = now.hour
    minutos = now.minute
    hora_cita = now + timedelta(minutes=30)

    agenda = [{"nombre":"octavio", "valor": datetime.strptime("2:39", "%H:%M").time()},
              {"nombre":"robert", "valor": datetime.strptime("2:40", "%H:%M").time()},
              {"nombre":"carlos", "valor": datetime.strptime("2:41", "%H:%M").time()}]

    df =DataFrame(agenda)
    df_1 = df[df["valor"] == hora_cita]
    df_2 = df_1["nombre"]
    df_2

#if (minutos+30) in df["valor"].tolist():
    if len(df_2) > 0:
        print(df_2 +" tienes una cita con nosotros a las:", hora_cita)

        return df_2[0], hora_cita

    else:
        return None

def noti_sender():

    elementos = cita()
    if elementos != None:
        nombre, hora_cita = elementos
        account_sid = 'AC5e68b93cd7a6d5b4e022edcb38da24f0'
        auth_token = 'a9f4fc0192cb049945b5bf085a39f9d9'
        client = Client(account_sid, auth_token)


        message = client.messages.create(from_='whatsapp:+14155238886', body= nombre + "* tu cita a las *" + hora_cita +
                                    "\n elige una opción: \n *1* Confirmar \n *2* Reagendar cita", to='whatsapp:+5215552974432')


        return message

def msg_sender():


    account_sid = 'AC5e68b93cd7a6d5b4e022edcb38da24f0'
    auth_token = 'a9f4fc0192cb049945b5bf085a39f9d9'
    client = Client(account_sid, auth_token)

    message = client.messages.create(from_='whatsapp:+14155238886',body= "en que te podemos ayudar\n elige una opción: \n 1 Agendar cita \n 2 Atencion de personal",
                                    to='whatsapp:+5215552974432')

    return message


notificacion = msg_sender()

if notificacion != "":

    app = Flask(__name__)

    @app.route('/bot_pruebas', methods=['POST'])

    def bot():
        incoming_msg = request.values.get('Body', '').lower()
        resp = MessagingResponse()
        msg = resp.message()
        responded = False

        if "menu" in incoming_msg:
            msg_sender()

        elif '1' in incoming_msg:
        # return a quote
            response = "aqui se desplegara el codigo del robert"
            msg.body(response)
            responded = True

        elif '2' in incoming_msg:
        # return a cat pic
            response = "En breve nos comunicaremos contigo"
            msg.body(response)
            responded = True

        else:
            response = "la opcion no es valida"
            msg.body(response)
            responded = True

        return str(resp)


if __name__ == '__main__':
    app.run()
