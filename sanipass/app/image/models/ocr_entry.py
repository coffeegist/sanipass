class OCREntry:

    def __init__(self, text="", left=0, top=0, width=0, height=0,
                 confidence=0, sensitive=False, sensitive_match=None):
        self.text = text
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.confidence = confidence
        self.sensitive = sensitive
        if not sensitive_match:
            self.sensitive_match = []
