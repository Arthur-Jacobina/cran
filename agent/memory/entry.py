import tiktoken

class Entry:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o")
        self.tokens = len(self.tokenizer.encode(self.content))

    def __repr__(self):
        return f"Entry(role={self.role}, content={self.content}, tokens={self.tokens})"

    def __str__(self):
        return self.__repr__()