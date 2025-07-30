# from mllm_serving.api import MLLMServing
import json
import os
from pprint import pprint

import cv2
import numpy as np
from ultracutpro.ai.vision.base import MLLMClient
import time
from ultracutpro.ai.vision.face_recog import FaceRecog
from ultracutpro.mediaprocess.ffmpeg_processor import VideoOp
from ultracutpro.ai.agent_translate import TranslateAgent
from pprint import pprint
from audiotool.utils import normalize_audio_to_target


def test_serving():
    api_key = os.environ["api_key"]
    # api_key = ""  # hunyuan-vision
    api_secret = os.environ["api_secret"]

    m = MLLMClient(
        api_key=api_key,
        api_secret=api_secret,
        group_id="876",
        # provider="openai",
        provider="mllm_serving",
        # base_url="http://0.0.0.0:8888/v1",
        # base_url="http://127.0.0.1:8888/v1",
    )
    # vp = VideoOp('temp/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min_470040.0_553080.0_keys.mp4')
    # vp = VideoOp(
    #     # "temp/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min_586200.0_432600.0_keys.mp4"
    #     "temp/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min_529560.0_435960.0_keys.mp4"
    # )
    # # frames = vp.get_frames_to_np(target_size_h=None)
    # frames = vp.get_frames_to_np(target_size_w=448, target_size_h=None)
    # print(f"frames: {len(frames)} {frames[0].shape}")

    res = m.get_response_no_stream(
        # "描述一下这张图片", "data/images/gt_10027.jpg", model="internvl-26b"
        # "描述一下这张图片", "data/images/gt_10027.jpg", model="gpt-4o"
        # "描述一下这张图片", "data/images/gt_10027.jpg", model="gemini-1.5-pro"
        # "根据编号描述一下图片内容，简单的一段话即可，充分表现出图中人物动作表情和活动",
        """你是一位资深的场景和人物互动分析师，你可以根据给定的若干帧视频，完整推断人物动作、活动、场景以及人物和场景相关的细节，并完整的简明扼要地阐述。
    我会给你一个视频（视频中人物我都用方框标注了名字，请直接根据人物名字来描绘）。
    你的任务是输出：
    - 视频中主体或说话人的动作、表情、神态、穿着细节，用简短的一段话描述视频里面人在干什么；
    - 着重描述主体人物的动作、表情、穿着，以及整体场景的可能爆点；

    你需要注意的点：
    - 视频人物描述请直接以姓名的形式给出，要非常自然通过姓名描述人物之间的活动以及人物本身；
    - 你的输出是一段话；
    - 视频变化可能较快，请合理的根据画面变化推断；
    - 人物指代不要用第三人称；
    - 请不要幻觉，请注意视频活动的连续性，根据连续性推断人物动作；
            """,
        [
            # "data/images/gt_10027.jpg",
            # "temp/l41000sbn89[01_24_24][20240801-165209]_out.jpg",
            "data/images/gt_10019.jpg",
        ],
        # frames[:12],
        model="gemini-1.5-flash",
        # model="hunyuan-vision",
        # model='247223'
    )

    # res = m.get_response_no_stream(
    #     "根据编号描述一下图片内容，简单的一段话即可，充分表现出图中人物动作表情和活动。请根据人脸检测的人名用名字对应人物。",
    #     [
    #         # "data/images/gt_10027.jpg",
    #         # "temp/l41000sbn89[01_24_24][20240801-165209]_out.jpg",
    #         "temp/ci46h2leuhfi85cfbn80[00_29_19][20240809-161624].png.jpg",
    #     ],
    #     # frames,
    #     # model="gemini-1.5-flash",
    #     model="hunyuan-vision",
    # )
    print(res)


def test_mllm():
    mllm = MLLMClient(base_url="http://0.0.0.0:8000/v1")
    t0 = time.time()
    a = mllm.get_response_no_stream(
        "第二张图片店铺可以提供哪些服务？第一张图可能是哪个地方？",
        ["data/images/gt_10027.jpg", "data/images/gt_10019.jpg"],
    )
    t1 = time.time()
    print(f"cost time: {t1 - t0}")
    print(a)


def test_face():
    fr = FaceRecog(face_lib_dir="raw/faces/少年行v2")

    # a = fr.get_faces_and_names('raw/data/test/ci46euleuhfi85cfapi0[00_24_14][20240809-162100].png')
    # a = fr.get_faces_and_names('raw/data/test/ci46euleuhfi85cfapi0[00_25_33][20240809-162114].png')
    # a, b = fr.get_faces_and_names('raw/data/test/ci46h2leuhfi85cfbn80[00_26_11][20240809-161610].png')
    # a, b = fr.get_faces_and_names('raw/data/test/ci46h2leuhfi85cfbn80[00_29_19][20240809-161624].png')
    # a, b = fr.get_faces_and_names('raw/data/test/ci46h2leuhfi85cfbn80[01_04_43][20240809-161638].png')
    # a, b = fr.get_faces_and_names('raw/data/test/ci46h2leuhfi85cfbn80[01_44_36][20240809-161647].png')
    a, b = fr.get_faces_and_names(
        "raw/data/test/ci46h2leuhfi85cfbn80[01_51_20][20240809-161651].png"
    )
    print(a)


def test_tts():
    from ultracutpro.ai.voice.edgetts import tts_for_srt
    import sys

    srt_file = sys.argv[1]
    a = tts_for_srt(srt_file, "male-zh-CN-YunxiNeural", 1.0)
    print(a)


def test_blur():
    # i = 'temp/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min/keyframe_00100.jpg' # 147
    i = "temp/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min/keyframe_00203.jpg"  # 259
    i = "temp/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min/keyframe_00211.jpg"  # 188
    i = "temp/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min/keyframe_00227.jpg"  # 189
    i = "temp/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min/keyframe_00055.jpg"  # 114
    i = "temp/ci46h2leuhfi85cfbn80_0515-初舞台-CAM6-_test0_10min/keyframe_00099.jpg"  # 113
    frame = cv2.imread(i)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray_frame, cv2.CV_64F).var()
    print(laplacian_var)


def test_translate():
    c = TranslateAgent(
        provider="mllm_serving",
        group_id=876,
        default_model="gpt-4o",
    )
    # a = c.translate("am from new yorl", "", "zh")
    # a = c.translate("是的，没错", "", "en")
    with open("temp/yyxh1/target_results.json", "r") as f:
        segments = json.load(f)
    a = c.batch_translate_segments(segments=segments, target_lan="en")
    pprint(a)


def test_pywhisper():
    from pywhispercpp.model import Model

    # model = Model('base.en', n_threads=6)
    model = Model("large-v3-turbo", n_threads=6)

    audio_f = "temp/yyxh3_1206/parts_asr/50.9_51.4.wav"
    # audio_f = "temp/yyxh3_1206/extracted_audio_clean.wav"
    audio_f = "temp/yyxh1_1210/extracted_audio_clean.wav"
    # audio_f = "temp/yyxh3_1206/extracted_audio_clean.wav"
    # audio_f = "data/audios/10.0.wav"
    # audio_f = "data/lei-jun-test.wav"
    audio_f = normalize_audio_to_target(audio_f)
    print(audio_f)
    # model = Model('checkpoints/belle_whisper_v3_turbo_ggml/ggml-model.bin', n_threads=6)
    # segments = model.transcribe('data/lei-jun-test.wav')
    # segments = model.transcribe('temp/yyxh3_1206/extracted_audio_clean.wav')
    # segments = model.transcribe('temp/yyxh3_1206/extracted_audio.wav')
    segments = model.transcribe(audio_f, language="zh")
    for segment in segments:
        print(segment.text)


def test_whisper():
    from transformers import pipeline

    transcriber = pipeline(
        "automatic-speech-recognition",
        # model="checkpoints/Belle-whisper-large-v3-turbo-zh",
        model="checkpoints/whisper-large-v3-turbo",
    )

    transcriber.model.config.forced_decoder_ids = (
        transcriber.tokenizer.get_decoder_prompt_ids(language="zh", task="transcribe")
    )

    # audio_f = "temp/yyxh3_1206/parts_asr/50.9_51.4.wav"
    audio_f = "temp/yyxh3_1206/extracted_audio_clean.wav"
    audio_f = "data/audios/10.0.wav"
    # audio_f = "data/lei-jun-test.wav"
    audio_f = normalize_audio_to_target(audio_f)
    print(audio_f)

    # segments = transcriber(audio_f, return_timestamps=True)
    segments = transcriber(audio_f, return_timestamps=False)
    print(segments)
    for segment in segments["chunks"]:
        print(segment)


def test_punc():
    from ultracutpro.ai.voice.paramformer_ort import PuncModel

    # text_in = "跨境河流是养育沿岸人民的生命之源长期以来为帮助下游地区防灾减灾中方技术人员在上游地区极为恶劣的自然条件下克服巨大困难甚至冒着生命危险向印方提供汛期水文资料处理紧急事件中方重视印方在跨境河流问题上的关切愿意进一步完善双方联合工作机制凡是中方能做的我们都会去做而且会做得更好我请印度朋友们放心中国在上游的任何开发利用都会经过科学规划和论证兼顾上下游的利益"
    text_in = "你信不信我只要动一个小手指头即可当平梁山片甲不留"

    punc = PuncModel()
    punc.add_punc(text_in, split_size=3)


def test_pixit():
    # instantiate the pipeline
    from pyannote.audio import Pipeline
    from pyannote.audio import Model

    pipeline = Pipeline.from_pretrained(
        checkpoint_path="pyannote/speech-separation-ami-1.0",
        use_auth_token="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",
        cache_dir="checkpoints/pyannote",
    )

    # run the pipeline on an audio file
    # audio_f = "data/audios/overlap/54.8_59.6.wav"
    # audio_f = "data/audios/overlap/67.0_70.5.wav"
    audio_f = "data/audios/overlap/75.8_79.3.wav"
    audio_f = normalize_audio_to_target(audio_f)
    diarization, sources = pipeline(audio_f)

    # dump the diarization output to disk using RTTM format
    print(diarization)

    # dump sources to disk as SPEAKER_XX.wav files
    import scipy.io.wavfile

    for s, speaker in enumerate(diarization.labels()):
        scipy.io.wavfile.write(
            os.path.join(os.path.dirname(audio_f), f"{speaker}.wav"),
            16000,
            sources.data[:, s],
        )


def test_scd():
    from pyannote.audio import Pipeline
    from pyannote.audio import Model
    from pyannote.audio import Inference

    import os
    from pathlib import Path
    import soundfile as sf
    from pydub import AudioSegment

    def save_segments_as_wav(audio_file_path, segments):
        # Get the directory of the audio file
        audio_dir = Path(audio_file_path).parent

        # Create the pyannot_seg folder if it doesn't exist
        output_dir = audio_dir / f"pyannot_seg_{os.path.basename(audio_file_path)}"
        output_dir.mkdir(exist_ok=True)

        # Load the audio file
        audio = AudioSegment.from_wav(audio_file_path)

        # Iterate through the segments and save each as a WAV file
        for i, segment in enumerate(segments):
            start_ms = int(segment.start * 1000)  # Convert seconds to milliseconds
            end_ms = int(segment.end * 1000)

            # Extract the segment
            segment_audio = audio[start_ms:end_ms]

            # Generate the output file name
            output_file = output_dir / f"segment_{i+1:03d}.wav"

            # Export the segment as WAV
            segment_audio.export(output_file, format="wav")

            print(f"Saved segment {i+1} to {output_file}")

    # pipeline = Model.from_pretrained(
    #     # checkpoint_path="pyannote/speech-separation-ami-1.0",
    #     checkpoint="pyannote/speaker-segmentation",
    #     use_auth_token="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",
    #     cache_dir="checkpoints/pyannote",
    # )

    # run the pipeline on an audio file
    # audio_f = "data/audios/overlap/54.8_59.6.wav"
    # audio_f = "temp/九条命群像封神之作《_006_516.4_615.2_1213/extracted_audio_clean.wav"
    audio_f = "temp/九条命群像封神之作《_006_516.4_615.2_1213/short.wav"
    # audio_f = "data/audios/overlap/67.0_70.5.wav"
    # audio_f = "data/audios/overlap/75.8_79.3.wav"
    audio_f = normalize_audio_to_target(audio_f)
    # diarization, sources = pipeline(audio_f)

    BATCH_AXIS = 0
    TIME_AXIS = 1
    SPEAKER_AXIS = 2

    to_scd = lambda probability: np.max(
        np.abs(np.diff(probability, n=1, axis=TIME_AXIS)),
        axis=SPEAKER_AXIS,
        keepdims=True,
    )
    scd = Inference(
        "pyannote/segmentation",
        use_auth_token="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",
        pre_aggregation_hook=to_scd,
    )
    scd_prob = scd(audio_f)

    # dump the diarization output to disk using RTTM format
    print(scd_prob)

    from pyannote.audio.utils.signal import Peak

    peak = Peak(alpha=0.05)
    # scd = peak(scd_prob).crop(speech.get_timeline())
    scd = peak(scd_prob)

    print(scd)

    # dump sources to disk as SPEAKER_XX.wav files
    import scipy.io.wavfile

    save_segments_as_wav(audio_f, scd)


if __name__ == "__main__":
    # test_translate()
    # test_pywhisper()
    # test_pixit()
    test_scd()
    # test_whisper()
    # test_punc()
    # test_serving()

    # test_face()
    # test_tts()
    # test_blur()
