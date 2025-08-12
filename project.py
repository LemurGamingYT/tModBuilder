from dataclasses import dataclass, field
# from gzip import compress, decompress
from pickle import loads, dumps
from pathlib import Path


@dataclass
class ModConfig:
    author: str = 'none'
    hideCode: bool = False
    hideResources: bool = False
    includeSource: bool = True
    version: str = '0.1'
    buildIgnore: list[str] = field(default_factory=lambda: [
        '*.csproj', '*.user', 'obj\\*', 'bin\\*', '.vs\\*'
    ])
    description: str = 'Made with TModBuilder!'
    icon: Path = Path.cwd() / 'assets' / 'placeholder_image.png'

@dataclass
class Project:
    name: str
    path: Path
    content: list = field(default_factory=list)
    config: ModConfig = field(default_factory=lambda: ModConfig())

    @property
    def file(self):
        return self.path / f'{self.name}.tmb'
    
    @property
    def internal_name(self):
        return self.name.replace(' ', '_')

    @staticmethod
    def load(path: Path):
        return loads(path.read_bytes())

    def save(self):
        self.file.write_bytes(dumps(self))
