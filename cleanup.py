import os, time

def cleanup():
    now = time.time()
    converted_folder = 'uploads/converted'
    for file in os.listdir(converted_folder):
        if not file.endswith('.mp3'):
            continue
        file_path = os.path.join(converted_folder, file)
        if os.stat(file_path).st_mtime < now - 60:
            os.remove(file_path)


if __name__ == '__main__':
    cleanup()