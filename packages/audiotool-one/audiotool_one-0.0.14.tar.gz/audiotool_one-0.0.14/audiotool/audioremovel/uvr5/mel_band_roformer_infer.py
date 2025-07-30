import argparse
import yaml
import time
from ml_collections import ConfigDict
from tqdm import tqdm
import sys
import os
import glob
import torch
import soundfile as sf
import torch.nn as nn
from .mel_band_roformer.utils import demix_track, get_model_from_config
import torch
import warnings
from loguru import logger
from .bsroformer import BsRoformer_Loader

warnings.filterwarnings("ignore")


class AudioSeparator:
    def __init__(
        self,
        config_path=None,
        model_path="checkpoints/melband_roformer_inst_v2.ckpt",
        device="cuda" if torch.cuda.is_available() else "cpu",
        model_url=None,
    ):
        """
        url:
        https://huggingface.co/KimberleyJSN/melbandroformer/blob/main/MelBandRoformer.ckpt
        Initialize the separator
        Args:
            config_path: path to yaml config file
            model_path: path to model checkpoint
            device: device to run inference on
        """
        # default_url = "https://huggingface.co/KimberleyJSN/melbandroformer/resolve/main/MelBandRoformer.ckpt"
        if "dereverb" in model_path.lower():
            # dereverb model
            default_url = model_url
        elif "melband_roformer_v2" in model_path.lower():
            default_url = "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/melband_roformer_inst_v2.ckpt"
        elif (
            "melband_roformer" in model_path.lower()
            or "melband_roformer_v1" in model_path.lower()
        ):
            default_url = "https://huggingface.co/KimberleyJSN/melbandroformer/resolve/main/MelBandRoformer.ckpt"
        elif "bs_roformer" in model_path.lower():
            default_url = "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/model_bs_roformer_ep_937_sdr_10.5309.ckpt"
        else:
            default_url = "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/model_bs_roformer_ep_937_sdr_10.5309.ckpt"

        if not os.path.exists(model_path):
            # download url to model_path
            logger.info(f"Downloading model from {default_url} into: {model_path}")
            torch.hub.download_url_to_file(default_url, model_path)
            logger.info(f"model downloaded successfully.")

        self.model_path = model_path
        if "melband_roformer" in model_path.lower():
            self._load_mel_band_roformer(model_path, device)
            logger.info("Melbandroformer model loaded successfully.")
        elif "dereverb-melband-roformer" in model_path.lower():
            self._load_mel_band_roformer(model_path, device)
            logger.info("Melbandroformer model loaded successfully.")
        elif "bs_roformer" in model_path.lower():
            self._load_bs_roformer(model_path, device)
            logger.info("BsRoformer model loaded successfully.")
        else:
            logger.error(
                f"Unsupported model {self.model_path}. Please use MelBandRoformer or BsRoformer."
            )
        self.device = device

    def _load_bs_roformer(self, model_path, device):
        self.model = BsRoformer_Loader(
            model_path, device, is_half=torch.cuda.is_available()
        )

    def _load_mel_band_roformer(self, model_path, device):
        if "dereverb-melband-roformer-small" in model_path.lower():
            config_path = os.path.join(
                os.path.dirname(__file__),
                "bs_roformer/configs",
                "config_dereverb-echo_128_4_4_mel_band_roformer.yaml",
            )
            logger.info(
                f"loading a dereverb-melband-roformer-small model. {config_path}"
            )
        elif "dereverb-melband-roformer" in model_path.lower():
            config_path = os.path.join(
                os.path.dirname(__file__),
                "bs_roformer/configs",
                "config_dereverb-echo_mel_band_roformer.yaml",
            )
            logger.info(f"loading a dereverb-melband-roformer model. {config_path}")
        else:
            config_path = os.path.join(
                os.path.dirname(__file__), "mel_band_roformer", "config.yaml"
            )
        with open(config_path) as f:
            # config = yaml.safe_load(f)
            config = ConfigDict(yaml.load(f, Loader=yaml.FullLoader))
        self.config = config
        self.device = device

        if "dereverb" in model_path.lower():
            from .bs_roformer.mel_band_roformer import MelBandRoformer

            self.model = MelBandRoformer(**dict(self.config.model))
            self.model.load_state_dict(torch.load(model_path, map_location=device))
            self.model.to(device)
            self.model.eval()

        else:
            self.model = get_model_from_config("mel_band_roformer", self.config)
            self.model.load_state_dict(torch.load(model_path, map_location=device))
            self.model.to(device)
            self.model.eval()

    def separate(self, audio_path, output_dir=None):
        """
        Separate audio into vocals and instrumental
        Args:
            audio_path: path to input audio file
            output_dir: directory to save separated audio files (optional)
        Returns:
            dict: paths to separated audio files
        """
        # Determine output paths
        if output_dir is None:
            output_dir = os.path.dirname(audio_path)
        os.makedirs(output_dir, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        vocal_path = os.path.join(output_dir, f"{base_name}_vocals.wav")
        inst_path = os.path.join(output_dir, f"{base_name}_instrumental.wav")

        # Load and process audio
        mix, sr = sf.read(audio_path)
        mixture = torch.tensor(mix.T, dtype=torch.float32)

        # Separate
        if "melband_roformer" in self.model_path.lower():
            res, _ = demix_track(self.config, self.model, mixture, self.device)

            # Get instruments
            instruments = self.config.training.instruments
            if self.config.training.target_instrument is not None:
                instruments = [self.config.training.target_instrument]

            # Save vocals
            vocals = res[instruments[0]].T
            sf.write(vocal_path, vocals, sr, subtype="FLOAT")

            # Save instrumental
            instrumental = mix - vocals
            sf.write(inst_path, instrumental, sr, subtype="FLOAT")
            return {"vocals": vocal_path, "instrumental": inst_path}
        elif "dereverb" in self.model_path.lower():
            res, _ = demix_track(self.config, self.model, mixture, self.device)

            # Get instruments
            instruments = self.config.training.instruments
            if self.config.training.target_instrument is not None:
                instruments = [self.config.training.target_instrument]

            # Save vocals
            vocals = res[instruments[0]].T
            sf.write(vocal_path, vocals, sr, subtype="FLOAT")

            # Save instrumental
            instrumental = mix - vocals
            sf.write(inst_path, instrumental, sr, subtype="FLOAT")
            return {"vocals": vocal_path, "instrumental": inst_path}
        elif "bs_roformer" in self.model_path.lower():
            res = self.model.demix_track(mixture, self.device)
            vocals = res["vocals"].T
            sf.write(vocal_path, vocals, sr, subtype="FLOAT")

            instrumental = mix - vocals
            sf.write(inst_path, instrumental, sr, subtype="FLOAT")
            return {"vocals": vocal_path, "instrumental": inst_path}


def run_folder(model, args, config, device, verbose=False):
    start_time = time.time()
    model.eval()
    all_mixtures_path = glob.glob(args.input_folder + "/*.wav")
    total_tracks = len(all_mixtures_path)
    print("Total tracks found: {}".format(total_tracks))

    instruments = config.training.instruments
    if config.training.target_instrument is not None:
        instruments = [config.training.target_instrument]

    if not os.path.isdir(args.store_dir):
        os.mkdir(args.store_dir)

    if not verbose:
        all_mixtures_path = tqdm(all_mixtures_path)

    first_chunk_time = None

    for track_number, path in enumerate(all_mixtures_path, 1):
        print(
            f"\nProcessing track {track_number}/{total_tracks}: {os.path.basename(path)}"
        )

        mix, sr = sf.read(path)
        mixture = torch.tensor(mix.T, dtype=torch.float32)

        if first_chunk_time is not None:
            total_length = mixture.shape[1]
            num_chunks = (
                total_length
                + config.inference.chunk_size // config.inference.num_overlap
                - 1
            ) // (config.inference.chunk_size // config.inference.num_overlap)
            estimated_total_time = first_chunk_time * num_chunks
            print(
                f"Estimated total processing time for this track: {estimated_total_time:.2f} seconds"
            )
            sys.stdout.write(
                f"Estimated time remaining: {estimated_total_time:.2f} seconds\r"
            )
            sys.stdout.flush()

        res, first_chunk_time = demix_track(
            config, model, mixture, device, first_chunk_time
        )

        for instr in instruments:
            vocals_path = "{}/{}_{}.wav".format(
                args.store_dir, os.path.basename(path)[:-4], instr
            )
            sf.write(vocals_path, res[instr].T, sr, subtype="FLOAT")

        vocals = res[instruments[0]].T
        instrumental = mix - vocals
        instrumental_path = "{}/{}_instrumental.wav".format(
            args.store_dir, os.path.basename(path)[:-4]
        )
        sf.write(instrumental_path, instrumental, sr, subtype="FLOAT")

    time.sleep(1)
    print("Elapsed time: {:.2f} sec".format(time.time() - start_time))


def proc_folder(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_type", type=str, default="mel_band_roformer")
    parser.add_argument("--config_path", type=str, help="path to config yaml file")
    parser.add_argument(
        "--model_path", type=str, default="", help="Location of the model"
    )
    parser.add_argument("--input_folder", type=str, help="folder with songs to process")
    parser.add_argument(
        "--store_dir", default="", type=str, help="path to store model outputs"
    )
    parser.add_argument(
        "--device_ids", nargs="+", type=int, default=0, help="list of gpu ids"
    )
    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)

    torch.backends.cudnn.benchmark = True

    with open(args.config_path) as f:
        config = ConfigDict(yaml.load(f, Loader=yaml.FullLoader))

    model = get_model_from_config(args.model_type, config)
    if args.model_path != "":
        print("Using model: {}".format(args.model_path))
        model.load_state_dict(
            torch.load(args.model_path, map_location=torch.device("cpu"))
        )

    if torch.cuda.is_available():
        device_ids = args.device_ids
        if type(device_ids) == int:
            device = torch.device(f"cuda:{device_ids}")
            model = model.to(device)
        else:
            device = torch.device(f"cuda:{device_ids[0]}")
            model = nn.DataParallel(model, device_ids=device_ids).to(device)
    else:
        device = "cpu"
        print("CUDA is not available. Run inference on CPU. It will be very slow...")
        model = model.to(device)

    run_folder(model, args, config, device, verbose=False)


if __name__ == "__main__":
    proc_folder(None)
