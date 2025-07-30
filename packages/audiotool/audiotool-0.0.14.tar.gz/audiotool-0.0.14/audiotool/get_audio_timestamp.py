import os
import json
import sys


def video_to_audio(video_file, format):
    t = os.path.join(
        os.path.dirname(video_file),
        f'{os.path.basename(video_file).split(".")[0]}.{format}',
    )
    os.system(f"ffmpeg -hide_banner -loglevel error -i {video_file} {t}")
    return t


def get_audio_by_timestamp(s, e, video_file, prefix):
    """
    :param s: 开始时间，单位ms
    :param e: 结束时间，单位ms
    :param video_file: 视频文件路径
    :return: 音频文件路径
    """
    os.makedirs("tmp", exist_ok=True)
    save_path = os.path.join("tmp", f"{prefix}_audio.mp3")
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if os.path.exists(save_path):
        os.remove(save_path)

    if video_file.lower().endswith(".mp4"):
        # If it's an MP4 file, extract the audio and save it as an MP3 file
        os.system(
            f'ffmpeg -ss {s/1000} -to {e/1000} -i "{video_file}" -f mp3 -copyts "{save_path}" -y'
        )
    elif video_file.lower().endswith(".mp3"):
        # If it's an MP3 file, cut the audio and save it as an MP3 file
        os.system(
            f'ffmpeg -ss {s/1000} -to {e/1000} -i "{video_file}" -acodec copy "{save_path}" -y'
        )
    else:
        print("Unsupported file type. Please provide an MP3 or MP4 file.")
    return save_path


def extract_audio_to_file(s, e, source_file, save_file):
    """
    :param s: 开始时间，单位s
    :param e: 结束时间，单位s
    :param video_file: 视频文件路径
    :return: 音频文件路径
    """

    if source_file.lower().endswith(".mp4"):
        # If it's an MP4 file, extract the audio and save it as an MP3 file
        os.system(
            f'ffmpeg -ss {s} -to {e} -i "{source_file}" -f mp3 -copyts "{save_file}" -y'
        )
    elif source_file.lower().endswith(".mp3"):
        # If it's an MP3 file, cut the audio and save it as an MP3 file
        os.system(
            f'ffmpeg -hide_banner -loglevel error -ss {s} -to {e} -i "{source_file}" -acodec copy "{save_file}" -y'
        )
    elif source_file.lower().endswith(".wav"):
        # If it's an MP3 file, cut the audio and save it as an MP3 file
        os.system(f'ffmpeg -ss {s} -to {e} -i "{source_file}" "{save_file}" -y')
    else:
        print("Unsupported file type. Please provide an MP3 or MP4 file.")
    return save_file


def convert_to_milliseconds(timestamp):
    parts = timestamp.split(":")
    minutes = int(parts[0])
    seconds, milliseconds = map(int, parts[1].split("."))
    total_milliseconds = (minutes * 60 * 1000) + (seconds * 1000) + milliseconds
    return total_milliseconds


if __name__ == "__main__":
    """
    {"startTime":269100,"endTime":270370,"content":{"component":{"asrkey":"被狗揍了"},
    {"startTime":273815,"endTime":275435,"content":{"component":{"asrkey":"是带他去绝育去了"},
    {"startTime":280080,"endTime":282020,"content":{"component":{"asrkey":"关键它反应太快了"},
    {"startTime":1126990,"endTime":1128230,"content":{"component":{"asrkey":"他们都有名称"},"confidence":100,

    {"startTime":950590,"endTime":953900,"content":{"component":{"asrkey":"你别老就艾伦一个人有权住"}
    {"startTime":969710,"endTime":971340,"content":{"component":{"asrkey":"我跟冰我俩去吧"}
    {"startTime":1130085,"endTime":1131920,"content":{"component":{"asrkey":"别都可一个屋挤了"},
    """

    # speaker_mapper = {
    #     '金晨': [[269100, 270370], [273815, 275435], [280080, 282020], [1126990, 1128230]],
    #     '沈腾': [[950590, 953900], [969710, 971340], [1130085, 1131920]]
    # }
    video_f = sys.argv[1]

    # for k, v in speaker_mapper.items():
    #     for i, ad in enumerate(v):
    #         get_audio_by_timestamp(ad[0], ad[1], video_file=video_f, prefix=f'{k}_{i}')

    # get all audio
    data_f = sys.argv[2]
    vid = os.path.basename(data_f).split(".")[0]
    res = json.load(open(data_f, "r", encoding="utf-8"))
    # res = a['results']
    print(len(res))
    for i, vd in enumerate(res):
        s = vd["startTime"]
        e = vd["endTime"]
        print(type(s))
        if isinstance(s, str):
            s = convert_to_milliseconds(s)
            e = convert_to_milliseconds(e)

        p = int(e) / 1000 - int(s) / 1000
        # if p > 5:
        si = int(s) / 1000
        ei = int(e) / 1000
        get_audio_by_timestamp(
            s, e, video_file=video_f, prefix=f"tmp/{vid}_{int(si)}-{int(ei)}_{i}"
        )
