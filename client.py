import socketio
import time

# Initialize a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print('Connected to server')

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.event
def broadcast_data(data):
    print('Received broadcast data:', data)

def main():
    # Connect to the Flask Socket.IO server
    sio.connect('http://localhost:5050')

    try:
        # Send data to the server
        while True:
            data = {'message': 'Hello from Python client'}
            sio.emit('send_data', data)
            print('Data sent:', data)
            time.sleep(5)  # Send data every 5 seconds

    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C
        print('Client shutting down...')
    finally:
        sio.disconnect()

if __name__ == '__main__':
    main()
