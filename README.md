# openvoiceassistant-hub
HUB for openvoiceassistant

Open Voice Assistant is a fully offline, locally hosted and completely customizable Voice Assistant.

# Deployment
Deploy on a single server on your LAN. OVA-hub can be deployed on anything from a Raspberry Pi, to an Ubuntu server.

To utilize some of the more advanced AI features, deploy on a GPU capable machine with CUDA support.

## Installation
openvoiceassistant-hub is tested on Ubuntu 20.04 with **python >= 3.11**

```
sudo apt install -y git && \
git clone -b release https://github.com/greerviau/openvoiceassistant-hub.git && \
cd openvoiceassistant-hub && \
sudo ./scripts/install.sh
```

The installation will automatically create a systemd service to host everything.

## Frontend
Navigate to ```<ova_hub_ip>:7123``` in a web browser to access the frontend UI

From here you can configure OVA nodes, add and configure skills, edit general configuration, view logs and debug information, etc.

OVA nodes on your local network should auto discover the HUB on your LAN and automatically sync. Once synced their information will be available from here where you can configure them to your needs, control remotely, view debug logs, etc.

## REST API
Navigate to ```<ova_hub_ip>:7123/docs``` to access the swagger UI for the REST API.

# Integrations
Integrations are an augmentation for skills that might need similar capabilities. Ex. Home Assistant api that multiple skills need to utilize

Check out the [list of available integrations](core/integrations)

If you want to write your own integration, follow the [documentation](core/integrations/README.md#writing-a-custom-integration) for a guideline. 

# Skills
Skills are available out of the box, no programming required. Simply import them from the frontend UI and configure them appropriatley.

Check out the [list of available skills](core/skills) openvoiceassistant has to offer!

If you want to write your own skills, follow the [documentation](core/skills/README.md#writing-a-custom-skill) for a guideline. 

Users are encouraged to create their own skills and contribute them so others may use them!

# Design
OVA-hub recieves a HTTP request from an OVA-node containing speech data plus context information. The data is run through the inference pipeline like so:

**Audio -> Transcription -> Understanding -> Action -> Response -> Synthesis**

Actions performed and associated responses are dependant on skills that you can customize. (Ex. getting the weather report, controlling IOT devices, etc.)

Responses from OVA-hub are synthesized into speech audio and returned to the origin OVA-node along with metadata.

All of the algorithms in the pipeline are customizable, including:

## Audio Transcription
* Kaldi (default)
* Whisper

## Understanding
* Rapidfuzz (default)
* Neural Intent

## Voice Synthesis
* Espeak (default)
* Piper TTS

# [Release Notes](RELEASES.md)