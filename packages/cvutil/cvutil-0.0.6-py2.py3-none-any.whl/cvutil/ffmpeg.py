"""
    Video/audio processing via FFMPEG auxiliary functions.
"""

__all__ = ['extract_frames_from_video', 'extract_audio_from_video', 'merge_video_with_audio']

import logging
import subprocess


def _run_command(command: list[str],
                 show_output: bool = False):
    """
    Run shell command as subprocess.

    Parameters
    ----------
    command : list(str)
        Shell command.
    show_output : bool, default False
        Whether to show command output.
    """
    kwargs = {"stdout": None, "stderr": None} if show_output else\
        {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    proc_res = subprocess.run(command, **kwargs)
    if proc_res.returncode != 0:
        logging.error("Subprocess `{}` returns code `{}`".format(" ".join(proc_res.args), proc_res.returncode))


def extract_frames_from_video(input_video_file_path: str,
                              output_frame_dir_path: str,
                              frame_file_name_ext: str,
                              fps: float = 60,
                              all_frames: bool = True,
                              show_ffmpeg_output: bool = False):
    """
    Extract frames from a video file.

    Parameters
    ----------
    input_video_file_path : str
        Input video file path.
    output_frame_dir_path : str
        Output directory path for frames.
    frame_file_name_ext : str
        Target frame file name extension.
    fps : float, default 60
        Video FPS (for all frame extraction only).
    all_frames : bool, default False
        Whether to extract all frames from video steam without dropping and dubbing.
    show_ffmpeg_output : bool, default False
        Whether to show FFMPEG output.
    """
    if all_frames:
        cmd_template = ["ffmpeg", "-r", "{fps}", "-i", "{in_video}", "-r", "{fps}", "-q:v", "2", "{dir}/%5d{frame_ext}"]
    else:
        cmd_template = ["ffmpeg", "-i", "{in_video}", "-q:v", "2", "{dir}/%5d{frame_ext}"]
    command = [c.format(
        fps=fps,
        in_video=input_video_file_path,
        dir=output_frame_dir_path,
        frame_ext=frame_file_name_ext) for c in cmd_template]
    _run_command(command=command, show_output=show_ffmpeg_output)


def extract_audio_from_video(input_video_file_path: str,
                             output_audio_file_path: str,
                             ffmpeg_params: str = "-vn -c:a copy",
                             show_ffmpeg_output: bool = False):
    """
    Real extract an audio stream from a video file.

    Parameters
    ----------
    input_video_file_path : str
        Path to input video file.
    output_audio_file_path : str
        Output audio file path.
    ffmpeg_params : str, default '-vn -c:a copy'
        Encoder ffmpeg params.
    show_ffmpeg_output : bool, default False
        Whether to show FFMPEG output.
    """
    cmd_template1 = ["ffmpeg", "-i", "{in_video}"]
    cmd_template2 = ["{out_audio}"]
    command1 = [c.format(in_video=input_video_file_path) for c in cmd_template1]
    command2 = [c.format(out_audio=output_audio_file_path) for c in cmd_template2]
    command = command1 + ffmpeg_params.split() + command2
    _run_command(command=command, show_output=show_ffmpeg_output)


def merge_video_with_audio(input_video_file_path: str,
                           input_audio_file_path: str,
                           output_video_file_path: str,
                           ffmpeg_params: str = "-c:v copy -c:a aac",
                           show_ffmpeg_output: bool = False):
    """
    Merge video with audio into a video file.

    Parameters
    ----------
    input_video_file_path : str
        Path to an input video file.
    input_audio_file_path : str
        Path to an input audio file.
    output_video_file_path : str
        Path to an output video file.
    ffmpeg_params : str, default '-c:v copy -c:a aac'
        Muxing FFMPEG params.
    show_ffmpeg_output : bool, default False
        Whether to show FFMPEG output.
    """
    cmd_template1 = ["ffmpeg", "-i", "{in_video}", "-i", "{in_audio}"]
    cmd_template2 = ["{out_video}"]
    command1 = [c.format(in_video=input_video_file_path, in_audio=input_audio_file_path) for c in cmd_template1]
    command2 = [c.format(out_video=output_video_file_path) for c in cmd_template2]
    command = command1 + ffmpeg_params.split() + command2
    _run_command(command=command, show_output=show_ffmpeg_output)
