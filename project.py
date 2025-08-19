from dataclasses import dataclass, field, fields
from json import loads, dumps
from pathlib import Path
from typing import Any


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

    @staticmethod
    def load(json: dict[str, Any]):
        return ModConfig(
            json['author'],
            json['hideCode'],
            json['hideResources'],
            json['includeSource'],
            json['version'],
            json['buildIgnore'],
            json['description'],
            Path(json['icon'])
        )

    def save(self):
        return {
            'author': self.author,
            'hideCode': self.hideCode,
            'hideResources': self.hideResources,
            'includeSource': self.includeSource,
            'version': self.version,
            'buildIgnore': self.buildIgnore,
            'description': self.description,
            'icon': self.icon.as_posix()
        }

@dataclass
class Project:
    name: str
    path: Path
    content: list = field(default_factory=list)
    config: ModConfig = field(default_factory=lambda: ModConfig())

    @property
    def file(self):
        return self.path / f'{self.name}.json'
    
    @property
    def internal_name(self):
        return self.name.replace(' ', '_')

    @staticmethod
    def load_content(json: dict):
        from editor_types.content_types import CONTENT_TYPES
        from editor_types.data_types import DATA_TYPES

        mod_content = []
        for content in json['content']:
            content_type = content.pop('type')
            for typ in CONTENT_TYPES:
                if content_type != typ.__name__:
                    continue

                content_kwargs: dict[str, Any] = {}
                for field_name, field_json in content.items():
                    field_type = field_json.pop('type')
                    for data_type in DATA_TYPES:
                        if field_type != data_type.__name__:
                            continue

                        content_kwargs[field_name] = data_type(**field_json)
                        break

                mod_content.append(typ(**content_kwargs))
                break
        
        return mod_content

    @staticmethod
    def load(path: Path):
        json = loads(path.read_text('utf-8'))
        mod_content = Project.load_content(json)
        return Project(
            name=json['name'],
            path=path.parent,
            content=mod_content,
            config=ModConfig.load(json['config'])
        )

    def save(self):
        json = {
            'name': self.name,
            'path': self.path.as_posix(),
            'content': [],
            'config': self.config.save()
        }

        for content_instance in self.content:
            encoded_content = {'type': content_instance.__class__.__name__}
            for content_field in fields(content_instance):
                value = getattr(content_instance, content_field.name)
                encoded_value = {'type': value.__class__.__name__}
                for value_field in fields(value):
                    encoded_value[value_field.name] = getattr(value, value_field.name)
                
                encoded_content[content_field.name] = encoded_value
            
            json['content'].append(encoded_content)
        
        self.file.write_text(dumps(json, indent=4))
