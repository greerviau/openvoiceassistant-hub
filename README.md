# openvoiceassistant-hub
HUB for openvoiceassistant (duh)

Open Voice Assistant is a fully offline and completely customizable Voice Assistant.

# Deployment
Deploy on a single server on your LAN. OVA-hub can be deployed on anything from a Raspberry Pi, to an Ubuntu server.

To utilize some of the more advanced features, deploy on a GPU capable machine with CUDA support.

# Design
OVA-hub recieves a request from an OVA-node containing speech data plus context information, and runs a pipeline to perform an action and return a response.

**Audio -> Transcription -> Understanding -> Action -> Response -> Synthesis**

Actions performed and associated responses are dependant on skills that you can customize. (Eg. getting the weather report, controlling IOT devices, etc.)

Responses from OVA-hub are synthesized into speech audio and returned to the OVA-node.

Every aspect of the pipeline is customizable, including:
* Algorithm for voice detection
* Algorithm for audio transcription
* Skills to perform
* Algorithm for voice synthesis

## Audio Transcription Algorithms
* Kaldi (default)
* Whisper

## Voice Synthesis Algorithms
* Espeak (default)
* GradTTS

## v0.1.0
- [ ] Logging system
- [ ] Weather skill
- [ ] Datetime skill
- [ ] Homeassistant skill
- [ ] Optimize and improve inference speed
