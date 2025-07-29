import os, tarfile, requests, subprocess
from pathlib import Path
from io import BytesIO

class Wabt:
    def __init__(self):
        self.path = Path(os.getenv('LOCALAPPDATA')) / 'wabt'
        if not self.is_installed(): self.install_wabt()
        self.exes = self.get_exes()
    
    def is_installed(self):
        if not self.path.exists():
            self.path.mkdir(parents=True)
            return False
        return any(self.path.iterdir())
    
    def install_wabt(self):
        response = requests.get("https://github.com/WebAssembly/wabt/releases/download/1.0.36/wabt-1.0.36-windows.tar.gz")
        with tarfile.open(fileobj=BytesIO(response.content), mode='r:gz') as tar:
            for member in tar.getmembers():
                if member.name.startswith('wabt-1.0.36/bin/') and member.isfile():
                    member.name = Path(member.name).name
                    tar.extract(member, path=self.path)
    
    def get_exes(self):
        return {exe.stem.replace('-', '_'): exe for exe in self.path.glob("*.exe")}
    
    def run(self, tool, *args):
        if tool not in self.exes:
            raise ValueError(f"{tool} not found in WABT installation.")
        
        cmd = [str(self.exes[tool])] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return result.stdout, result.stderr
    
    def __getattr__(self, name):
        if name in self.exes:
            return lambda *args: self.run(name, *args)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def wat2wasm(self, *args):
        return self.run('wat2wasm', *args)
    
    def wasm2wat(self, *args):
        return self.run('wasm2wat', *args)
    
    def wasm_objdump(self, *args):
        return self.run('wasm_objdump', *args)

    def wasm_decompile(self, *args):
        return self.run('wasm_decompile', *args)