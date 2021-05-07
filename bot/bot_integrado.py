
from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
from pandas import DataFrame, read_csv
from csv import writer

i = {"time": datetime.now(), "number": "000000", "type":"none"}
interactions = DataFrame(i, index=[0])
app = Flask(__name__)

c = [{"nombre": "Roberto Cadena Vega", "numero": "whatsapp:+5215527154000"},
     {"nombre": "Carlos Macias Martinez", "numero": "whatsapp:+5215554745318"}]
clientes = DataFrame(c)

@app.route('/bot', methods=['POST'])
def bot():
    global interactions, clientes
    incoming_msg = request.values.get('Body', '').lower()
    incoming_num = request.values.get("From", "")
    incoming_time = datetime.now()

    resp = MessagingResponse()
    msg = resp.message()
    responded = False

    last_interactions = interactions[interactions["number"]==incoming_num]
    last_interactions = last_interactions.sort_values(by="time", ascending=False)
    last_interactions = last_interactions.reset_index(drop=True)

    if len(last_interactions) > 0:
        last_int = last_interactions["type"][0]
    else:
        last_int = "none"

    if last_int == "hola":
        if "1" in incoming_msg:
            cliente = clientes[clientes["numero"]==incoming_num]
            cliente = cliente.reset_index(drop = True)
            if len(cliente) > 0:
                nom_cliente = cliente["nombre"][0].split(" ")[0]
                message  = f"Hola, {nom_cliente} en que horario deseas tu cita:\n"

                citas = read_csv(r"C:\Users\Telecomm\Desktop\version_control\citas_db.csv", usecols= ["fecha","hora", "paciente"]).fillna(" ")
                citas = citas[:-1]
                citas_disponibles = citas[citas["paciente"] == " "]["hora"]

                for i, hora in enumerate(citas_disponibles):
                    message += str(i+1) + " - " + hora +"\n"
                    print (message)

                msg.body(message)
                responded = True
                inter = {"time": incoming_time, "number": incoming_num, "type":"c1"}
                interactions = interactions.append(inter, ignore_index=True)

            else:
                message = "¿Me podrías proporcionar tu nombre completo?"
                msg.body(message)
                responded = True
                inter = {"time": incoming_time, "number": incoming_num, "type":"c2"}
                interactions = interactions.append(inter, ignore_index=True)

        else:
            message = "En breve se comunicara contigo un asistente."
            msg.body(message)
            responded = True
            inter = {"time": incoming_time, "number": incoming_num, "type":"asis"}
            interactions = interactions.append(inter, ignore_index=True)

    elif last_int == "c2":
        c = {"nombre": incoming_msg, "numero": incoming_num}
        clientes = clientes.append(c, ignore_index=True)

        cliente = clientes[clientes["numero"]==incoming_num]
        cliente = cliente.reset_index(drop = True)
        print(cliente)
        nom_cliente = cliente["nombre"][0].split(" ")[0]

        message  = f"Hola, {nom_cliente} en que horario deseas tu cita:\n"

        citas = read_csv(r"C:\Users\Telecomm\Desktop\version_control\citas_db.csv", usecols= ["fecha","hora", "paciente"]).fillna(" ")
        citas = citas[:-1]
        citas_disponibles = citas[citas["paciente"] == " "]["hora"]

        for i, hora in enumerate(citas_disponibles):
            message += str(i+1) + " - " + hora +"\n"

        msg.body(message)
        responded = True
        inter = {"time": incoming_time, "number": incoming_num, "type":"c1"}
        interactions = interactions.append(inter, ignore_index=True)

    elif last_int == "c1":
        cliente = clientes[clientes["numero"]==incoming_num]
        cliente = cliente.reset_index(drop = True)
        nom_cliente = cliente["nombre"][0].split(" ")[0]

        cita = read_csv(r"C:\Users\Telecomm\Desktop\version_control\citas_db.csv", usecols= ["fecha","hora", "paciente"]).fillna(" ")
        cita = cita[:-1]
        citas_disponibles = cita[cita["paciente"] == " "]["hora"]

        hora_vacio = []
        for i, hora in enumerate(citas_disponibles):
             hora_disponible = {"indice": i+1, "hora": hora}
             hora_vacio.append(hora_disponible)

        horas_posibles = DataFrame(hora_vacio)
        horas_posibles = horas_posibles[horas_posibles["indice"] == int(incoming_msg)]
        horas_posibles = horas_posibles.reset_index(drop = True)
        hora_agendada = horas_posibles["hora"][0]

        message  = f"De acuerdo {nom_cliente}, agendamos tu cita a las {hora_agendada}"
        msg.body(message)
        responded = True

        inter = {"time": incoming_time, "number": incoming_num, "type":"c3"}
        interactions = interactions.append(inter, ignore_index=True)

        datos_cita = [nom_cliente, incoming_num]
        with open(r"C:\Users\Telecomm\Desktop\version_control\agenda.csv", "w", newline= "") as agenda:

            nueva_cita = writer(agenda)
            nueva_cita.writerow(datos_cita)
            agenda.close()

        incoming_msg_index = int(incoming_msg)-1
        db_cita = read_csv(r"C:\Users\Telecomm\Desktop\version_control\citas_db.csv", usecols=["fecha", "hora", "paciente"]).fillna(" ")
        db_cita_temp = db_cita[db_cita["paciente"] == " "].reset_index(drop = True)
        db_cita_hora =db_cita_temp["hora"][incoming_msg_index]
        index = db_cita[db_cita["hora"] == db_cita_hora].index[0]
        db_cita["paciente"][index] = nom_cliente
        db_cita = db_cita.reset_index(drop = True)
        db_cita.to_csv(r"C:\Users\Telecomm\Desktop\version_control\citas_db.csv", index = False)


    else:
        message  = "Hola, ¿En que podemos ayudarte?\n"
        message += "1 - Agendar cita\n"
        message += "2 - Solicitar atencion humana"
        msg.body(message)
        responded = True
        inter = {"time": incoming_time, "number": incoming_num, "type":"hola"}
        interactions = interactions.append(inter, ignore_index=True)

    print(resp)
    return str(resp)


if __name__ == '__main__':
    app.run()
