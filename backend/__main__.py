import uvicorn
from backend.src.api import create_app

from backend.ova import OpenVoiceAssistant

if __name__ == '__main__':
    ova = OpenVoiceAssistant()

    app = create_app(ova)
    uvicorn.run(app, host='0.0.0.0', port=5010)
    print("running")