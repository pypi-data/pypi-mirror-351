from io import BytesIO


class SharePointFile(BytesIO):
    def __init__(self, name, mode, storage):
        super().__init__()
        self.name = name
        self.mode = mode
        self.storage = storage
        self._is_dirty = False

    def write(self, content):
        if 'w' not in self.mode:
            raise ValueError("File was not opened in write mode.")
        if isinstance(content, str):
            content = content.encode('utf-8')
        self._is_dirty = True
        return super().write(content)

    def close(self):
        if self._is_dirty:
            # Seek to the start of the BytesIO buffer before saving
            self.seek(0)
            self.storage._save(self.name, self)
        super().close()