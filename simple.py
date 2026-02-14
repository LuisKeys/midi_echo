from dataclasses import dataclass
@dataclass
class Test:
    x: int = 1
    @classmethod
    def load(cls):
        return cls()
print('simple ok')
