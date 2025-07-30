from collections import defaultdict
from typing import Dict, List
import numpy as np
import torch
from loguru import logger
import os

import torchaudio

from ultracutpro.ai.voice.one_asr import VoiceActivityDetector
from .speaker_clustering import SpeakerClustering


import csv
from datetime import timedelta
import json
from loguru import logger
from datetime import timedelta

try:
    from funasr import AutoModel
except ImportError:
    logger.warning("funasr is not installed, some functions may not work.")


class SpeakerEmbedModel:
    def __init__(self, speaker_model_name) -> None:
        model_name = "M"  # ~b3-b4 size
        train_type = "ft_mix"
        dataset = "vb2+vox2+cnc"
        torch.hub.set_dir("./checkpoints/")
        if os.path.exists("checkpoints/IDRnD_ReDimNet_master"):
            source = "local"
            # source = "github"
            model_or_dir = "checkpoints/IDRnD_ReDimNet_master"
            logger.info(f"founded: {model_or_dir}, load from local.")
        else:
            source = "github"
            model_or_dir = "IDRnD/ReDimNet"
        self.model = torch.hub.load(
            model_or_dir,
            "ReDimNet",
            source=source,
            model_name=model_name,
            train_type=train_type,
            dataset=dataset,
            skip_validation=True,
        )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.spectrogram = self.model.spec
        self.model.spec = torch.nn.Identity()
        if self.device == "cuda":
            self.model.half()
        self.spectrogram.eval()
        self.model.eval()

    def __call__(self, audio, return_tensor=False):
        if len(audio.shape) == 1:
            audio = audio.unsqueeze(0)
            audio = audio.to(self.device)
            if self.device == "cuda":
                audio = audio.half()
        # print(audio)
        # print(audio.shape)
        spec = self.spectrogram(audio)
        if self.device == "cuda":
            spec = spec.half()
        a = self.model(spec)
        # print(a)
        if not return_tensor:
            return a.detach().cpu().numpy()
        return a


class SpeakerVerification:
    def __init__(
        self,
        speaker_model_name="redimnet",
        vad_model=None,
        similarity_threshold=0.4,
        merge_small_clusters=True,
        merge_small_clusters_threshold=0.35,
    ):
        """
        similarity_threshold:
        """
        # extract the embedding of speaker
        # self.speaker_embed_model = EmbedModel()
        self.vad = vad_model
        if self.vad is None:
            logger.warning("vad is None, will not run vad.")
        self.speaker_embed_model = SpeakerEmbedModel(speaker_model_name)
        self.similarity_threshold = similarity_threshold
        self.crt_wav = None

        self.merge_small_clusters = merge_small_clusters
        self.merge_small_clusters_threshold = merge_small_clusters_threshold

        self.clustering = SpeakerClustering(method="simple")
        # self.clustering = SpeakerClustering(method="funasr")

    def _read_audio(self, audio, sampling_rate=16000):
        self.sample_rate = sampling_rate
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

    def init_audio_file(self, audio):
        self.crt_wav = self._read_audio(audio)

    def get_sub_audio(self, start_s, end_s):
        """
        start_ms: start time in ms
        """
        start_sample = int(start_s * self.sample_rate)
        end_sample = int(end_s * self.sample_rate)
        return self.crt_wav[start_sample:end_sample]

    def extract_voice_segments(self, audio: np.ndarray) -> List[np.ndarray]:
        if self.vad is None:
            logger.info(
                "create vad on the fly as you did not have voice_segments and not vad"
            )
            self.vad = VoiceActivityDetector()
        return self.vad.get_timestamps(audio)

    def compute_embeddings(self, voice_segments: List[np.ndarray]) -> np.ndarray:
        embeddings = []
        for segment in voice_segments:
            embedding = self.speaker_embed_model(segment)
            embeddings.append(embedding[0])
        embeds = np.array(embeddings)
        return embeds

    def clear_audio_file(self):
        self.crt_wav = None

    def get_speaker_ids(
        self,
        audio_file: str = None,
        voice_segments=None,
        batch_segments=120,
        debug=False,
    ) -> Dict[int, List[np.ndarray]]:
        """
        users can specific timestamps, if has, VAD will not run
        """
        if audio_file is None and self.vad is None:
            logger.warning(
                "You are not provide either whole audio or vad model, this could result fail."
            )
        has_seg_before = voice_segments is not None
        if voice_segments is None:
            logger.info(f"runing on vad..")
            voice_segments = self.extract_voice_segments(audio_file)
            logger.info("segments got.")
        elif self.vad is None:
            # voice segments have, and VAD is none
            if self.crt_wav is not None:
                logger.info("reuse from crt_wav.")
            else:
                logger.info("init whole audio file.")
                self.init_audio_file(audio_file)

        logger.info(f"all voice_segments: {len(voice_segments)}")
        # Process segments in batches
        segments_times = [(seg["start"], seg["end"]) for seg in voice_segments]
        if self.vad is None:
            audio_datas = [
                self.get_sub_audio(b["start"], b["end"]) for b in voice_segments
            ]
        else:
            audio_datas = [
                self.vad.get_sub_audio(b["start"], b["end"]) for b in voice_segments
            ]

        embeddings = self.compute_embeddings(audio_datas)
        speaker_labels = self.clustering.get_speaker_ids(
            embeddings,
            merge_threshold=self.merge_small_clusters_threshold,
            batch_segments=batch_segments,
            debug=debug,
        )
        if debug:
            logger.info(f"speaker_labels: {speaker_labels}")

        speaker_segments = defaultdict(list)
        for (start, end), label in zip(segments_times, speaker_labels):
            speaker_segments[label].append({"start": start, "end": end})

        timeline = []
        for speaker_id, segments in speaker_segments.items():
            for segment in segments:
                timeline.append(
                    {
                        "start": segment["start"],
                        "end": segment["end"],
                        "speaker_id": speaker_id,
                    }
                )
        timeline.sort(key=lambda x: x["start"])
        # logger.info(f'final timeline speaker id: {[i["speaker_id"] for i in timeline]}')
        return timeline


is_whisper_model = lambda x: "whisper" in x.lower()


class SpeakerDiarizationCamPP:

    def __init__(self, do_diarization=True) -> None:
        # paraformer-zh is a multi-functional asr model
        # use vad, punc, spk or not as you need
        if do_diarization:
            # self.model_name_or_path = "Whisper-large-v3-turbo"
            self.model_name_or_path = "paraformer-zh"
            self.model = AutoModel(
                model=self.model_name_or_path,
                # init_param="checkpoints/whisper-large-v3-turbo/large-v3-turbo.pt",
                # hub="openai",
                model_revision="v2.0.4",
                vad_model="fsmn-vad",
                vad_model_revision="v2.0.4",
                punc_model="ct-punc-c",
                punc_model_revision="v2.0.4",
                spk_model="cam++",
                spk_model_revision="v2.0.2",
                disable_update=True,
                # vad_kwargs={"max_single_segment_time": 30000},
            )

        else:
            self.model = AutoModel(
                model="paraformer-zh",
                model_revision="v2.0.4",
                vad_model="fsmn-vad",
                vad_model_revision="v2.0.4",
                # punc_model="ct-punc-c",
                # punc_model_revision="v2.0.4",
                # spk_model="cam++",
                # spk_model_revision="v2.0.2",
            )

    @staticmethod
    def save_to_csv(data, filename):
        def format_timestamp(seconds):
            # td = timedelta(milliseconds=seconds)
            td = timedelta(seconds=seconds)
            total_seconds = int(td.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = int(td.microseconds / 1000)
            return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

        with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["index", "时间戳", "转录文本", "说话人"])
            for index, entry in enumerate(data):
                start_timestamp = format_timestamp(entry["start"])
                end_timestamp = format_timestamp(entry["end"])
                subtitle_timestamp = f"{start_timestamp} --> {end_timestamp}"
                translated_subtitle = "''"
                chinese_subtitle = entry["text"]
                role = entry["speaker_id"]

                writer.writerow([index, subtitle_timestamp, chinese_subtitle, role])

    def get_asr_spk(self, audio_f, save_json=True, save_csv=True, rerun=False):

        save_f = audio_f[:-4] + "_funasr_dari.json"
        save_f_csv = audio_f[:-4] + "_funasr_dari.csv"

        new_results = []
        if os.path.exists(save_f):
            with open(save_f, "r") as f:
                new_results = json.load(f)
                logger.info(f"resumed from json file: {save_f}")
        else:
            if is_whisper_model(self.model_name_or_path):
                DecodingOptions = {
                    "task": "transcribe",
                    "language": "zh",
                    "beam_size": None,
                    "fp16": True,
                    "without_timestamps": False,
                    "prompt": None,
                }
                res = self.model.generate(
                    DecodingOptions=DecodingOptions,
                    batch_size_s=0,
                    input=audio_f,
                )
            else:
                res = self.model.generate(
                    input=audio_f,
                    batch_size_s=64,
                )

            for aa in res[0]["sentence_info"]:
                # print(aa)
                new_results.append(
                    {
                        "start": aa["start"] / 1000,
                        "end": aa["end"] / 1000,
                        "text": aa["text"],
                        "speaker_id": aa["spk"],
                    }
                )
        if save_json:
            with open(save_f, "w") as f:
                # with open("data/a.json", "w") as f:
                json.dump(new_results, f, indent=2, ensure_ascii=False)
            logger.info("result saved.")
        if save_csv:
            self.save_to_csv(new_results, save_f_csv)

        return new_results
