import os

class FileValidator:
    def __init__(self, allowed_extensions):
        self.allowed_extensions = allowed_extensions

    def validate(self, filename, category):
        if not filename:
            return False, "Empty filename"

        if category not in self.allowed_extensions:
            return False, "Invalid category"

        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        if not ext:
            return False, "File has no extension"

        allowed = self.allowed_extensions[category]

        if ext not in allowed:
            return False, f"Extension '{ext}' is not allowed for category '{category}'"

        return True, None