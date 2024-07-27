from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import openai
import logging

app = Flask(__name__)

# Configure your OpenAI and Twilio API keys
openai.api_key = 'sk-proj-iN5jkIi8PJtpBVW4FCv2T3BlbkFJBOz41MdzodfHftcGfrMK'
twilio_account_sid = 'AC97e5af858083f89b0b4fad2fa8142821'
twilio_auth_token = 'ffdf5007e4d28f7d53f3e3c00a4b3f41'

client = Client(twilio_account_sid, twilio_auth_token)

# Configure logging
logging.basicConfig(filename='call_interactions.log', level=logging.INFO)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Respond to incoming phone calls with a simple text-to-speech message."""
    resp = VoiceResponse()
    gather = Gather(input='speech', action='/gather', method='POST')
    gather.say('Hello, you are speaking with the AI agent. How can I assist you today?')
    resp.append(gather)
    resp.redirect('/voice')

    return str(resp)

@app.route("/gather", methods=['POST'])
def gather():
    """Process the gathered input from the user."""
    speech_result = request.form['SpeechResult']
    logging.info(f"User said: {speech_result}")

    # Generate a response using OpenAI
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"User: {speech_result}\nAI:",
        max_tokens=150
    )

    ai_response = response.choices[0].text.strip()
    logging.info(f"AI responded: {ai_response}")

    resp = VoiceResponse()
    resp.say(ai_response)
    resp.hangup()

    return str(resp)

@app.route("/make_call", methods=['POST'])
def make_call():
    """Make an outbound call and interact with the client."""
    to_number = request.form['to']
    from_number = '18778406471'

    call = client.calls.create(
        to=to_number,
        from_=from_number,
        url="https://api.openai.com/v1/audio/speech"
    )

    return jsonify({"message": "Call initiated", "sid": call.sid})

if __name__ == "__main__":
    app.run(debug=True)
