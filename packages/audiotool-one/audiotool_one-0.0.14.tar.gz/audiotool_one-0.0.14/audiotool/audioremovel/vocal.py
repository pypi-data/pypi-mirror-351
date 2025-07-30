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


class AudioSeparatorOne:
    def __init__(
        self,
        model_type="melband_roformer",
        revise_instrument=False,
        revise_vocal=False,
        revise_reverb=False,
    ) -> None:
        """
        MXDNet have issue in instrument might contains human voice.

        """
        self.model_type = model_type
        self.revise_instrument = revise_instrument
        self.revise_vocal = revise_vocal
        self.revise_reverb = revise_reverb

        if "melband_roformer" in self.model_type:
            from .uvr5.mel_band_roformer_infer import AudioSeparator

            self.model = AudioSeparator(
                model_path=f"checkpoints/{self.model_type}.ckpt"
            )
            logger.info(f"audio separator using {self.model_type} model")
        elif "bs_roformer" in self.model_type:
            from .uvr5.mel_band_roformer_infer import AudioSeparator

            self.model = AudioSeparator(model_path="checkpoints/bs_roformer.ckpt")
            logger.info(f"audio separator using {self.model_type} model")
        elif "bandit_v2" in self.model_type:
            logger.error("bandit_v2 not supported yet.")
            pass
        elif "mdxnet" in self.model_type:
            self.model_type = self.model_type.replace("audiotool-", "")
            if self.model_type == "mdxnet":
                self.model_type = "mdxnet-kim-inst"
                logger.info(f"force using default mdxnet model")

            # source https://github.com/TRvlvr/model_repo/releases/tag/all_public_uvr_models
            # https://github.com/TRvlvr/model_repo/releases/tag/all_public_uvr_models

            self.model_path = self._get_mdxnet_path(self.model_type)
            self.model = self._get_mdxnet_model(self.model_type, self.model_path)
            logger.info(f"mdxnet model initialized. {self.model_path}")

            if self.revise_vocal:
                # inst_model = "mdxnet-kim-vocal-2"
                inst_model = "mdxnet-voc-ft"
                self.revise_vocal_model = self._get_mdxnet_model(
                    inst_model, self._get_mdxnet_path(inst_model)
                )
                logger.info(f"will using {inst_model} to revise vocal extraction.")

            if self.revise_instrument:
                inst_model = "mdxnet-kim-inst"
                logger.info(f"will using {inst_model} to revise vocal extraction.")
                self.revise_inst_model = self._get_mdxnet_model(
                    inst_model, self._get_mdxnet_path(inst_model)
                )
        else:
            raise Exception(f"Model not found {self.model_type}")

    def _get_mdxnet_path(self, model_type):
        hf_root = "hf-mirror.com"
        available_models = {
            "mdxnet-main": "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Inst_Main.onnx",
            "mdxnet-inst-main": "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Inst_Main.onnx",
            "mdxnet-voc-ft": "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Voc_FT.onnx",
            "mdxnet-crowd-hq": "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET_Crowd_HQ_1.onnx",
            "mdxnet-kim-vocal-2": f"https://{hf_root}/seanghay/uvr_models/resolve/main/Kim_Vocal_2.onnx",
            "mdxnet-kim-inst": f"https://{hf_root}/Blane187/all_public_uvr_models/resolve/main/Kim_Inst.onnx",
            "mdxnet-reverb-hq": f"https://{hf_root}/seanghay/uvr_models/resolve/main/Reverb_HQ_By_FoxJoy.onnx",
        }
        """
        inst-main: 对背景音乐提取较为准确
        voc-ft: 对人声提取较为准确

        Combination for more cleaner
        MDX-Net: Kim Vocal 1, UVR-MDX-NET inst 3 & UVR-MDX-NET inst main
        Demucs: v4: htdemucs_ft
        """
        if self.model_type not in available_models:
            raise Exception(
                f"Model {self.model_type} not found, available models: {available_models.keys()}"
            )
        model_path = (
            f"checkpoints/{get_filename_from_url(available_models[self.model_type])}"
        )
        if not os.path.exists(model_path):
            logger.info(
                f"downloading {self.model_type} model from {available_models[self.model_type]}"
            )
            torch.hub.download_url_to_file(
                available_models[self.model_type], model_path, progress=True
            )
            logger.info(f"{self.model_type} model downloaded successfully.")
        return model_path

    def _get_mdxnet_model(self, model_type, model_path):
        model_dim_map = {
            "mdxnet-kim-vocal-2": 3072,
            "mdxnet-kim-inst": 3072,
            "mdxnet-voc-ft": 3072,
            "mdxnet-crowd-hq": 2560,
        }
        if "crowd-hq" in model_type:
            logger.warning(f"{model_type} performance is bad!")

        mdx_config = SimpleNamespace(
            output="temp/",
            onnx=Path(model_path),
            model_path=Path(model_path),
            denoise=True,
            margin=44100,
            chunks=15,
            n_fft=6144,
            dim_t=8,
            dim_f=(
                2048 if model_type not in model_dim_map else model_dim_map[model_type]
            ),
        )
        model = Predictor(mdx_config)
        return model

    def separate(
        self,
        audio_file,
        output_dir=None,
    ):
        if "mdxnet" in self.model_type:
            # vocals, no_vocals, sampling_rate = self.model.predict(audio_file)

            # due to onnx export issue, some models actually opposite vocal and inst
            if "kim-inst" in self.model_type or "mdxnet-main" in self.model_type:
                vocals, no_vocals, sampling_rate = self.model.predict(audio_file)
            else:
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

            # decide to rerun
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

            if self.revise_vocal:
                vocals, no_vocals, sampling_rate = self.revise_vocal_model.predict(
                    vocal_path
                )
                # vocal_revise_path = os.path.splitext(vocal_path)[0] + "_revise.wav"
                vocal_revise_path = vocal_path
                sf.write(
                    vocal_revise_path,
                    vocals,
                    sampling_rate,
                )
                return {"vocals": vocal_revise_path, "instrumental": inst_path}
            if self.revise_instrument:
                logger.error("revise instrumental not implemented yet")
            return {"vocals": vocal_path, "instrumental": inst_path}

        else:
            return self.model.separate(audio_file, output_dir=output_dir)
