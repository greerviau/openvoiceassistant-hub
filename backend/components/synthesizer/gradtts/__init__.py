import json
import os
import datetime as dt
import numpy as np
import torch
import typing

from backend.config import Configuration

from .grad_tts import params as params
from .grad_tts.model import GradTTS
from .grad_tts.text import text_to_sequence, cmudict
from .grad_tts.text.symbols import symbols
from .grad_tts.utils import intersperse

from .grad_tts.hifi_gan.env import AttrDict
from .grad_tts.hifi_gan.models import Generator as HiFiGAN

HIFI_CONFIG = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'grad_tts/resources/hifigan-config.json')
CMU_DICT = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'grad_tts/resources/cmu_dictionary')

class Gradtts:
    def __init__(self, use_cuda: bool, model_file: str, hifi_model: str):
        self.cuda_available = torch.cuda.is_available()
        self.CUDA = use_cuda and self.cuda_available

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
            self.vocoder.load_state_dict(torch.load(hifi_model)['generator'])
        else:
            self.vocoder.load_state_dict(torch.load(hifi_model, map_location='cpu')['generator'])
        self.vocoder.eval()
        self.vocoder.remove_weight_norm()

        self.cmu = cmudict.CMUDict(CMU_DICT)

    def synthesize(self, text: str, file_path: str):
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
            return audio.tobytes(), 22050, audio.dtype.itemsize

def build_engine(config: Configuration) -> GradTTS:
    use_cuda = config.get('components', 'synthesizer', 'config', 'use_cuda')
    model_file = config.get('components', 'synthesizer', 'config', 'model_file')
    hifi_model_file = config.get('components', 'synthesizer', 'config', 'hifi_model_file')
    return Gradtts(use_cuda, model_file, hifi_model_file)

def default_config() -> typing.Dict:
    return {
        "use_cuda": False,
        "model_file": "",
        "hifi_model_file": ""
    }