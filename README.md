# openvoiceassistant-hub
HUB for openvoiceassistant

Open Voice Assistant is a fully offline, locally hosted and completely customizable Voice Assistant.

# Deployment
Deploy on a single server on your LAN. OVA-hub can be deployed on anything from a Raspberry Pi, to an Ubuntu server.

To utilize some of the more advanced AI features, deploy on a GPU capable machine with CUDA support.

## Installation
```
git clone https://github.com/greerviau/openvoiceassistant-hub.git
cd openvoiceassistant-hub
./scripts/install.sh
```

The installation will automatically create system services for the front and backend applications.

## Frontend (WIP)
Navigate to ```localhost:3000``` or ```<ova-server-ip>:3000``` in a web browser to access the frontend UI

From here you can configure OVA nodes, add and configure skills, edit general configuration, view logs and debug information, etc.

OVA nodes on your local network should auto discover the HUB on your LAN and automatically sync. Once synced their information will be available from here where you can configure them to your needs, control remotely, view debug logs, etc.

## REST API
Navigate to ```localhost:5010/docs``` or ```<ova-server-ip>:5010/docs``` to access the swagger UI for the REST API.

# Skills
Skills are available out of the box, no programming required, simply import them from the frontend UI and configure them appropriatley.

Check out a [list of all the skills](https://github.com/greerviau/openvoiceassistant-hub/blob/develop/backend/skills/README.md) openvoiceassistant has to offer!

If you want to write your own skills, follow the documentation in ```backend/skills/README.md``` for a guideline. 

Users are encouraged to create their own skills and contribute them so others may use them!

# Design
OVA-hub recieves a HTTP request from an OVA-node containing speech data plus context information. The data is run through the inference pipeline like so:

**Audio -> Transcription -> Understanding -> Action -> Response -> Synthesis**

Actions performed and associated responses are dependant on skills that you can customize. (Ex. getting the weather report, controlling IOT devices, etc.)

Responses from OVA-hub are synthesized into speech audio and returned to the origin OVA-node along with metadata.

All of the algorithms in the pipeline are customizable, including:
* Voice Detection
* Audio Transcription
* Voice Synthesis

## Voice Detection
* Kaldi Phrase Detection

## Audio Transcription
* Kaldi (default)
* Whisper

## Voice Synthesis
* Espeak (default)
* GradTTS
* Coqui TTS

## v0.1.0
- [ ] Logging system
- [x] Weather skill
- [x] Datetime skill
- [x] Homeassistant skill
- [ ] Optimize and improve inference speed
- [ ] Build frontend
