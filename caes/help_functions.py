import os


# -----------------------------------------------------
# Remove filetype from filename
# -----------------------------------------------------
def remove_ext(filename):
    ind = filename.find('.')
    if not ind == -1:
        return filename[:ind]
    else:
        return filename


# -----------------------------------------------------
# Create directory to hold project files
# -----------------------------------------------------
def create_dir(project_path=os.path.normcase('.'), folder='results'):
    # configs - required
    dir = os.path.join(project_path, folder)
    try:
        os.stat(dir)
    except:
        os.mkdir(dir)

    return dir
