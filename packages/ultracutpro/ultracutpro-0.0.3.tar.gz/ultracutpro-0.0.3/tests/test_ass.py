from ultracutpro.cutter.cutter_utils import print_subtitle_with_ass


if __name__ == "__main__":
    src_video_f = "temp/d0040i9tzjd/m_merge_subtitle1.mp4"
    # srt_f = "raw/sources/d0040oylx81_5882160_6090680.srt"
    srt_f = "temp/d0040i9tzjd/subtitle/a.ass"
    print_subtitle_with_ass(src_video_f, srt_f, "temp/a.mp4")
