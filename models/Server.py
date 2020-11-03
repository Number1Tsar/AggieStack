class Server:
    def __init__(self, name, rack, ip, memory, disk, vcpu):
        self.Name = name
        self.IP = ip
        self.Memory = memory
        self.Disk = disk
        self.VCPU = vcpu
        self.Memory_free = memory
        self.VCPU_free = vcpu
        self.disk_free = disk
        self.Rack = rack

        self.isActive = True
