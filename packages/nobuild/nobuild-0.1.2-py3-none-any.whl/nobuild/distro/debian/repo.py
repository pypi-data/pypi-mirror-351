import shutil
import os

def copy_extra(source: str = "./src/extra"):
    for filename in os.listdir(source):
        source_file = os.path.join(source, filename)
        target_file = os.path.join("./work/config", filename)
        shutil.copy2(source_file, target_file)

def copy_files(source: str = "./src/files"):
    if os.path.isdir(source):
        for item in os.listdir(source):
            src_path = os.path.join(source, item)
            dst_path = os.path.join("./work/config/includes.chroot_after_packages", item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

def copy_repo(source: str = "./src/repo"):
    if os.path.isdir(source):
        for file in os.listdir(source):
            src_file = os.path.join(source, file)
            dst_file = os.path.join("./work/config/archives/", file)

            shutil.copy(src_file, dst_file + ".chroot")        
            shutil.copy(src_file, dst_file + ".binary")