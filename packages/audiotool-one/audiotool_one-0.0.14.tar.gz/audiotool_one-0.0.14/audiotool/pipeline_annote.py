from pyannote.audio import Pipeline
import time
import os
from pyannote.audio.pipelines import SpeakerDiarization


class PyAnno:
    def __init__(self, pipe="trained") -> None:
        self.pipe = pipe
        if pipe == "anno":
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token="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",
            )
        elif pipe == "trained":
            pretrained_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token="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",
                # cache_dir="./pretrain_model_3.1",
            )
            self.model_p = os.path.join(
                os.path.expanduser("~"),
                ".cache/lightning_logs/version_0/checkpoints/epoch=97.ckpt",
            )
            if not os.path.exists(self.model_p):
                print(
                    f"You selected trained model, but not found {self.model_p}, please download model and unzip it into ~/.cache/"
                )
                exit(0)
            self.pipeline = SpeakerDiarization(
                segmentation=self.model_p,  # pretrained_pipeline.segmentation_model, #finetuned_model,
                embedding=pretrained_pipeline.embedding,
                embedding_exclude_overlap=pretrained_pipeline.embedding_exclude_overlap,
                clustering=pretrained_pipeline.klustering,
            )
            best_segmentation_threshold = 0.58  # 0
            best_clustering_threshold = 0.68
            self.pipeline.instantiate(
                {
                    "segmentation": {
                        "threshold": best_segmentation_threshold,
                        "min_duration_off": 0.98,  # seconds
                    },
                    "clustering": {
                        "method": "centroid",
                        "min_cluster_size": 12,
                        "threshold": best_clustering_threshold,
                    },
                }
            )

    def get_annote_result(self, audio_f):
        # pipeline.to(torch.device("cuda"))
        folder = audio_f

        t0 = time.time()
        name = os.path.basename(folder).split(".")[0]
        # diarization = pipeline(folder, min_speakers=2, max_speakers=4)
        diarization = self.pipeline(folder, min_speakers=2, max_speakers=4)

        # diarization = pipeline(audio_f, num_speakers=2)
        t1 = time.time()
        print(f"time cost: {t1 - t0}")
        #  print the result
        speakers = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            # print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
            speaker_dict = {}
            speaker_dict["start"] = turn.start
            speaker_dict["end"] = turn.end
            speaker_dict["speaker"] = speaker
            speaker_dict["unit_len"] = turn.end - turn.start
            speakers.append(speaker_dict)
        # a list, contains very speaker info
        return speakers
