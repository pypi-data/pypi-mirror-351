from abc import ABC, abstractmethod

class SystemCheck(ABC):
    @abstractmethod
    def check_disk_encryption(self):
        pass

    @abstractmethod
    def check_os_updates(self):
        pass

    @abstractmethod
    def check_antivirus_status(self):
        pass

    @abstractmethod
    def check_sleep_settings(self):
        pass
