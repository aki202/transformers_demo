# %%
class Table:
    def __init__(self, name: str, idx: int):
        self.name = name
        self.idx = idx

    def __str__(self) -> str:
        return '{} #({})'.format(self.name, self.idx)
