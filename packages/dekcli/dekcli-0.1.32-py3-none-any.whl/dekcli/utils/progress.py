import tqdm


class FileProgress:
    ellipsis = 30

    def __init__(self, filepath, size_total):
        self.filepath = filepath
        self.size_total = size_total

    @property
    def filepath_short(self):
        if len(self.filepath) > self.ellipsis:
            return f"...{self.filepath[-self.ellipsis:]}"
        return self.filepath

    def update(self, size):
        pass

    def close(self):
        pass


class FileProgressTqdm(FileProgress):
    def __init__(self, filepath, size_total):
        super().__init__(filepath, size_total)
        self.progress_bar = tqdm.tqdm(total=size_total, unit="B", unit_scale=True, desc=self.filepath_short)

    def update(self, size):
        self.progress_bar.update(size)

    def close(self):
        self.progress_bar.close()
