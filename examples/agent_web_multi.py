from flask import Flask, request, jsonify, render_template_string
from agent import Agent

app = Flask(__name__)

# Cria múltiplos agentes com diferentes modelos/contextos
agents = {
    'groq': Agent(model="groq", enable_history=True, history_limit=10),
    'openai': Agent(model="groq", enable_history=True, history_limit=10, info="Você é um agente OpenAI."),
    'gemini': Agent(model="groq", enable_history=True, history_limit=10, info="Você é um agente Gemini."),
}

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Agentes SmartAgent</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .chatbox { width: 100%; max-width: 700px; margin: auto; }
        .msg { margin-bottom: 10px; }
        .user { color: #0074D9; }
        .agent { color: #2ECC40; }
    </style>
</head>
<body>
    <div class="chatbox">
        <h2>Multi-Agentes SmartAgent</h2>
        <form method="post">
            <label for="agent">Escolha o agente:</label>
            <select name="agent" id="agent">
                {% for k in agents.keys() %}
                    <option value="{{k}}" {% if k == selected_agent %}selected{% endif %}>{{k}}</option>
                {% endfor %}
            </select>
            <input type="text" name="user_input" autofocus required style="width:60%">
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
    selected_agent = request.form.get('agent', 'groq') if request.method == 'POST' else 'groq'
    agent = agents.get(selected_agent, agents['groq'])
    if request.method == 'POST':
        user_input = request.form.get('user_input', '')
        if user_input:
            agent.chat(user_input)
    history = agent.get_history()
    return render_template_string(HTML, agents=agents, history=history, selected_agent=selected_agent)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    agent_name = data.get('agent', 'groq')
    user_input = data.get('user_input', '')
    agent = agents.get(agent_name, agents['groq'])
    resposta = agent.chat(user_input)
    return jsonify({
        'agent': agent_name,
        'user_input': user_input,
        'response': resposta,
        'history': agent.get_history()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5070)
