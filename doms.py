import codecs
import os
import random

import logs


def read_file(f):
    line = f.readline()
    all = ''
    while line:
        all += line
        try:
            line = f.readline()
        except UnicodeDecodeError:
            # some bytes are not valid unicode characters
            line = '???'

    return all


def read_dom(path):
    with codecs.open(path, errors='ignore') as f:
        # throw all the multipart entities that are not text
        all = read_file(f)
        text_only = ''
        multipart_boundary_msg = '------MultipartBoundary--'
        content_type_msg = 'Content-Type: '
        entity_start = all.find(multipart_boundary_msg)
        while entity_start != -1:
            entity_end = all.find(multipart_boundary_msg, entity_start + 1)
            if entity_end == -1:
                entity_end = len(all)
            entity = all[entity_start:entity_end]
            content_type_pos = entity.find('\n')
            content_type = logs.extract_attr(entity[content_type_pos:entity.find('\n', content_type_pos + 1)],
                                             content_type_msg)
            if content_type.startswith('text'):
                text_only += entity + '\n\n\n\n'
            entity_start = all.find(multipart_boundary_msg, entity_end + 1)

        return text_only


def write_to_temp(dom, fname, base_dir):
    # generate random filename
    path = os.path.join(base_dir, fname + '_' + str(random.randint(100000, 1000000000)) + '.txt')
    with open(path, 'w') as f:
        f.write(dom)
    return path
