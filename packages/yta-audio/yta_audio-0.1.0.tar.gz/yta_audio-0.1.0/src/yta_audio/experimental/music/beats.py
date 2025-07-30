from yta_programming.decorators.requires_dependency import requires_dependency


@requires_dependency('librosa', 'yta_audio', 'librosa')
def get_song_tempo_and_beats(
    filename: str
):
    """
    Analyzes the provided song 'filename' and returns a dict that
    contains the song estimated 'tempo' and 'beats' time moments
    (in seconds).

    @param
        **filename**
        The filename of a file that contains a song to be analyzed.
    """
    import librosa

    # Thanks: https://dev.to/highcenburg/getting-the-tempo-of-a-song-using-librosa-4e5b
    audio_file = librosa.load(filename)
    y, sr = audio_file
    estimated_tempo, beat_frames = librosa.beat.beat_track(y = y, sr = sr)
    beat_times = librosa.frames_to_time(beat_frames, sr = sr)

    return {
        'tempo': estimated_tempo,
        'beats': beat_times
    }