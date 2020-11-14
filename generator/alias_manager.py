# %%
class AliasManager:
    def __init__(self):
        self.aliases: {str: int} = {}

    def __len__(self) -> int:
        return len(self.aliases)

    def all_aliases(self) -> [str]:
        return [ alias for alias in self.aliases.keys() if alias not in [None]]

    def table_id(self, alias: str) -> int or None:
        if alias == None: return self.aliases[None]

        alias_l: str = alias.lower()

        for (_alias, _table_idx) in self.aliases.items():
            if _alias == None: continue
            if alias_l == _alias.lower(): return _table_idx

        return None

    def add(self, alias: str, table_id: int):
        if alias == None:
            self.aliases[None] = table_id
            return

        self.aliases[alias] = table_id

    def alias(self, table_idx: int) -> int:
        if table_idx == -1: return ''
        if table_idx == None: return ''

        for alias, idx in self.aliases.items():
            if alias == None: continue
            if table_idx == idx: return alias

        raise Exception('Not found alias for #{}'.format(table_idx))

# %%
