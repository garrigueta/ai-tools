from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess

app = FastAPI()


class CommandRequest(BaseModel):
    """ Command Request """
    command: str


class CommandResponse(BaseModel):
    """ Command Response """
    stdout: str
    stderr: str
    exit_code: int


@app.post("/run", response_model=CommandResponse)
def run_command(cmd: CommandRequest):
    """ Run Command """
    try:
        result = subprocess.run(
            cmd.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        return CommandResponse(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode
        )
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(status_code=408, detail="Command timed out") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
