"""
The audio of a video is a numpy array with the
shape (n_samples, n_channels):
- n_samples: number of audio frames.
- n_channels: 1 (mono) or 2 (stereo)

Also, the array includes (ideally) values between
-1.0 and 1.0, being 0.0 the silence.
"""
from dataclasses import dataclass

import numpy as np


@dataclass
class AudioFrame:
    """
    Class to represent an audio frame, to simplify the
    way we modify it. An audio frame is a numpy array.
    """

    @property
    def number_of_channels(
        self
    ) -> int:
        """
        The number of channels of the audio frame.
        """
        shape = self.frame.shape

        return (
            1
            if len(shape) == 1 else
            shape[1]
        )

    @property
    def number_of_samples(
        self
    ) -> int:
        """
        The number of samples in the audio frame.
        """
        return self.frame.shape[0]

    @property
    def is_mono(
        self
    ) -> bool:
        """
        Check if the audio frame is mono (includes
        only one channel) or not.
        """
        return self.number_of_channels == 1
    
    @property
    def is_stereo(
        self
    ) -> bool:
        """
        Check if the audio frame is stereo (includes
        two channels) or not.
        """
        return self.number_of_channels == 2
    
    def __init__(
        self,
        frame: np.ndarray
    ):
        # TODO: Do more things here
        self.frame = frame
        """
        A numpy array containing the audio for this frame.
        """
        if (
            not self.is_mono and
            not self.is_stereo
        ):
            raise Exception('The format is unexpected, no mono nor stereo audio.')

# TODO: Test with a real audio and add more functions

# audio = clip.audio
# samples = audio.to_soundarray(fps=44100)