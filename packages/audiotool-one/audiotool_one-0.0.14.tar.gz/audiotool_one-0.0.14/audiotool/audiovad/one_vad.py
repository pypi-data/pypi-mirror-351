from audiotool.audiovad.vad import VADFsmn
from silero_vad import load_silero_vad, get_speech_timestamps
import torchaudio
from loguru import logger


class VoiceActivityOne:
    def __init__(self, sample_rate=16000, model_type="silero") -> None:
        self.model_type = model_type
        if self.model_type == "fsmn":
            self.model = VADFsmn()
            logger.info("using fsmn vad model")
        elif self.model_type == "silero":
            self.model = load_silero_vad(onnx=True)
        else:
            logger.error("model type not support")
        self.crt_wav = None
        self.sample_rate = sample_rate

    def _read_audio(self, audio, sampling_rate=16000):
        wav, sr = torchaudio.load(audio, backend="soundfile")
        if wav.size(0) > 1:
            wav = wav.mean(dim=0, keepdim=True)
        if sr != sampling_rate:
            transform = torchaudio.transforms.Resample(
                orig_freq=sr, new_freq=sampling_rate
            )
            wav = transform(wav)
            sr = sampling_rate
        return wav.squeeze(0)

    def get_timestamps(
        self, audio, threshold=0.5, min_silence_duration_ms=50, speech_pad_ms=30
    ):
        if self.model_type == "fsmn":
            speech_timestamps = self.model.get_timestamps(
                audio, threshold, speech_pad_ms
            )
        elif self.model_type == "silero":
            self.crt_wav = self._read_audio(audio, sampling_rate=self.sample_rate)
            speech_timestamps = get_speech_timestamps(
                self.crt_wav,
                self.model,
                return_seconds=True,
                threshold=threshold,
                speech_pad_ms=speech_pad_ms,
                min_silence_duration_ms=min_silence_duration_ms,
            )
        return speech_timestamps

    def get_sub_audio(self, start_s, end_s):
        """
        start_ms: start time in ms
        """
        start_sample = int(start_s * self.sample_rate)
        end_sample = int(end_s * self.sample_rate)
        return self.crt_wav[start_sample:end_sample]
