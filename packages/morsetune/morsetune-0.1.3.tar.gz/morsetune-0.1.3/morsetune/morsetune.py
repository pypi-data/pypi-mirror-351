import numpy as np

class MorseTune:
    SPS = 8000              # samples per second
    FREQ = 750              # frequency
    WPM = 12                # words per minute
    DPS = WPM * 50 / 60.0   # dots per second
    AUDIO_PADDING = 0.5     # in seconds
    CLICK_SMOOTH = 2        # tone periods

    def __getArrayByMorse(self, code):
        count = int(self.SPS / self.DPS)
        dot = np.ones(count * 1, bool)
        dash = np.ones(count * 3, bool)
        gap = np.zeros(count * 1, bool)
        char = np.zeros(count * 3, bool)
        word = np.zeros(count * 7, bool)
        pieces = []
        wasSpace = False
        wasElement = False
        for c in code:
            if c == '.':
                if wasElement:
                    pieces.append(gap)
                pieces.append(dot)
                wasSpace, wasElement = False, True
            elif c == '-':
                if wasElement:
                    pieces.append(gap)
                pieces.append(dash)
                wasSpace, wasElement = False, True
            else:
                if wasSpace:
                    pieces[-1] = word
                else:
                    pieces.append(char)
                wasSpace, wasElement = True, False
        return np.concatenate(pieces)

    def __getToneByArray(self, array):
        length = int(self.CLICK_SMOOTH * self.SPS / self.FREQ)
        if length % 2 == 0:
            length += 1
        smoothing = np.concatenate((np.arange(1, length // 2 + 1), np.arange(length // 2 + 1, 0, -1)))
        smoothing = smoothing / np.sum(smoothing)
        padding = np.zeros(int(self.SPS * self.AUDIO_PADDING) + int((length - 1) / 2), bool)
        array = np.concatenate((padding, array, padding)).astype(np.float32)
        array = np.correlate(array, smoothing, 'valid')
        sample = np.arange(len(array))
        tone = np.sin(sample * (self.FREQ * 2 * np.pi / self.SPS))
        tone *= array
        return tone

    def convert(self, morse):
        array = self.__getArrayByMorse(morse)
        audio = self.__getToneByArray(array)

        return audio