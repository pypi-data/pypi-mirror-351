"""

simply inference script of ModelScope clear voice

"""

import os

import torch
from .clearvoice.clearvoice import ClearVoice
from loguru import logger
from pydub import AudioSegment
import numpy as np
from ..utils import save_np_float32_to_wav_file, normalize_audio_to_target
from .effects.phone import add_phone_effect, dephone_effect, advanced_dephone_effect


class SpeechEnhance:
    def __init__(self, model_type="MossFormerGAN_SE_16K") -> None:

        model_link = "https://huggingface.co/alibabasglab/MossFormer2_SE_48K/resolve/main/last_best_checkpoint.pt"

        # or MossFormerGAN_SE_16K
        # 48k for enhancement is ok.
        # MossFormerGAN_SE_16K
        availiable_models = ["MossFormerGAN_SE_16K", "MossFormer2_SE_48K"]
        self.model_type = model_type
        if model_type not in availiable_models:
            logger.error(f"{model_type} not in availiable_models: {availiable_models}")

        self.model = ClearVoice(task="speech_enhancement", model_names=[model_type])
        logger.info(f"speech_enhancement model loaded. {model_type}")

        self.crt_audio_duration = 0.4  # in seconds

    def enhance(self, audio_path, output_path=None, align_ratio=0.6, save_raw=False):
        if output_path is None:
            output_path = os.path.splitext(audio_path)[0] + "_enhanced.wav"

        if "48k" in self.model_type.lower():
            audio_path_48k = os.path.splitext(audio_path)[0] + "_48k.wav"
            original_audio_48k = AudioSegment.from_wav(audio_path)
            self.crt_audio_duration = len(original_audio_48k) / 1000.0
            if original_audio_48k.frame_rate != 48000:
                original_audio_48k = original_audio_48k.set_frame_rate(48000)
                original_audio_48k.export(audio_path_48k, format="wav")
            else:
                audio_path_48k = audio_path
            result_wav = self.model(input_path=audio_path_48k, online_write=False)
        else:
            audio_path_16k = os.path.splitext(audio_path)[0] + "_16k.wav"
            original_audio_16k = AudioSegment.from_wav(audio_path)
            self.crt_audio_duration = len(original_audio_48k) / 1000.0
            if original_audio_16k.frame_rate != 16000:
                original_audio_16k = original_audio_16k.set_frame_rate(16000)
                original_audio_16k.export(audio_path_16k, format="wav")
            else:
                audio_path_16k = audio_path
            result_wav = self.model(input_path=audio_path_16k, online_write=False)

        self.model.write(result_wav, output_path=output_path)
        logger.info(f"enhanced audio saved to {output_path}")

        output_tmp = AudioSegment.from_wav(output_path)
        original_audio = AudioSegment.from_wav(audio_path)
        # normalize to original audio frame rate
        if output_tmp.frame_rate != original_audio.frame_rate and not save_raw:
            output_tmp = output_tmp.set_frame_rate(original_audio.frame_rate)
            logger.info(
                f"reset output sample rate to original: {output_tmp.frame_rate}"
            )
            output_tmp.export(output_path, format="wav")

        original_dbfs = original_audio.dBFS
        logger.info(f"Original audio dBFS: {original_dbfs:.2f}")

        enhanced_audio = AudioSegment.from_wav(output_path)
        change_in_dbfs = original_dbfs - enhanced_audio.dBFS
        enhanced_audio = enhanced_audio.apply_gain(change_in_dbfs * align_ratio)
        logger.info(f"model output dBFS: {enhanced_audio.dBFS:.2f}")

        if save_raw:
            output_path = os.path.splitext(output_path)[0] + "_aligned.wav"
        enhanced_audio.export(output_path, format="wav")
        logger.info(f"Enhanced audio saved to {output_path} with matched volume")
        return output_path


class SpeechSeparate:
    def __init__(self) -> None:
        self.model = ClearVoice(
            task="speech_separation", model_names=["MossFormer2_SS_16K"]
        )

    def separate(self, audio_path, output_path=None):
        if output_path is None:
            output_path = os.path.splitext(audio_path)[0] + "_separated.wav"

        audio_path_16k = os.path.splitext(audio_path)[0] + "_16k.wav"
        original_audio_16k = AudioSegment.from_wav(audio_path)
        if original_audio_16k.frame_rate != 16000:
            original_audio_16k = original_audio_16k.set_frame_rate(16000)
            original_audio_16k.export(audio_path_16k, format="wav")
        else:
            audio_path_16k = audio_path

        result_wav = self.model(input_path=audio_path_16k, online_write=False)
        print(result_wav)
        self.model.write(result_wav, output_path=output_path)
        logger.info(f"enhanced audio saved to {output_path}")
        return output_path


def enhance_simple(audio_file):
    save_path = os.path.splitext(audio_file)[0] + "_enhance_denoiser.wav"

    # not work
    # from scipy.io import wavfile
    # import noisereduce as nr
    # # load data
    # rate, data = wavfile.read(audio_file)
    # # perform noise reduction
    # reduced_noise = nr.reduce_noise(y=data, sr=rate)
    # wavfile.write(save_path, rate, reduced_noise)
    # return save_path

    # from pydub import AudioSegment
    # from pydub.effects import compress_dynamic_range
    # audio = AudioSegment.from_wav(audio_file)
    # # 应用均衡化
    # equalized_audio = compress_dynamic_range(audio)
    # equalized_audio.export(save_path, format="wav")

    # from denoiser import pretrained
    # from denoiser.dsp import convert_audio
    # import soundfile as sf
    # import torchaudio

    # model = pretrained.dns64()

    # audio_file = normalize_audio_to_target(audio_file)
    # wav, sr = torchaudio.load(audio_file)
    # wav = convert_audio(wav, sr, model.sample_rate, model.chin)

    # with torch.no_grad():
    #     denoised = model(wav[None])[0].cpu()
    # print(denoised.shape)
    # # sf.write(save_path, denoised.numpy(), model.sample_rate)
    # # torchaudio.save(save_path, denoised, model.sample_rate)
    # save_np_float32_to_wav_file(
    #     denoised.numpy(),
    #     model.sample_rate,
    #     save_path,
    # )

    # save_path = os.path.splitext(audio_file)[0] + "_addphone.wav"
    # add_phone_effect(audio_file, save_path)
    save_path = os.path.splitext(audio_file)[0] + "_dephone.wav"
    dephone_effect(audio_file, save_path)
    # advanced_dephone_effect(audio_file, save_path)
    return save_path
