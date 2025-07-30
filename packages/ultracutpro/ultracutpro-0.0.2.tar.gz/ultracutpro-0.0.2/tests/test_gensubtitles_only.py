import argparse
from collections import defaultdict
import csv
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import sherpa_onnx
import soundfile as sf
from loguru import logger


def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--silero-vad-model",
        default="./data/silero_vad_v5.onnx",
        help="silero_vad.onnx",
    )
    parser.add_argument(
        "--tokens",
        default="./data/sherpa-onnx-sense-voice/tokens.txt",
        help="Path to tokens.txt",
    )
    parser.add_argument("--encoder", default="", help="encoder model")
    parser.add_argument("--decoder", default="", help="decoder model")
    parser.add_argument("--joiner", default="", help="joiner model")
    parser.add_argument("--paraformer", default="", help="model.onnx from Paraformer")
    parser.add_argument(
        "--speaker-model",
        # default="data/3dspeaker_speech_campplus_sv_zh_en_16k-common_advanced.onnx",
        default="data/3dspeaker_speech_eres2netv2_sv_zh-cn_16k-common.onnx",
        help="camppplus speaker model.",
    )
    parser.add_argument(
        "--sense-voice",
        default="./data/sherpa-onnx-sense-voice/model.onnx",
        help="SenseVoice",
    )
    parser.add_argument("--wenet-ctc", default="", help="CTC model.onnx from WeNet")
    parser.add_argument("--num-threads", type=int, default=3)
    parser.add_argument("--whisper-encoder", default="", help="encoder model")
    parser.add_argument("--whisper-decoder", default="", help="whisper decoder model")
    parser.add_argument(
        "--whisper-language", default="zh", help="""en, fr, de, zh, jp."""
    )
    parser.add_argument(
        "--whisper-task", default="transcribe", choices=["transcribe", "translate"]
    )
    parser.add_argument(
        "--whisper-tail-paddings",
        default=-1,
        type=int,
        help="""Number of tail padding frames.
        We have removed the 30-second constraint from whisper, so you need to
        choose the amount of tail padding frames by yourself.
        Use -1 to use a default value for tail padding.
        """,
    )
    parser.add_argument(
        "--decoding-method",
        type=str,
        default="greedy_search",
        help="""Valid values are greedy_search and modified_beam_search.
        modified_beam_search is valid only for transducer models.
        """,
    )
    parser.add_argument(
        "--debug",
        type=bool,
        default=False,
        help="True to show debug messages when loading modes.",
    )
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--feature-dim", type=int, default=80, help="Feature dimension")
    parser.add_argument("--threshold", type=float, default=0.52)
    # parser.add_argument("--speaker-file", default="data/speakers.txt")
    parser.add_argument("--speaker-file")
    parser.add_argument("sound_file", type=str)
    return parser.parse_args()


def assert_file_exists(filename: str):
    a = """
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx -O data/silero_vad.onnx
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/3dspeaker_speech_campplus_sv_zh_en_16k-common_advanced.onnx -O data/3dspeaker_speech_campplus_sv_zh_en_16k-common_advanced.onnx
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/3dspeaker_speech_eres2netv2_sv_zh-cn_16k-common.onnx -O data/3dspeaker_speech_eres2netv2_sv_zh-cn_16k-common.onnx
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad_v5.onnx -O data/silero_v
ad_v5.onnx
huggingface-cli download csukuangfj/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17 --local-dir sherpa-onnx-sense-voice
"""
    assert Path(
        filename
    ).is_file(), f"{filename} does not exist!\n Model prepare: \n{a}"


def create_recognizer(args) -> sherpa_onnx.OfflineRecognizer:
    if args.encoder:
        assert len(args.paraformer) == 0, args.paraformer
        assert len(args.sense_voice) == 0, args.sense_voice
        assert len(args.wenet_ctc) == 0, args.wenet_ctc
        assert len(args.whisper_encoder) == 0, args.whisper_encoder
        assert len(args.whisper_decoder) == 0, args.whisper_decoder

        assert_file_exists(args.encoder)
        assert_file_exists(args.decoder)
        assert_file_exists(args.joiner)

        recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=args.encoder,
            decoder=args.decoder,
            joiner=args.joiner,
            tokens=args.tokens,
            num_threads=args.num_threads,
            sample_rate=args.sample_rate,
            feature_dim=args.feature_dim,
            decoding_method=args.decoding_method,
            debug=args.debug,
        )
    elif args.paraformer:
        # assert len(args.sense_voice) == 0, args.sense_voice
        assert len(args.wenet_ctc) == 0, args.wenet_ctc
        assert len(args.whisper_encoder) == 0, args.whisper_encoder
        assert len(args.whisper_decoder) == 0, args.whisper_decoder

        assert_file_exists(args.paraformer)
        logger.info(f"loading paraformer model: {args.paraformer}")
        logger.info("auto assign decoder path.")

        args.tokens = Path(args.paraformer).parent.joinpath("tokens.txt").as_posix()
        logger.info(f"auto reassigned tokens: {args.tokens}")

        recognizer = sherpa_onnx.OfflineRecognizer.from_paraformer(
            paraformer=args.paraformer,
            tokens=args.tokens,
            num_threads=args.num_threads,
            sample_rate=args.sample_rate,
            feature_dim=args.feature_dim,
            decoding_method=args.decoding_method,
            debug=args.debug,
            provider="cuda",
        )
    elif args.wenet_ctc:
        assert len(args.whisper_encoder) == 0, args.whisper_encoder
        assert len(args.whisper_decoder) == 0, args.whisper_decoder

        assert_file_exists(args.wenet_ctc)

        recognizer = sherpa_onnx.OfflineRecognizer.from_wenet_ctc(
            model=args.wenet_ctc,
            tokens=args.tokens,
            num_threads=args.num_threads,
            sample_rate=args.sample_rate,
            feature_dim=args.feature_dim,
            decoding_method=args.decoding_method,
            debug=args.debug,
        )
    elif args.whisper_encoder:
        assert_file_exists(args.whisper_encoder)
        if not os.path.exists(args.whisper_decoder):
            logger.info("auto assign decoder path.")
            args.whisper_decoder = args.whisper_encoder.replace(
                "large-v3-encoder", "large-v3-decoder"
            )
            args.tokens = (
                Path(args.whisper_decoder)
                .parent.joinpath("large-v3-tokens.txt")
                .as_posix()
            )
            logger.info(f"token path: {args.tokens}")
        logger.info(
            f"loading whisper model.\nencoder:{args.whisper_encoder}\ndecoder:{args.whisper_decoder}"
        )

        recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=args.whisper_encoder,
            decoder=args.whisper_decoder,
            tokens=args.tokens,
            num_threads=args.num_threads,
            decoding_method=args.decoding_method,
            debug=args.debug,
            language=args.whisper_language,
            task=args.whisper_task,
            tail_paddings=args.whisper_tail_paddings,
        )
    elif args.sense_voice:
        assert len(args.wenet_ctc) == 0, args.wenet_ctc
        assert len(args.whisper_encoder) == 0, args.whisper_encoder
        assert len(args.whisper_decoder) == 0, args.whisper_decoder

        assert_file_exists(args.sense_voice)
        recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
            model=args.sense_voice,
            tokens=args.tokens,
            num_threads=args.num_threads,
            use_itn=True,
            debug=args.debug,
        )
    else:
        raise ValueError("Please specify at least one model")

    return recognizer


@dataclass
class Segment:
    start: float
    duration: float
    text: str = ""
    name: str = "unkown"

    @property
    def end(self):
        return self.start + self.duration

    def __str__(self):
        s = f"{timedelta(seconds=self.start)}"[:-3]
        s += " --> "
        s += f"{timedelta(seconds=self.end)}"[:-3]
        s = s.replace(".", ",")
        s += "\n"
        s += self.text
        return s


def load_speaker_embedding_model(args):
    config = sherpa_onnx.SpeakerEmbeddingExtractorConfig(
        model=args.speaker_model,
        num_threads=args.num_threads,
        debug=args.debug,
        # provider=args.provider,
    )
    if not config.validate():
        raise ValueError(f"Invalid config. {config}")
    extractor = sherpa_onnx.SpeakerEmbeddingExtractor(config)
    return extractor


def load_speaker_file(args) -> Dict[str, List[str]]:
    if not Path(args.speaker_file).is_file():
        raise ValueError(
            f"--speaker-file {args.speaker_file} does not exist, speaker txt file contains like:\n小明 /path/a.wav\n小黄 /path/b.wav\n"
        )
    logger.info(f"load speakers txt from: {args.speaker_file}")
    ans = defaultdict(list)
    with open(args.speaker_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            fields = line.split()
            if len(fields) != 2:
                raise ValueError(f"Invalid line: {line}. Fields: {fields}")

            speaker_name, filename = fields
            ans[speaker_name].append(filename)
    return ans


def load_audio(filename: str) -> Tuple[np.ndarray, int]:
    data, sample_rate = sf.read(
        filename,
        always_2d=True,
        dtype="float32",
    )
    data = data[:, 0]  # use only the first channel
    samples = np.ascontiguousarray(data)
    return samples, sample_rate


def compute_speaker_embedding(
    filenames: List[str],
    extractor: sherpa_onnx.SpeakerEmbeddingExtractor,
) -> np.ndarray:
    assert len(filenames) > 0, "filenames is empty"

    ans = None
    for filename in filenames:
        print(f"processing {filename}")
        samples, sample_rate = load_audio(filename)
        stream = extractor.create_stream()
        stream.accept_waveform(sample_rate=sample_rate, waveform=samples)
        stream.input_finished()

        assert extractor.is_ready(stream)
        embedding = extractor.compute(stream)
        embedding = np.array(embedding)
        if ans is None:
            ans = embedding
        else:
            ans += embedding

    return ans / len(filenames)


def save_to_csv(data, filename):
    def format_timestamp(seconds):
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int(td.microseconds / 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["index", "字幕时间戳", "翻译字幕", "中文字幕", "角色"])
        for index, entry in enumerate(data):
            start_timestamp = format_timestamp(entry["start_t"])
            end_timestamp = format_timestamp(entry["end_t"])
            subtitle_timestamp = f"{start_timestamp} --> {end_timestamp}"
            translated_subtitle = "''"
            chinese_subtitle = entry["text"]
            role = entry["speaker_name"]

            writer.writerow(
                [index, subtitle_timestamp, translated_subtitle, chinese_subtitle, role]
            )


def main():
    args = get_args()
    assert_file_exists(args.tokens)
    assert_file_exists(args.silero_vad_model)

    assert args.num_threads > 0, args.num_threads

    if not Path(args.sound_file).is_file():
        raise ValueError(f"{args.sound_file} does not exist")

    assert (
        args.sample_rate == 16000
    ), f"Only sample rate 16000 is supported.Given: {args.sample_rate}"

    segment_list = []
    results_json = []

    res_filename = Path(args.sound_file).with_suffix(".json")
    if res_filename.exists():
        logger.info("loaded existed result")
        results_json = json.load(open(res_filename, "r"))["data"]
    else:
        recognizer = create_recognizer(args)

        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            args.sound_file,
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            str(args.sample_rate),
            "-",
        ]

        process = subprocess.Popen(
            ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )

        frames_per_read = int(args.sample_rate * 100)  # 100 second

        stream = recognizer.create_stream()

        config = sherpa_onnx.VadModelConfig()
        config.silero_vad.model = args.silero_vad_model
        # config.silero_vad.min_silence_duration = 0.25
        # config.silero_vad.min_silence_duration = 0.8  # for tv drama longer
        # config.silero_vad.min_silence_duration = 0.42  # for tv drama longer
        config.silero_vad.min_silence_duration = 0.34  # for tv drama longer
        config.sample_rate = args.sample_rate

        window_size = config.silero_vad.window_size

        buffer = []
        vad = sherpa_onnx.VoiceActivityDetector(config, buffer_size_in_seconds=100)

        # speaker identification model
        if args.speaker_file is not None:
            extractor = load_speaker_embedding_model(args)
            speaker_file = load_speaker_file(args)
            manager = sherpa_onnx.SpeakerEmbeddingManager(extractor.dim)
            for name, filename_list in speaker_file.items():
                embedding = compute_speaker_embedding(
                    filenames=filename_list,
                    extractor=extractor,
                )
                status = manager.add(name, embedding)
                if not status:
                    raise RuntimeError(f"Failed to register speaker {name}")
            logger.success("speakers registered success.")

        logger.info("Started!")
        is_silence = False
        while True:
            # *2 because int16_t has two bytes
            data = process.stdout.read(frames_per_read * 2)
            if not data:
                if is_silence:
                    break
                is_silence = True
                # The converted audio file does not have a mute data of 1 second or more at the end, which will result in the loss of the last segment data
                data = np.zeros(1 * args.sample_rate, dtype=np.int16)

            samples = np.frombuffer(data, dtype=np.int16)
            samples = samples.astype(np.float32) / 32768

            buffer = np.concatenate([buffer, samples])
            while len(buffer) > window_size:
                vad.accept_waveform(buffer[:window_size])
                buffer = buffer[window_size:]

            if is_silence:
                vad.flush()

            streams = []
            streams_extactor = []
            segments: List[Segment] = []
            while not vad.empty():
                segment = Segment(
                    start=vad.front.start / args.sample_rate,
                    duration=len(vad.front.samples) / args.sample_rate,
                )
                segments.append(segment)

                stream = recognizer.create_stream()
                stream.accept_waveform(args.sample_rate, vad.front.samples)
                streams.append(stream)

                if args.speaker_file is not None:
                    stream2 = extractor.create_stream()
                    stream2.accept_waveform(args.sample_rate, vad.front.samples)
                    streams_extactor.append(stream2)

                vad.pop()

            # print(streams)
            for s in streams:
                recognizer.decode_stream(s)

            # matching speaker
            if args.speaker_file is not None:
                names = []
                for s in streams_extactor:
                    # add for speaker identification
                    embedding = extractor.compute(s)
                    embedding = np.array(embedding)
                    name = manager.search(embedding, threshold=args.threshold)
                    if not name:
                        name = "未知"
                    names.append(name)

            if args.speaker_file is not None:
                for seg, stream, name in zip(segments, streams, names):
                    seg.text = stream.result.text
                    segment_list.append(seg)

                    a = {
                        "speaker_name": name,
                        "start_t": seg.start,
                        "end_t": seg.end,
                        "duration": seg.duration,
                        "text": seg.text,
                    }
                    results_json.append(a)
            else:
                for seg, stream in zip(segments, streams):
                    seg.text = stream.result.text
                    segment_list.append(seg)

                    a = {
                        "start_t": seg.start,
                        "end_t": seg.end,
                        "duration": seg.duration,
                        "text": seg.text,
                    }
                    results_json.append(a)

        results = {"filename": args.sound_file, "data": results_json}
        if args.speaker_file is not None:
            with open(res_filename, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                logger.success(f"result json saved into: {res_filename}")
        srt_filename = Path(args.sound_file).with_suffix(".srt")
        with open(srt_filename, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segment_list):
                print(i + 1, file=f)
                print(seg, file=f)
                print("", file=f)
        logger.success(f"Saved to {srt_filename}")

    # last convert
    if args.speaker_file is not None:
        save_to_csv(results_json, Path(args.sound_file).with_suffix(".csv"))
    logger.success("done.")


if __name__ == "__main__":
    if shutil.which("ffmpeg") is None:
        sys.exit("Please install ffmpeg first!")
    main()
