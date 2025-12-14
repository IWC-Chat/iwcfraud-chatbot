from flask import Flask, request, jsonify, render_template_string
import re
from datetime import datetime

app = Flask(__name__)

ANGER_KEYWORDS = ['angry', 'mad', 'furious', 'betrayed', 'hate', 'scam', 'lied']
DISTRESS_KEYWORDS = ['sad', 'worried', 'anxious', 'scared', 'shame', 'depressed', 'cry']

SERVICES = {
    'kit': 'Defense Resource Kit - $50: Evidence playbook & affidavit templates.',
    'soft': 'Soft Package - $75: Gentle guidance & emotional support tools.',
    'hard': 'Hard Package - $125: Aggressive evidence strategy & action plan.'
}

def profile_user(message):
    msg = message.lower()
    if any(kw in msg for kw in ANGER_KEYWORDS):
        return 'angry', 'assertive'
    elif any(kw in msg for kw in DISTRESS_KEYWORDS):
        return 'distressed', 'empathetic'
    return 'neutral', 'standard'

def get_style(style):
    styles = {
        'empathetic': {
            'greeting': "I'm really sorry you're going through this.",
            'empathy': "Your feelings are completely valid.",
            'cta': "Share more whenever you're ready."
        },
        'assertive': {
            'greeting': "I hear your anger—this shouldn't have happened.",
            'empathy': "Let's turn that into strong evidence.",
            'cta': "Tell me details when ready to fight back."
        },
        'standard': {
            'greeting': "Hey, I'm Winston with Integrity Wins.",
            'empathy': "Many face K-1 fraud; you're not alone.",
            'cta': "Share what happened—I'm listening."
        }
    }
    return styles.get(style, styles['standard'])

def present_services(archetype):
    if archetype == 'angry':
        return SERVICES['hard'] + "\n" + SERVICES['kit']
    elif archetype == 'distressed':
        return SERVICES['soft'] + "\nIntake is free first."
    return "Free intake first. Later:\n" + "\n".join(SERVICES.values())

def handle_objection(message):
    msg = message.lower()
    if 'cost' in msg or 'money' in msg:
        return "Intake is free. Pay only if you choose services later."
    if 'trust' in msg:
        return "We start with facts only—no pressure."
    return "I understand. Tell me more when ready."

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Winston - Integrity Wins</title>
    <style>
        body { background: #0a0a0a; color: #fff; font-family: Arial; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        #chat { width: 90%; max-width: 600px; height: 80vh; background: #111; border-radius: 10px; display: flex; flex-direction: column; }
        #messages { flex: 1; padding: 20px; overflow-y: auto; }
        #input-area { display: flex; padding: 10px; }
        input { flex: 1; padding: 10px; background: #222; border: none; color: #fff; border-radius: 5px; }
        button { padding: 10px; background: #008080; color: #fff; border: none; margin-left: 10px; border-radius: 5px; }
        .bot { color: #C0C0C0; }
        .user { text-align: right; color: #fff; }
    </style>
</head>
<body>
    <div id="chat">
        <div id="messages">
            <div class="bot">Hey, I'm Winston. Whenever you're ready—just talk.</div>
        </div>
        <div id="input-area">
            <input type="text" id="userInput" placeholder="Type here...">
            <button onclick="send()">Send</button>
        </div>
    </div>
    <script>
        function send() {
            let input = document.getElementById('userInput');
            let msg = input.value.trim();
            if (!msg) return;
            addMessage(msg, 'user');
            fetch('/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({msg: msg}) })
                .then(r => r.json()).then(data => addMessage(data.reply, 'bot'));
            input.value = '';
        }
        function addMessage(text, sender) {
            let div = document.createElement('div');
            div.className = sender;
            div.textContent = text;
            document.getElementById('messages').appendChild(div);
            div.scrollIntoView();
        }
        document.getElementById('userInput').addEventListener('keypress', e => { if (e.key === 'Enter') send(); });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('msg', '')
    archetype, style = profile_user(user_msg)
    responses = get_style(style)
    
    reply = responses['greeting']
    
    if any(word in user_msg.lower() for word in ['package', 'service', 'buy', 'cost']):
        reply += "\n\n" + present_services(archetype)
    
    if any(word in user_msg.lower() for word in ['but', 'however', 'no', 'doubt']):
        reply += "\n\n" + handle_objection(user_msg)
    
    reply += f"\n\n{responses['empathy']}\n{responses['cta']}"
    
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run()
