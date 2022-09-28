import uvicorn
from backend.src.api import create_app

from backend.ova import OpenVoiceAssistant

if __name__ == '__main__':
    ova = OpenVoiceAssistant()

    app = create_app(ova)
    uvicorn.run(app, host='127.0.0.1', port=5001)
    print("running")