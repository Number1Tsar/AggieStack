class Rack:
    def __init__(self, name, capacity):
        self.Name = name
        self.Capacity = capacity
        self.AvailableCapacity = capacity
        self.ImageCache = []
