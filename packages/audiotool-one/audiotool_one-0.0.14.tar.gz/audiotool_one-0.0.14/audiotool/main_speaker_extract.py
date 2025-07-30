import argparse
import glob
import json
import pickle
import shutil
import time
import os
import numpy as np
from collections import OrderedDict
from audiotool.get_audio_timestamp import extract_audio_to_file
from pydub import AudioSegment
from audiotool.get_audio_timestamp import video_to_audio
from .pipeline_annote import PyAnno
from .pipeline_ms import MSSD, MSSD2

# import torchaudio.lib.libtorchaudio
from pprint import pprint
import csv


def save_to_csv(data, filename, main_spk_id):
    # Open the file in write mode
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        # Create a CSV writer
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow(["开始时间", "结束时间", "文本", "说话人id"])
        # Write the data
        for item in data:
            if item["speaker"] == main_spk_id:
                item["speaker"] = str(item["speaker"]) + "_main"
            writer.writerow(
                [
                    item["start"],
                    item["end"],
                    item["text"] if "text" in item.keys() else "",
                    item["speaker"],
                ]
            )
    print("done save")


def save_tts_txt(data, target_folder, format="mp3"):
    # Open the file in write mode
    # with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    for i, item in enumerate(data):
        tgt_txt_f = os.path.join(target_folder, str(item["speaker"]) + "_tts.txt")
        with open(tgt_txt_f, "a", encoding="utf-8") as file:
            a_f = f'{str(item["speaker"])}_{i}.{format}'
            d = f'{a_f}|{str(item["speaker"])}|ZH|{item["text"] if "text" in item.keys() else ""}'
            file.write(d + "\n")
    print("save txt done.")


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        return super(NumpyEncoder, self).default(obj)


def save_eval_json(data, file_name_key, target_f):
    # check file already have
    if os.path.exists(target_f):
        with open(target_f, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
        existing_data[file_name_key] = data
        with open(target_f, "w", encoding="utf-8") as file:
            json.dump(
                existing_data, file, indent=4, ensure_ascii=False, cls=NumpyEncoder
            )
    else:
        result = {}
        result[file_name_key] = data
        with open(target_f, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4, ensure_ascii=False, cls=NumpyEncoder)


def mute_speakers(wav_file, timestamps, main_speaker):
    # Load the audio file
    if wav_file.endswith(".wav"):
        audio = AudioSegment.from_wav(wav_file)
    elif wav_file.endswith(".mp3"):
        audio = AudioSegment.from_mp3(wav_file)
    else:
        audio = AudioSegment.from_mp3(wav_file)
    # Iterate over the timestamps
    for timestamp in timestamps:
        # If the speaker is not the main speaker, mute them
        if "main" not in str(timestamp["speaker"]):
            start_t = int(timestamp["start"] * 1000)  # Convert to milliseconds
            end_t = int(timestamp["end"] * 1000)  # Convert to milliseconds
            audio = (
                audio[:start_t]
                + AudioSegment.silent(duration=(end_t - start_t))
                + audio[end_t:]
            )
    # Save the audio file
    to_save_f = ""
    if wav_file.endswith(".wav"):
        to_save_f = wav_file.replace(".wav", "_masked.wav")
        audio.export(to_save_f, format="wav")
    elif wav_file.endswith(".mp3"):
        to_save_f = wav_file.replace(".mp3", "_masked.mp3")
        audio.export(to_save_f, format="mp3")
    print(f"muted audio saved into: {to_save_f}")


def find_audio_files(path):
    mp3_files = glob.glob(f"{path}/*.mp3")
    wav_files = glob.glob(f"{path}/*.wav")
    a = mp3_files + wav_files
    return [i for i in a if "_masked" not in i]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", nargs="+", type=str, default=None)
    parser.add_argument("-m", "--model", type=str, default="campp")
    parser.add_argument("--format", type=str, default="mp3")
    parser.add_argument("-t", "--target", type=str, default=None, help="target folder")
    parser.add_argument("--tts", action="store_true", help="save tts txt?")
    parser.add_argument("--debug", action="store_true", help="save tts txt?")
    parser.add_argument("--eval", action="store_true", help="save eval result?")
    parser.add_argument(
        "--cache", action="store_true", help="save result to pkl for pass rerun models."
    )
    args = parser.parse_args()

    if "ms" in args.model or "campp" in args.model:
        pipe_name = "paraformer" if args.model == "ms" else "campp"
        ms_pipe = MSSD2(pipe=pipe_name)
        print(f"Modelscope pipe initiated: {pipe_name}")
    elif "trained" in args.model:
        ms_pipe = PyAnno(pipe=args.model)

    if args.format not in ["mp3", "wav"]:
        print("only mp3 and wav format support for now")

    print(f"start solve {len(args.file)} file(s).")

    files = args.file

    if len(files) == 1 and os.path.isdir(files[0]):
        print(f"auto found from dir: {files[0]}")
        files = find_audio_files(files[0])
        print(f"found: {len(files)} audio files except the one with _masked")

    for in_f in files:
        if in_f.endswith(".mp4"):
            print("convert mp4 to wav")
            in_f = video_to_audio(in_f, args.format)
            print(f"now solving: {in_f}")

        try:
            if args.model == "annote" or "trained" in args.model:
                cache_f = in_f.rsplit(".", maxsplit=1)[0] + f"_{args.model}.pkl"
                if args.cache and os.path.exists(cache_f):
                    speakers = pickle.load(open(cache_f, "rb"))
                    print(f"resume the cached identification result from: {cache_f}")
                else:
                    speakers = ms_pipe.get_annote_result(in_f)
                    if args.cache:
                        pickle.dump(speakers, open(cache_f, "wb"))
                        print(f"save the identification result to: {cache_f}")
            else:
                cache_f = in_f.rsplit(".", maxsplit=1)[0] + f"_{args.model}.pkl"
                if args.cache and os.path.exists(cache_f):
                    speakers = pickle.load(open(cache_f, "rb"))
                    print(f"resume the cached identification result from: {cache_f}")
                else:
                    speakers = ms_pipe.get_result_ms(in_f)
                    if args.cache:
                        pickle.dump(speakers, open(cache_f, "wb"))
                        print(f"save the identification result to: {cache_f}")

            if args.debug:
                pprint(speakers)
        except Exception as e:
            print(f"solve: {in_f} got error: {e}")
            import traceback

            traceback.print_exc()
            continue

        name = os.path.basename(in_f).split(".")[0]
        # save the most speaker into a folder by the length
        speakers_lens_gather = OrderedDict()
        for sp in speakers:
            # print(sp["speaker"])
            if sp["speaker"] in speakers_lens_gather.keys():
                speakers_lens_gather[sp["speaker"]] += sp["unit_len"]
            else:
                speakers_lens_gather[sp["speaker"]] = sp["unit_len"]

        if args.debug:
            print(speakers_lens_gather)

        most_speaker_index = np.argmax(list(speakers_lens_gather.values()))
        most_speaker = list(speakers_lens_gather.keys())[most_speaker_index]

        # add judge from audio loudness
        speakers_loudness_gather = OrderedDict()
        speakers_period_num_map = OrderedDict()
        original_audio = AudioSegment.from_file(in_f)
        for sp in speakers:
            start_t = int(sp["start"] * 1000)  # Convert to milliseconds
            end_t = int(sp["end"] * 1000)
            sound = original_audio[start_t:end_t]
            rms = sound.rms
            if sp["speaker"] in speakers_loudness_gather.keys():
                speakers_loudness_gather[sp["speaker"]] += rms
                speakers_period_num_map[sp["speaker"]] += 1
            else:
                speakers_loudness_gather[sp["speaker"]] = rms
                speakers_period_num_map[sp["speaker"]] = 1
        del original_audio
        # average of them
        speakers_loudness_gather = OrderedDict(
            [
                (k, v / speakers_period_num_map[k])
                for k, v in speakers_loudness_gather.items()
            ]
        )
        most_speaker_index_1 = np.argmax(list(speakers_loudness_gather.values()))
        most_speaker_1 = list(speakers_loudness_gather.keys())[most_speaker_index_1]

        if most_speaker != most_speaker_1:
            print(
                f"Warning: most speaker evidence, time and loudness not same, choose loundness."
                f" most speaker: {most_speaker}, most_speaker_1: {most_speaker_1}",
            )
            print(f"loudness compare: {speakers_loudness_gather}")
            most_speaker = most_speaker_1

        print("most speaker: ", most_speaker, ", index: ", most_speaker_index)
        target_folder = f"results/{name}"
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)
        os.makedirs(target_folder, exist_ok=True)
        if args.eval:
            save_eval_json(
                speakers,
                os.path.basename(in_f),
                os.path.join(os.path.dirname(in_f), "eval.json"),
            )

        for i, sp in enumerate(speakers):
            if sp["speaker"] == most_speaker:
                spk_dir = f'{target_folder}/{sp["speaker"]}_main'
            else:
                spk_dir = f'{target_folder}/{sp["speaker"]}'
            os.makedirs(spk_dir, exist_ok=True)
            s = sp["start"]
            e = sp["end"]
            if args.format == "wav":
                extract_audio_to_file(s, e, in_f, f"{spk_dir}/{sp['speaker']}_{i}.wav")
            else:
                extract_audio_to_file(s, e, in_f, f"{spk_dir}/{sp['speaker']}_{i}.mp3")

        if args.tts:
            save_tts_txt(speakers, target_folder, args.format)

        save_to_csv(speakers, os.path.join(target_folder, "asr.csv"), most_speaker)

        # concate all mp3 files into one
        most_spk_dir = f"{target_folder}/{most_speaker}_main"
        mp3_files = [
            f for f in os.listdir(most_spk_dir) if f.endswith(f".{args.format}")
        ]
        mp3_files.sort(key=lambda f: int("".join(filter(str.isdigit, f))))
        # Initialize an empty audio segment
        combined = AudioSegment.empty()
        for mp3_file in mp3_files:
            sound = AudioSegment.from_mp3(os.path.join(most_spk_dir, mp3_file))
            combined += sound
        combined.export(
            f"{target_folder}/final_concat.{args.format}", format=f"{args.format}"
        )
        print("done!")
        mute_speakers(in_f, speakers, most_speaker)


if __name__ == "__main__":
    main()
