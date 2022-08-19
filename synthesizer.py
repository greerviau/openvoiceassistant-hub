import json
import datetime as dt
import numpy as np

import torch

from scipy.io.wavfile import write

import grad_tts.params as params
from grad_tts.model import GradTTS
from grad_tts.text import text_to_sequence, cmudict
from grad_tts.text.symbols import symbols
from grad_tts.utils import intersperse

from grad_tts.hifi_gan.env import AttrDict
from grad_tts.hifi_gan.models import Generator as HiFiGAN


HIFIGAN_CONFIG = './grad_tts/checkpts/hifigan-config.json'
HIFIGAN_CHECKPT = './grad_tts/checkpts/hifigan.pt'
GRADTTS_CHECKPT = './grad_tts/checkpts/grad_2250.pt'

CUDA = torch.cuda.is_available()

class Synthesizer:
    def __init__(self):
        self.timesteps = 10
    
        print('Initializing Grad-TTS...')
        self.generator = GradTTS(len(symbols)+1, params.n_spks, params.spk_emb_dim,
                            params.n_enc_channels, params.filter_channels,
                            params.filter_channels_dp, params.n_heads, params.n_enc_layers,
                            params.enc_kernel, params.enc_dropout, params.window_size,
                            params.n_feats, params.dec_dim, params.beta_min, params.beta_max, params.pe_scale)

        if CUDA:
            self.generator = self.generator.cuda()
            self.generator.load_state_dict(torch.load(GRADTTS_CHECKPT))
        else:
            self.generator.load_state_dict(torch.load(GRADTTS_CHECKPT, map_location='cpu'))

        self.generator.eval()

        print(f'Number of parameters: {self.generator.nparams}')

        print('Initializing HiFi-GAN...')
        with open(HIFIGAN_CONFIG) as f:
            h = AttrDict(json.load(f))
        self.vocoder = HiFiGAN(h)
        if CUDA:
            self.vocoder = self.vocoder.cuda()
            self.vocoder.load_state_dict(torch.load(HIFIGAN_CHECKPT)['generator'])
        else:
            self.vocoder.load_state_dict(torch.load(HIFIGAN_CHECKPT, map_location='cpu')['generator'])
        self.vocoder.eval()
        self.vocoder.remove_weight_norm()

        self.cmu = cmudict.CMUDict('./grad_tts/resources/cmu_dictionary')

    def synthesize_text(self, text):
        with torch.no_grad():
            seq = text_to_sequence(text, dictionary=self.cmu)
            x = torch.LongTensor(intersperse(seq, len(symbols)))
            if CUDA:
                x = x.cuda()
            x = x[None]
            x_lengths = torch.LongTensor([x.shape[-1]])
            if CUDA:
                x_lengths = x_lengths.cuda()
            
            t = dt.datetime.now()
            y_enc, y_dec, attn = self.generator.forward(x, x_lengths, n_timesteps=self.timesteps, temperature=1.5,
                                                    stoc=False, spk=None, length_scale=0.91)
            t = (dt.datetime.now() - t).total_seconds()
            #print(f'Grad-TTS RTF: {t * 22050 / (y_dec.shape[-1] * 256)}')

            audio = (self.vocoder.forward(y_dec).cpu().squeeze().clamp(-1, 1).numpy() * 32768).astype(np.int16)

            #write(f'./output.wav', 22050, audio)
            return audio