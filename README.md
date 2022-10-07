# openvoiceassistant-hub
HUB for openvoiceassistant (duh)

Open Voice Assistant is a fully offline and completely customizable voice assistant.

# Deployment
Deploy on a single server on your LAN. OVA-hub can be deployed on anything from a Raspberry Pi, to an Ubuntu server.

To utilize some of the more advanced features, deploy on a GPU capable machine with CUDA support.

# Design
OVA-hub recieves a request from an OVA-node, containing speech data, and runs a pipeline to possibly perform an action and return a response.

**Audio -> Transcription -> Understanding -> Action -> Response -> Synthesis**

Actions performed and associated responses are dependant on skills that you can customize. (Eg. getting the weather report, controlling IOT devices, etc.)

Responses from OVA-hub are synthesized into speech audio and returned to the OVA-node.

Every aspect of the pipeline is customizable, including:
* Algorithm for audio transcription
* Skills to perform
* Method of voice synthesis

## Audio Transcription Algorithms
* Vosk (Kaldi Recognizer)
* (TODO) Wave2Vec
* (TODO) OpenAI Whisper

## Voice Synthesis
* espeak (default)
* GradTTS

