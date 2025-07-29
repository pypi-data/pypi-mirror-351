import json
from pathlib import Path

from makex.file_checksum import FileChecksum
from makex.metadata import TargetWithValidKey
from makex.protocols import FileStatus
from makex.python_script import FileLocation
from makex.target import Task


class MakexMetadataFile:
    def __init__(self, path, targets: list[Task]):
        self.path: Path = path
        self.targets: dict[Task, Task] = {}

    def add_target(self, target: Task):
        self.targets[target] = target

    def write(self):
        # newline delimited json
        with (self.path).open("wb") as f:
            for target in self.targets:
                input_files = [
                    {
                        "path": file.path.as_posix(),
                        "checksum": str(file.checksum),
                        "fingerprint": "",
                    } for file in target.inputs
                ]
                output_files = [
                    {
                        "path": file.path.as_posix(),
                        "checksum": str(file.checksum),
                        "fingerprint": "",
                    } for file in target.inputs
                ]

                json.dump(
                    {
                        "$": "target",
                        "name": target.name,
                        "path": target.path.as_posix(),
                        "inputs": input_files,
                        "outputs": output_files
                    },
                    f
                )
                f.write(b"\n")

    def get_target(self, target: TargetWithValidKey, path: Path):
        return self.targets.get(target, None)

    @classmethod
    def load(cls, path: Path):
        targets = []

        with open(path) as f:
            for line in f:
                obj = json.loads(line)
                inputs = [
                    FileStatus(
                        path=Path(input.get("path")),
                        checksum=FileChecksum.parse(input.get("checksum"))
                    ) for input in obj.get("inputs", [])
                ]
                requires = [
                    Task(name=req.get("name"), path=Path(req.get("path")))
                    for req in obj.get("requires", [])
                ]

                objloc = obj.get("location")
                location = FileLocation(
                    objloc.get("line"), objloc.get("column"), objloc.get("path")
                )

                target = Task(
                    name=obj.get("name"),
                    path=Path(obj.get("path")),
                    inputs=inputs,
                    outputs=[],
                    requires=requires,
                    location=location,
                )
                targets.append(target)

        return cls(cls, targets)
