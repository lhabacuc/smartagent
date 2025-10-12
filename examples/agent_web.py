from flask import Flask, request, jsonify, render_template_string
from agent import Agent

app = Flask(__name__)
agent = Agent(model="groq", enable_history=True, history_limit=5)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>SmartAgent Web Chat</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .chatbox { width: 100%; max-width: 600px; margin: auto; }
        .msg { margin-bottom: 10px; }
        .user { color: #0074D9; }
        .agent { color: #2ECC40; }
    </style>
</head>
<body>
    <div class="chatbox">
        <h2>SmartAgent Web Chat</h2>
        <form method="post">
            <input type="text" name="user_input" autofocus required style="width:80%">
            <button type="submit">Enviar</button>
        </form>
        <div>
            {% for m in history %}
                <div class="msg"><span class="user">Você:</span> {{m['user_prompt']}}<br><span class="agent">Agente:</span> {{m['final_response']}}</div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.form.get('user_input', '')
        if user_input:
            agent.chat(user_input)
    history = agent.get_history()
    return render_template_string(HTML, history=history)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    user_input = data.get('user_input', '')
    resposta = agent.chat(user_input)
    return jsonify({
        'user_input': user_input,
        'response': resposta,
        'history': agent.get_history()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5070)
