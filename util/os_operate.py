

def file_list(match):
    import glob
    file_list = glob.glob(match)

    return file_list


def dir_check(dir_name, delete=True):
    import os
    if delete:
        if os.path.exists(dir_name):
            import shutil
            shutil.rmtree(dir_name)
        os.mkdir(dir_name)
    else:
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)


