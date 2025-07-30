import torchaudio
from ultracutpro.ai.voice.one_tts import TTSOne
from audio_separator.separator import Separator
from speechbrain.inference.separation import SepformerSeparation as sepformer


def test_vocal_remover():
    separator = Separator()
    separator.load_model("UVR-MDX-NET-Inst_HQ_3.onnx")

    output_files = separator.separate(
        "temp/270268822-1-208/parts/92.5.wav",
        primary_output_name="temp/primary",
        secondary_output_name="temp/ssec",
    )
    print(f"Separation complete! Output file(s): {' '.join(output_files)}")


def test():
    a = TTSOne(base_url="http://127.0.0.1:8088")

    text = "如果不能跟我喜欢的人在一起，就算让我做玉皇大帝我也不会开心。做人不快乐，长生不老又有什么用。我猜中了开头，却猜不中这结局。"
    # target_len = 6
    # target_len = 12
    target_len = 18

    prompt_wav = "data/zero_shot_prompt.wav"
    prompt_text = "希望你以后能够做到比我还好哟"

    output_path = f"output/test_out_{target_len}.wav"
    a.tts_clone(
        text=text,
        prompt_wav=prompt_wav,
        prompt_text=prompt_text,
        target_lan="zh",
        target_length=target_len,
        save_path=output_path,
    )


def test_separation():
    """
    Find a way to separate 2 speak (more) their own audio
    so that each one can be used to generate voice?
    """
    model = sepformer.from_hparams(
        source="speechbrain/sepformer-wham16k-enhancement",
        savedir="checkpoints/sepformer-wham16k-enhancement",
    )

    # for custom file, change path
    est_sources = model.separate_file(
        # path="speechbrain/sepformer-wham16k-enhancement/example_wham16k.wav"
        path="temp/11_1123_21/parts/131.1.wav"
    )
    print(est_sources.shape)
    torchaudio.save("enhanced_wham16k.wav", est_sources[:, :, 0].detach().cpu(), 16000)


# test()
# test_vocal_remover()
test_separation()
