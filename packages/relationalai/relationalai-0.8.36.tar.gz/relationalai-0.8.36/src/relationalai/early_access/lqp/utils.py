class UniqueNames:
    def __init__(self):
        # Track count of seen names
        self.seen = dict[str, int]()
        # Maps id to unique name
        self.id_to_name = dict[int,str]()

    def get_name(self, name: str) -> str:
        # TODO: Do we need to be threadsafe?
        if name in self.seen:
            self.seen[name] += 1
            id = self.seen[name]
            return f"{name}_{id}"
        else:
            self.seen[name] = 1
            return f"{name}"

    # Get a unique name for the given id. If the id is already in the map, return the
    # existing name. Otherwise, generate a new name using the suggested_name and
    # store it in the map.
    def get_name_by_id(self, id: int, suggested_name:str) -> str:
        if id in self.id_to_name:
            return self.id_to_name[id]

        name = self.get_name(suggested_name)
        self.id_to_name[id] = name
        return name
