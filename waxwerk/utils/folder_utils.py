import os

class FolderHandler:
    @staticmethod
    def get_audio_files(folder_path):
        allowed_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.wma'}
        files = []
        for root, _, filenames in os.walk(folder_path):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in allowed_extensions:
                    files.append(os.path.join(root, f))
        return files
    
    @staticmethod
    def rename_files(folder_path, new_name):
        for root, _, filenames in os.walk(folder_path):
            for f in filenames:
                os.rename(os.path.join(root, f), os.path.join(root, new_name))