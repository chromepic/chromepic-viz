import datetime
import os

import keycodes
import triggers


def extract_attr(line, msg, tuples=True):
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

    if tuples and (-1 < line.find(',', end + 1) < line.find(':', end + 1)):
        # this probably means the attribute is a tuble, for instance 'Coordinates: 471, 1',
        # so return a tuple of those two values
        return line[msg_pos:end].strip(), extract_attr(line, msg + line[msg_pos:end] + ',')

    return line[msg_pos:end].strip()


def read_screenshot_metadata(log_path, log_filename):
    """

    :param log_path: Path to directory where log and screenshots are in
    :param log_filename: Name of log file relative to log_path
    :return: An dict for each snapshot, consisting of:
    (event id, filename, tab, time, absolute time, last mouse pos, last key pressed, trigger type, url)
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

        dir_generated_msg = 'SnapshotHandler:: Directory generated: '

        url_msg = 'SnapshotHandler:: HandleInputEvent'

        lines = f.readlines()

        initial_time = None
        last_mouse_pos = None
        last_keycode = None

        last_trigger = None
        last_snapshot_event = None

        # first line should contain date with timestamp
        start_date = None

        last_url = ''
        tab_to_url = {}
        date_str = '0'

        # Parse logs as follows: iterate through lines. We don't know if the line with the trigger comes first, or the line with
        # the snapshot info. So if we come accross a trigger line, set the trigger info for the last snapshot info if the event ids
        # match. Conversely, if we come accross a snapshot info line, set the snapshot info for the last trigger info if the
        # event ids match.

        for line in lines:

            if date_str == '0' and dir_generated_msg in line:
                dir_name = extract_attr(line, dir_generated_msg)
                date_str = dir_name[:dir_name.rfind('_')]
                try:
                    start_date = datetime.datetime.strptime(date_str, '%m_%d_%Y__%H_%M_%S')
                    initial_time = int(extract_attr(line, time_msg))
                except ValueError:
                    start_date = None
                    pass


            if line.find(snapshot_msg) != -1:
                snapshot_id = extract_attr(line, snapshot_id_msg)
                output_dir = extract_attr(line, output_dir_msg)
                time = int(extract_attr(line, time_msg))
                time_secs, absolute_time = 0, None
                if initial_time is not None:
                    time_secs = (time - initial_time) / 10000000
                if start_date is not None:
                    absolute_time = start_date + datetime.timedelta(seconds=time_secs)
                event_id = extract_attr(line, event_id_msg)
                snapshot_filename = os.path.join(output_dir, 'snapshot_{}.png'.format(snapshot_id))
                dom_filename = os.path.join(output_dir, 'snapshot_{}.mhtml'.format(snapshot_id))

                # lookup name corresponding to the keycode
                key_name = keycodes.keycodes[last_keycode]['name'] if last_keycode is not None else 'None'

                info = {'id': event_id, 'fname': snapshot_filename, 'dom': dom_filename, 'tab': output_dir,
                        't': time_secs, 'abstime': absolute_time, 'mouse': last_mouse_pos, 'key': key_name,
                        'url': last_url}

                # trigger could come before snapshot
                if last_trigger is not None and last_trigger[0] == event_id:
                    # append trigger type
                    info['trigger'] = (last_trigger[1])
                    metadata.append(info)
                    last_snapshot_event = None
                    last_trigger = None
                else:
                    last_snapshot_event = info

                if output_dir not in tab_to_url:
                    tab_to_url[output_dir] = last_url

            elif line.find(trigger_msg) != -1:
                event_id = extract_attr(line, event_id_msg)
                time = int(extract_attr(line, time_msg))
                if initial_time is None:
                    initial_time = time
                time_secs = (time - initial_time) / 10000000
                type = line[len(trigger_msg):line.find(' ', len(trigger_msg))]

                if type in triggers.mouse_position_triggers:
                    coordinates = extract_attr(line, coordinates_msg)
                    last_mouse_pos = (int(coordinates[0]), int(coordinates[1]))
                elif type in triggers.keycode_triggers:
                    keycode = extract_attr(line, keycode_msg)
                    last_keycode = int(keycode)
                    # lookup name corresponding to the keycode
                    key_name = keycodes.keycodes[last_keycode]['name'] if last_keycode is not None else 'None'

                # snapshot could come before trigger
                if last_snapshot_event is not None and last_snapshot_event['id'] == event_id:
                    # append trigger type
                    last_snapshot_event['trigger'] = type
                    if type in triggers.mouse_position_triggers:
                        last_snapshot_event['mouse'] = last_mouse_pos
                    elif type in triggers.keycode_triggers:
                        last_snapshot_event['key'] = key_name
                    metadata.append(last_snapshot_event)
                    last_snapshot_event = None
                    last_trigger = None
                else:
                    last_trigger = [event_id, type]

            elif line.find(url_msg) != -1:
                last_url = extract_attr(line, 'URL: ', tuples=False)

    return metadata, tab_to_url


def time_closest(metadata, t):
    """

    :param metadata:
    :return: Index with closest time to t
    """

    closest_t = abs(metadata[0]['t'] - t)
    closet_i = 0

    for i in range(1, len(metadata)):
        if abs(metadata[i]['t'] - t) < closest_t:
            closest_t = abs(metadata[i]['t'] - t)
            closet_i = i

    return closet_i
