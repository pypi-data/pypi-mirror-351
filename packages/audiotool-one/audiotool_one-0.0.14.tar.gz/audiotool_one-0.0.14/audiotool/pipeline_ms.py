from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import os
from funasr import AutoModel


class MSSD:
    def __init__(self, pipe="paraformer") -> None:
        self.pipe = pipe
        if pipe == "paraformer":
            pass
            # self.pipeline_ms = pipeline(
            #     task=Tasks.auto_speech_recognition,
            #     model="damo/speech_paraformer-large-vad-punc-spk_asr_nat-zh-cn",
            #     # model_revision="v0.0.2",
            #     vad_model="damo/speech_fsmn_vad_zh-cn-16k-common-pytorch",
            #     punc_model="damo/punc_ct-transformer_cn-en-common-vocab471067-large",
            #     output_dir="results",
            # )
        elif pipe == "campp":
            # self.pipeline_ms = AutoModel(
            #     task="speaker-diarization",
            #     model="damo/speech_campplus_speaker-diarization_common",
            #     # model_revision="v1.0.0",
            # )
            pass

    def get_result_ms(self, audio_f):
        result_dir = os.path.dirname(audio_f)
        if self.pipe == "paraformer":
            rec_result = self.pipeline_ms(
                audio_in=audio_f,
                batch_size_token=5000,
                batch_size_token_threshold_s=40,
                max_single_segment_time=6000,
            )
            # convert rec result to desired format.
            speakers = []
            for a in rec_result["sentences"]:
                speaker = {}
                speaker["start"] = a["start"] / 1000
                speaker["end"] = a["end"] / 1000
                speaker["text"] = a["text"]
                speaker["speaker"] = a["spk"]
                speaker["unit_len"] = a["end"] - a["start"]
                speakers.append(speaker)
            return speakers
        elif self.pipe == "campp":
            rec_result = self.pipeline_ms(
                audio_f,
            )
            # convert rec result to desired format.
            speakers = []
            for a in rec_result["text"]:
                speaker = {}
                speaker["start"] = a[0]
                speaker["end"] = a[1]
                speaker["text"] = ""
                speaker["speaker"] = a[2]
                speaker["unit_len"] = a[1] - a[0]
                speakers.append(speaker)
            return speakers


class MSSD2:
    def __init__(self, pipe="paraformer") -> None:
        self.pipe = pipe
        if pipe == "paraformer":
            print("unsupported now.")
            pass
        elif pipe == "campp":
            self.pipeline_ms = AutoModel(
                # task="speaker-diarization",
                model="iic/SenseVoiceSmall",
                # model="paraformer-zh",
                # vad_model="fsmn-vad",
                spk_model="cam++",
                # model_revision="v1.0.0",
            )

    def get_result_ms(self, audio_f):
        result_dir = os.path.dirname(audio_f)
        if self.pipe == "paraformer":
            rec_result = self.pipeline_ms(
                audio_in=audio_f,
                batch_size_token=5000,
                batch_size_token_threshold_s=40,
                max_single_segment_time=6000,
            )
            # convert rec result to desired format.
            speakers = []
            for a in rec_result["sentences"]:
                speaker = {}
                speaker["start"] = a["start"] / 1000
                speaker["end"] = a["end"] / 1000
                speaker["text"] = a["text"]
                speaker["speaker"] = a["spk"]
                speaker["unit_len"] = a["end"] - a["start"]
                speakers.append(speaker)
            return speakers
        elif self.pipe == "campp":
            rec_result = self.pipeline_ms.generate(
                input=audio_f,
            )
            # convert rec result to desired format.
            speakers = []
            for a in rec_result["text"]:
                speaker = {}
                speaker["start"] = a[0]
                speaker["end"] = a[1]
                speaker["text"] = ""
                speaker["speaker"] = a[2]
                speaker["unit_len"] = a[1] - a[0]
                speakers.append(speaker)
            return speakers
