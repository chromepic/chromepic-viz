import os


def immediate_subdirs(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def findnth(haystack, needle, n):
    parts= haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)

def extract_domain(url):
    i1 = findnth(url, '/', 1)
    i2 = findnth(url, '/', 2)
    if i1 == -1 or i2 == -1:
        return url
    return url[i1 + 1 : i2]
