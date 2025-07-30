"""

Models for removeing reverbs


"""

import os
from pathlib import Path
from urllib.parse import urlparse
from loguru import logger
import torch
from .uvr5.mdxnet import Predictor
import soundfile as sf
from types import SimpleNamespace


def get_filename_from_url(url):
    return os.path.basename(urlparse(url).path)


class AudioDereverbOne:
    def __init__(
        self,
        model_type="dereverb-melband-roformer-small",
        revise_instrument=False,
        revise_reverb=False,
    ) -> None:
        """
        Models especially for Dereverbe
        """
        self.model_type = model_type
        self.revise_instrument = revise_instrument
        self.revise_reverb = revise_reverb

        if "melband-roformer" in self.model_type:
            available_models = {
                "dereverb-melband-roformer-small": "https://huggingface.co/Sucial/Dereverb-Echo_Mel_Band_Roformer/resolve/main/dereverb-echo_128_4_4_mel_band_roformer_sdr_dry_12.4235.ckpt",
                "dereverb-melband-roformer": "https://huggingface.co/Sucial/Dereverb-Echo_Mel_Band_Roformer/resolve/main/dereverb-echo_mel_band_roformer_sdr_10.0169.ckpt",
            }

            from .uvr5.mel_band_roformer_infer import AudioSeparator

            assert (
                self.model_type in available_models
            ), f"model {self.model_type} not available for dereverb"

            self.model = AudioSeparator(
                model_path=f"checkpoints/{self.model_type}.ckpt",
                model_url=available_models[self.model_type],
            )
            logger.info(f"audio separator using {self.model_type} model")
        elif "bs_roformer" in self.model_type:
            from .uvr5.mel_band_roformer_infer import AudioSeparator

            self.model = AudioSeparator(model_path="checkpoints/bs_roformer.ckpt")
            logger.info(f"audio separator using {self.model_type} model")
        elif "bandit_v2" in self.model_type:
            pass
        elif "mdxnet" in self.model_type:
            self.model_type = self.model_type.replace("audiotool-", "")
            if self.model_type == "mdxnet":
                self.model_type = "mdxnet-main"
                logger.info(f"force using default mdxnet model")

            # source https://github.com/TRvlvr/model_repo/releases/tag/all_public_uvr_models
            # https://github.com/TRvlvr/model_repo/releases/tag/all_public_uvr_models
            hf_root = "hf-mirror.com"
            available_models = {
                "mdxnet-main": "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Inst_Main.onnx",
                "mdxnet-voc-ft": "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Voc_FT.onnx",
                "mdxnet-crowd-hq": "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET_Crowd_HQ_1.onnx",
                "mdxnet-kim-vocal-2": f"https://{hf_root}/seanghay/uvr_models/resolve/main/Kim_Vocal_2.onnx",
                "mdxnet-reverb-hq": f"https://{hf_root}/seanghay/uvr_models/resolve/main/Reverb_HQ_By_FoxJoy.onnx",
            }
            """
            Combination for more cleaner
            MDX-Net: Kim Vocal 1, UVR-MDX-NET inst 3 & UVR-MDX-NET inst main
            Demucs: v4: htdemucs_ft
            """
            if self.model_type not in available_models:
                raise Exception(
                    f"Model {self.model_type} not found, available models: {available_models.keys()}"
                )
            model_path = f"checkpoints/{get_filename_from_url(available_models[self.model_type])}"
            if not os.path.exists(model_path):
                logger.info(
                    f"downloading {self.model_type} model from {available_models[self.model_type]}"
                )
                torch.hub.download_url_to_file(
                    available_models[self.model_type], model_path, progress=True
                )
                logger.info(f"{self.model_type} model downloaded successfully.")
            self.model_path = model_path
            model_dim_map = {
                "mdxnet-kim-vocal-2": 3072,
                "mdxnet-voc-ft": 3072,
                "mdxnet-crowd-hq": 2560,
            }
            if "crowd-hq" in self.model_type:
                logger.warning(f"{self.model_type} performance is bad!")

            mdx_config = SimpleNamespace(
                output="temp/",
                onnx=Path(self.model_path),
                model_path=Path(self.model_path),
                denoise=True,
                margin=44100,
                chunks=15,
                n_fft=6144,
                dim_t=8,
                dim_f=(
                    2048
                    if self.model_type not in model_dim_map
                    else model_dim_map[self.model_type]
                ),
            )
            # todo: add default model path
            self.model = Predictor(mdx_config)
            logger.info(f"mdxnet model initialized.")
        else:
            raise Exception("Model not found")

    def separate(self, audio_file, output_dir=None):
        if "mdxnet" in self.model_type:
            # vocals, no_vocals, sampling_rate = self.model.predict(audio_file)
            no_vocals, vocals, sampling_rate = self.model.predict(audio_file)
            base_name = os.path.splitext(os.path.basename(audio_file))[0]

            if output_dir is not None:
                vocal_path = os.path.join(output_dir, f"{base_name}_vocals.wav")
                inst_path = os.path.join(output_dir, f"{base_name}_instrumental.wav")
            else:
                vocal_path = os.path.join(
                    os.path.dirname(audio_file), f"{base_name}_vocals.wav"
                )
                inst_path = os.path.join(
                    os.path.dirname(audio_file), f"{base_name}_instrumental.wav"
                )

            sf.write(
                vocal_path,
                vocals,
                sampling_rate,
            )
            sf.write(
                inst_path,
                no_vocals,
                sampling_rate,
            )
            return {"vocals": vocal_path, "instrumental": inst_path}

        else:
            return self.model.separate(audio_file, output_dir=output_dir)
