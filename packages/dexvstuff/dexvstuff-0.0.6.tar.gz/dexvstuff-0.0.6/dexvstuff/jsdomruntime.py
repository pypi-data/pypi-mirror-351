from javascript import require
import json

class JsdomRuntime:
    def __init__(self) -> None:
        self.jsdom = require('jsdom')
        self.vm = require("vm").Script
        self.runtime = self.jsdom.JSDOM(
            "<title>jsdom</title>", {
                "runScripts": "dangerously"
            }
        ).getInternalVMContext()
        
    def eval(self, data: str, promise: bool = False, byte_array: bool = False, suppress: bool = False) -> str:
        try:
            script = (
                f"{data}.then(r => JSON.stringify(Array.from(r)))" if byte_array and promise else
                f"JSON.stringify(Array.from(({data})))" if byte_array else
                f"{data}.then(r => JSON.stringify(r))" if promise else data
            )
            result = self.vm(script).runInContext(self.runtime)
            return json.loads(result) if byte_array else result
        except Exception as e:
            if suppress: pass
            else: raise e