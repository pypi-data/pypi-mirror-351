import os
from pprint import pprint
from ultracutpro.ai.vision.base import MLLMClient
from ultracutpro.ai.vision.utils import process_video_fixed_frames, resize_frames
import time
import textwrap

api_key = os.environ["api_key"]
api_secret = os.environ["api_secret"]
mllm = MLLMClient(
    api_key=api_key,
    api_secret=api_secret,
    group_id="876",
    # provider="openai",
    provider="mllm_serving",
    base_url="http://0.0.0.0:8000/v1",
)


def test_mllm():
    system = textwrap.dedent(
        """你是一位专业的图像场景分析专家，专注于按照提供的图片输出关于场景的内容理解。
    你的任务是输出：
    - 细致描绘什么样穿着的什么性别的人物再进行什么样的对话、活动、或者互动，再描绘他们的表情、推测活动内容；
    - 场景的描述以及中代表性的元素
    列点描述即可，不要用markdown，语言要简单干练，突出重点和细节。
    """
    )

    images = [
        "raw/images/l41000sbn89[00_20_34][20240801-165406].png",
        # "raw/images/l41000sbn89[00_22_10][20240801-165359].png",
        "raw/images/l41000sbn89[00_32_00][20240801-164735].png",
        # "raw/images/l41000sbn89[00_33_03][20240801-165350].png",
        "raw/images/l41000sbn89[00_37_22][20240801-164756].png",
        # "raw/images/l41000sbn89[00_44_38][20240801-165342].png",
        # "raw/images/l41000sbn89[00_59_51][20240801-165130].png",
        # "raw/images/l41000sbn89[00_59_53][20240801-165142].png",
        # "raw/images/l41000sbn89[01_19_00][20240801-165158].png",
        # "raw/images/l41000sbn89[01_24_24][20240801-165209].png",
    ]

    for img in images:
        print("-" * 100, f"image: {img}")
        t0 = time.time()
        a = mllm.get_response_no_stream(
            system,
            [img],
            # system=system,
        )
        t1 = time.time()
        print(f"cost time: {t1 - t0}, prompts: {len(a)}, token/s: {len(a) / (t1 - t0)}")
        print(a)


def test_mllm2():
    system = textwrap.dedent(
        """你是一位专业的图像场景分析专家，下面会给你一个短的视频，描述出改场景进行的活动。
    你的任务是输出：
    - 细致描绘什么样穿着的什么性别的人物再进行什么样的对话、活动、或者互动，再描绘他们的表情、推测活动内容；
    - 场景的描述以及中代表性的元素
    用一段文字描绘视频所进行的内容，要有叙事情节，完整的展现整个序列展示的活动场景，精确描绘每个人的人物动作和活动。
    """
    )

    images = [
        # "raw/images/l41000sbn89[00_20_34][20240801-165406].png",
        # "raw/images/l41000sbn89[00_22_10][20240801-165359].png",
        "raw/images/l41000sbn89[00_32_00][20240801-164735].png",
        "raw/images/l41000sbn89[00_33_03][20240801-165350].png",
        # "raw/images/l41000sbn89[00_37_22][20240801-164756].png",
        "raw/images/l41000sbn89[00_44_38][20240801-165342].png",
        "raw/images/l41000sbn89[00_59_51][20240801-165130].png",
        # "raw/images/l41000sbn89[00_59_53][20240801-165142].png",
        # "raw/images/l41000sbn89[01_19_00][20240801-165158].png",
        # "raw/images/l41000sbn89[01_24_24][20240801-165209].png",
    ]

    t0 = time.time()
    a = mllm.get_response_no_stream(
        system,
        images,
        # system=system,
    )
    t1 = time.time()
    print(f"cost time: {t1 - t0}, prompts: {len(a)}, token/s: {len(a) / (t1 - t0)}")
    print(a)


def test_video():
    system = textwrap.dedent(
        """你是一位专业的图像场景分析专家，下面会给你一个短的视频，描述出改场景进行的活动。
    你的任务是输出：
    - 细致描绘出视频中的情节、不同人物之间的互动，以及每个人物穿着，请注意不同画面之间相同人物的动作连续性；
    - 场景的描述以及中代表性的元素
    用一段文字描绘视频所进行的内容，要有叙事情节，完整的展现整个序列展示的活动场景，精确描绘每个人的人物动作和活动。
    """
    )

    video_file = "raw/images/l41000sbn89 截取视频 截取视频.mp4"
    images = process_video_fixed_frames(video_file=video_file, fps=1, num_frames=5)
    images = resize_frames(images)

    t0 = time.time()
    a = mllm.get_response_no_stream(
        system,
        images,
        # system=system,
    )
    t1 = time.time()
    print(f"cost time: {t1 - t0}, prompts: {len(a)}, token/s: {len(a) / (t1 - t0)}")
    print(a)


if __name__ == "__main__":
    # test_mllm2()
    # test_video()
    test_mllm()
