import json
import datetime as dt
import numpy as np
import pyttsx3

import torch

from scipy.io.wavfile import write

import services.synthesizer.grad_tts.params as params
from services.synthesizer.grad_tts.model import GradTTS
from services.synthesizer.grad_tts.text import text_to_sequence, cmudict
from services.synthesizer.grad_tts.text.symbols import symbols
from services.synthesizer.grad_tts.utils import intersperse

from services.synthesizer.grad_tts.hifi_gan.env import AttrDict
from services.synthesizer.grad_tts.hifi_gan.models import Generator as HiFiGAN

HIFI_MODEL_FILE = './services/synthesizer/grad_tts/checkpts/hifigan.pt'
HIFI_CONFIG = './services/synthesizer/grad_tts/checkpts/hifigan-config.json'
CMU_DICT = './services/synthesizer/grad_tts/resources/cmu_dictionary'

class Synthesizer:
    def __init__(self, use_ai, use_cuda, model_file):
        self.AI = use_ai
        self.cuda_available = torch.cuda.is_available()
        self.CUDA = use_cuda and self.cuda_available
        if self.AI:
            self.init_gradtts( model_file)
    
    def init_pyttsx(self):
        self.engine = pyttsx3.init()
    
    def init_gradtts(self, model_file):
        self.timesteps = 10
    
        print('Initializing Grad-TTS...')
        self.generator = GradTTS(len(symbols)+1, params.n_spks, params.spk_emb_dim,
                            params.n_enc_channels, params.filter_channels,
                            params.filter_channels_dp, params.n_heads, params.n_enc_layers,
                            params.enc_kernel, params.enc_dropout, params.window_size,
                            params.n_feats, params.dec_dim, params.beta_min, params.beta_max, params.pe_scale)

        if self.CUDA:
            self.generator = self.generator.cuda()
            self.generator.load_state_dict(torch.load(model_file))
        else:
            self.generator.load_state_dict(torch.load(model_file, map_location='cpu'))

        self.generator.eval()

        print(f'Number of parameters: {self.generator.nparams}')

        print('Initializing HiFi-GAN...')
        with open(HIFI_CONFIG) as f:
            h = AttrDict(json.load(f))
        self.vocoder = HiFiGAN(h)
        if self.CUDA:
            self.vocoder = self.vocoder.cuda()
            self.vocoder.load_state_dict(torch.load(HIFI_MODEL_FILE)['generator'])
        else:
            self.vocoder.load_state_dict(torch.load(HIFI_MODEL_FILE, map_location='cpu')['generator'])
        self.vocoder.eval()
        self.vocoder.remove_weight_norm()

        self.cmu = cmudict.CMUDict(CMU_DICT)

    def synth_with_ai(self, text):
         with torch.no_grad():
            seq = text_to_sequence(text, dictionary=self.cmu)
            x = torch.LongTensor(intersperse(seq, len(symbols)))
            if self.CUDA:
                x = x.cuda()
            x = x[None]
            x_lengths = torch.LongTensor([x.shape[-1]])
            if self.CUDA:
                x_lengths = x_lengths.cuda()
            
            t = dt.datetime.now()
            y_enc, y_dec, attn = self.generator.forward(x, x_lengths, n_timesteps=self.timesteps, temperature=1.5,
                                                    stoc=False, spk=None, length_scale=0.91)
            t = (dt.datetime.now() - t).total_seconds()
            #print(f'Grad-TTS RTF: {t * 22050 / (y_dec.shape[-1] * 256)}')

            audio = (self.vocoder.forward(y_dec).cpu().squeeze().clamp(-1, 1).numpy() * 32768).astype(np.int16)

            #write(f'./output.wav', 22050, audio)
            return audio

    def synth(self, text):
        self.save_to_file(text, 'response.wav')

    def synthesize_text(self, text):
        if self.AI:
            return self.synth_with_ai(text)
        else:
            return self.synth(text)