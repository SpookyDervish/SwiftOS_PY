import os
import asyncio
import multiprocessing
import math
from random import randint

from system.fs import run
from system.gui.desktop_screen import Desktop


PROC_ID_RANGE = (1000, 9999) # this defines the range of ids prossible
MAXprocesses = PROC_ID_RANGE[1]-PROC_ID_RANGE[1]+1


class MaxProcessesError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class ProcessAlreadyRegisteredError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class NoProcessFoundError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Process:    
    def __init__(self, name: str, file_path: str, process_manager) -> None:
        self.process_manager = process_manager
        self._name = name
        self._file = file_path
        
        self.__thread: multiprocessing.Process = None
        
        if not os.path.isfile(self._file):
            raise FileNotFoundError(self._file)
        
        self.id = self.__generate_unique_id()

    def _set_thread(self, thread):
        self.__thread = thread
        
    def get_thread(self):
        return self.__thread
        
    def __generate_unique_id(self):
        """Generates a random id within the possible range of ids. This function ensures non-duplicates.

        Returns:
            int: The unqiue generated id
        """
        existingprocesses = self.process_manager.processes
        
        if len(existingprocesses) >= (MAXprocesses): # This is so we don't get stuck in an infinite loop
            raise MaxProcessesError(f"Reached process limit of {MAXprocesses}")
        
        num = randint(*PROC_ID_RANGE)
        while num in existingprocesses:
            num = randint(*PROC_ID_RANGE)
            
        self.id = num
        return num
    
    async def start(self, args: list[str] = []):
        await run(self._file, self.process_manager.desktop, args)

class ProcessManager:
    def __init__(self, desktop: Desktop) -> None:
        self.processes: set[Process] = set()
        self.desktop: Desktop = desktop

    def get_process(self, id: int):
        processes_dict = {process.id: process for process in self.processes}
        process = processes_dict.get(id)
        
        return process
        
    def register_process(self, process: Process):
        if self.get_process(process.id):
            raise ProcessAlreadyRegisteredError()
        self.processes.add(process)
        
        self.desktop.app.log(f"Registered process: {process}")
        
    def __unregister_process(self, id: int):
        process = self.get_process(id)
        self.processes.remove(process)
        
    async def start(self, id: int, args: list[str] = []):
        process = self.get_process(id)
        
        if not process:
            raise NoProcessFoundError(id)
        
        self.desktop.app.log(args, process)
        _thread = multiprocessing.Process(target=asyncio.run, args=(process.start(args)), daemon=True)
        _thread.start()
        
        process._set_thread(_thread)
        
        self.desktop.app.log(f"Started process: {process}")
        
    def kill(self, id: int):
        process = self.get_process(id)
        thread = process.get_thread()
        
        thread.terminate()
        process._set_thread(None)
        self.__unregister_process(id)
        
        self.desktop.app.log(f"Killed process: {process}")
        
    @property
    def numprocesses(self) -> int:
        return len(self.processes)
    