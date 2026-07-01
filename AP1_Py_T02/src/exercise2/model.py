class ImageResult:
    def __init__(self, url: str):
        self.url = url
        self.status = "В процессе"
        self.error_msg = None
        self.filename = None
