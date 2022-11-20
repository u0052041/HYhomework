import os
from collections import defaultdict


def get_size_info(path):
    files = os.listdir(path)
    for file in files:
        p = os.path.join(path, file)
        if os.path.isdir(p):
            get_size_info(p)
        if os.path.isfile(p):
            type_name = os.path.splitext(p)[1]
            if type_name:
                folder_size_d['total']['count'] += 1
                folder_size_d['total']['size'] += os.path.getsize(p)
                folder_size_d[type_name]['count'] += 1
                folder_size_d[type_name]['size'] += os.path.getsize(p)

    return folder_size_d


folder_size_d = defaultdict(lambda: defaultdict(None, {'count':0, 'size': 0}))
ret = get_size_info('your file path')
for key, val in ret.items():
    print(f'''
          file type: {key}
          file count: {val["count"]}
          file size: {round(val["size"]/1024**2, 3)} MB''')
