from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

@app.route('/')
def index():
    return 'WebSocket Server is Running'

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('response', {'message': 'Connected to server'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('send_data')
def handle_message(data):
    print('Received data:', data)
    emit('broadcast_data', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, port=5050, debug=True)