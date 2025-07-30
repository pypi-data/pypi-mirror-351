from .fsmnvad.fsmnvad import FSMNVad


class VADFsmn:

    def __init__(self) -> None:
        self.model = FSMNVad()

    def get_timestamps(self, audio, threshold=0.5, speech_pad_ms=30):
        speech_timestamps = self.model.segments_offline(audio)
        final_res = []
        for itm in speech_timestamps:
            final_res.append(
                {"start": round(itm[0] / 1000, 2), "end": round(itm[1] / 1000, 2)}
            )
        return final_res
