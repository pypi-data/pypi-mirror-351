# [Dexv-Stuff](https://pypi.org/project/dexvstuff/)

Stuff i use in my projects

## Installation

```bash
pip install dexvstuff
```

## Features

- **Logger**: My own logger which i like 
- **Files**: Simplified file operations
- **JsdomRuntime**: Execute js in a dom environment
- **Wabt**: WebAssembly Binary Toolkit wrapper for Python. For a better WABT wrapper, check out [wabt.py](https://github.com/c7a2d9e/wabt.py)

## Usage

### Logger
```python
from dexvstuff import Logger

# basic logger
log = Logger()

# customized
log = Logger(prefix="Dexv", indent=2)  # prefix is optional, indent can be any number (default is 0)

log.info("This is an info message")
log.success("This is a success message")
log.warning("This is a warning message")
log.failure("This is a failure message")
log.debug("This is a debug message")
log.captcha("This is a captcha message")
log.PETC()  # Press Enter To Continue
```

### Files
```python
from dexvstuff import Files

Files.create("example.txt")
Files.create(["dir1/file1.txt", "dir2/file2.txt"])

Files.write("example.txt", "Dexvstuff is cool")
print(Files.read("example.txt"))
Files.append("example.txt", "\nDexvstuff is even cooler")

print(Files.get_file_size("example.txt"))
Files.delete("example.txt")
```

### JsdomRuntime
```python
from dexvstuff import JsdomRuntime

runtime = JsdomRuntime()

print(runtime.eval("console.log('Dexvstuff is cool')"))
print(runtime.eval("new Promise((resolve) => setTimeout(() => resolve('Dexvstuff is cool'), 1000))", promise=True)) # resolves promises
print(runtime.eval('''(function() { return new Uint8Array([1, 2, 3]) })()''', byte_array=False)) # support js byte arrays
```

### Wabt
```python
from dexvstuff import Wabt

wabt = Wabt()


wat_output, errors = wabt.wasm2wat("example.wasm")
wasm_output, errors = wabt.wat2wasm("example.wat")
objdump_output, errors = wabt.wasm_objdump("example.wasm")
...
```

## Documentation

### Logger
- `Logger(prefix=None, indent=0)`: create a new logger instance
  - `prefix`: optional string to prefix all messages (default: None)
  - `indent`: number of spaces to indent messages (default: 0)
- `info(message)`: info message
- `success(message)`: success message
- `warning(message)`: warning message
- `failure(message)`: error message
- `debug(message)`: debug message (only shown in debug mode)
- `captcha(message)`: captcha-related message
- `PETC()`: pause execution until Enter is pressed

### Files
- `create(path)`: create file or directory
- `read(path)`: read file content
- `write(path, content)`: write content to file
- `append(path, content)`: append content to file
- `delete(path)`: delete file
- `get_file_size(path)`: get file size in bytes
- `exists(path)`: check if file/directory exists

### JsdomRuntime
- `eval(code, promise=False, byte_array=False)`: execute JavaScript code
  - `promise`: set to True if code returns a promise
  - `byte_array`: set to True if code returns a byte array

### Wabt
- `wat2wasm(file)`: convert .wat to .wasm
- `wasm2wat(file)`: convert .wasm to .wat
- `wasm_objdump(file)`: inspect WASM file
- `wasm_decompile(file)`: decompile WASM to C-like code
- All WABT tools are supported but not all are defined in the wrapper, you can still use them through dynamic attribute access
  - Example: `wabt.wasm_validate('file.wasm')` will call the wasm-validate tool
  - See [WABT documentation](https://github.com/WebAssembly/wabt?tab=readme-ov-file#wabt-the-webassembly-binary-toolkit) for all available tools

## License
MIT License - See [LICENSE](LICENSE) for more information
