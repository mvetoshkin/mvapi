import os
from datetime import datetime

import sys

from mvapi.libs.misc import render_template
from mvapi.settings import settings


def save_error(save_to_file=True):
    timestamp = datetime.utcnow()
    exc_type, exc_value, exc_traceback = sys.exc_info()
    python_executable = sys.executable
    python_version = sys.version_info[0:3]
    python_path = sys.path
    error_timestamp = timestamp.strftime('%b %d, %Y at %H:%M:%S')
    frames = get_traceback_frames(exc_traceback)
    last_frame = frames[-1]

    error_str = render_template('mvapi/error.tmpl', locals())

    if save_to_file:
        errors_dir = settings.ERRORS_PATH
        error_loc = last_frame['filename'].rpartition('/')[-1]
        error_ts = timestamp.strftime('%Y%m%d.%H%M%S')
        filename = os.path.join(errors_dir, f'{error_loc}.{error_ts}.html')

        if not os.path.exists(errors_dir):
            os.makedirs(errors_dir, exist_ok=True)

        with open(filename, 'wt') as error_file:
            error_file.write(error_str)

    return error_str


def get_traceback_frames(traceback):
    frames = []

    while traceback is not None:
        filename = traceback.tb_frame.f_code.co_filename
        lineno = traceback.tb_lineno

        frames.append({
            'filename': filename,
            'function': traceback.tb_frame.f_code.co_name,
            'lineno': lineno,
            'file_lines': get_file_lines(filename, lineno),
            'vars': traceback.tb_frame.f_locals.items()
        })

        traceback = traceback.tb_next

    return frames


def get_file_lines(filename, lineno):
    if not os.path.exists(filename):
        return []

    with open(filename, 'rt') as file:
        lines = file.readlines()

    if not lines:
        return []

    offset_lines = 7
    start_lineno = max(1, lineno - offset_lines) - 1
    end_lineno = lineno + offset_lines

    out_lines = []
    cur_lineno = start_lineno + 1

    for line in lines[start_lineno:end_lineno]:
        out_lines.append((cur_lineno, line))
        cur_lineno += 1

    return out_lines
