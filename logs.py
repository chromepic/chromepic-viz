import os
import tkinter

from PIL import Image


def get_all_screenshot_names(directory):
    """

    :param directory: The directory where the screenshots are in
    :return: Filenames of all screenshots in the directory
    """

    # this assumes there are only screenshots in the dir
    return os.listdir(directory)


def read_screenshot(path):
    return Image.open(path)


def extract_attr(line, msg):
    """
    Extracts attribute from line, assuming it is in this form:
    [msg1][attr1], [msg2][attr2], ...
    """
    msg_pos = line.find(msg)
    if msg_pos is -1:
        return None
    msg_pos += len(msg)
    end = line.find(',', msg_pos)
    # if this message is last item, there is no comma after it
    end = len(line) if end == -1 else end

    if -1 < line.find(',', end + 1) < line.find(':', end + 1):
        # this probably means the attribute is a tuble, for instance 'Coordinates: 471, 1',
        # so return a tuple of those two values
        return line[msg_pos:end].strip(), extract_attr(line, msg + line[msg_pos:end] + ',')

    return line[msg_pos:end].strip()


def read_screenshot_metadata(log_path, log_filename):
    """

    :param log_path: Path to directory where log and screenshots are in
    :param log_filename: Name of log file relative to log_path
    :return: An array for each snapshot, consisting of:
    (event id, filename, time, last mouse pos, last key pressed, trigger type)
    """

    metadata = []

    with open(os.path.join(log_path, log_filename)) as f:

        snapshot_msg = 'SnapshotHandler:: This is a snapshot event'
        snapshot_id_msg = 'Snapshot ID: '  # in snapshot line
        output_dir_msg = 'Output Directory: '  # in snapshot line
        time_msg = 'Time: '  # in snapshot line
        event_id_msg = 'Event ID: '  # in snapshot line

        trigger_msg = 'SnapshotHandler:: LogEventMetadata '
        coordinates_msg = 'Coordinates: '
        keycode_msg = 'Code: '

        lines = f.readlines()

        initial_time = None
        last_mouse_pos = None
        last_keycode = None

        last_trigger = None
        last_snapshot_event = None

        for line in lines:
            if line.find(snapshot_msg) != -1:
                snapshot_id = extract_attr(line, snapshot_id_msg)
                output_dir = extract_attr(line, output_dir_msg)
                time = int(extract_attr(line, time_msg))
                if initial_time is None:
                    initial_time = time
                time_secs = (time - initial_time) / 10000000
                event_id = extract_attr(line, event_id_msg)
                snapshot_filename = os.path.join(log_path, 'screenshots', output_dir,
                                                 'snapshot_{}.png'.format(snapshot_id))

                info = [event_id, snapshot_filename, time_secs, last_mouse_pos, last_keycode]

                # trigger could come before snapshot
                if last_trigger is not None and last_trigger[0] == event_id:
                    # append trigger type
                    info.append(last_trigger[1])
                    metadata.append(info)
                    last_snapshot_event = None
                    last_trigger = None
                else:
                    last_snapshot_event = info

            elif line.find(trigger_msg) != -1:
                event_id = extract_attr(line, event_id_msg)
                time = int(extract_attr(line, time_msg))
                if initial_time is None:
                    initial_time = time
                time_secs = (time - initial_time) / 10000000
                type = line[len(trigger_msg):line.find(' ', len(trigger_msg))]

                if type == 'MouseMove':
                    coordinates = extract_attr(line, coordinates_msg)
                    last_mouse_pos = (int(coordinates[0]), int(coordinates[1]))
                elif type == 'Key':
                    keycode = extract_attr(line, keycode_msg)
                    last_keycode = int(keycode)

                # snapshot could come before trigger
                if last_snapshot_event is not None and last_snapshot_event[0] == event_id:
                    # append trigger type
                    last_snapshot_event.append(type)
                    metadata.append(last_snapshot_event)
                    last_snapshot_event = None
                    last_trigger = None
                else:
                    last_trigger = [event_id, type]

    return metadata