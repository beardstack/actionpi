class AbstractSystem(object):
    def get_cpu_temp(self) -> float:
        raise NotImplementedError('get_cpu_temp is not implemented')

    def get_cpu_percent(self) -> int:
        raise NotImplementedError('get_cpu_percent is not implemented')

    def get_disk_usage(self) -> int:
        raise NotImplementedError('get_disk_usage is not implemented')
    
    def get_ram_usage(self) -> int:
        raise NotImplementedError('get_ram_usage is not implemented')

    def halt_system(self):
        raise NotImplementedError('halt_system is not implemented')

    def enable_hotspot(self) -> bool:
        raise NotImplementedError('enable_hotspot is not implemented')

    def disable_hotspot(self) -> bool:
        raise NotImplementedError('disable_hotspot is not implemented')