from dataclasses import dataclass, field
from shutil import copyfile
from subprocess import run
from pathlib import Path

from project import Project


@dataclass
class Method:
    name: str
    params: list[tuple[str, str]] # (type, name)
    return_type: str
    body_code: str

    @property
    def code(self):
        params_str = ', '.join(f'{param[0]} {param[1]}' for param in self.params)
        return f"""public override {self.return_type} {self.name}({params_str}) {{
{self.body_code}
}}
"""

@dataclass
class PropertyFlags:
    override: bool = False
    static: bool = False
    readonly: bool = False
    
    def __str__(self) -> str:
        code = ''
        if self.override:
            code += 'override '
        
        if self.static:
            code += 'static '
        
        if self.readonly:
            code += 'readonly '
        
        return code

@dataclass
class Property:
    name: str
    type: str
    value: str
    is_field: bool = True
    flags: PropertyFlags = field(default_factory=PropertyFlags)
    
    @property
    def code(self):
        assign_symbol = '=' if self.is_field else '=>'
        return f"""public {self.flags} {self.type} {self.name} {assign_symbol} {self.value};"""

@dataclass
class Localization:
    name: str
    keys: dict[str, str] = field(default_factory=dict)

    @property
    def code(self):
        return f"""{self.name}: {{
    {'\n'.join(f'    {key}: {value}' for key, value in self.keys.items())}
}}
"""

@dataclass
class BuildContext:
    mod_name: str
    build_dir: Path
    project: Project
    class_name: str
    class_bases: list[str] = field(default_factory=list)
    class_properties: list[Property] = field(default_factory=list)
    class_methods: list[Method] = field(default_factory=list)

    @property
    def class_code(self):
        class_bases_str = ', '.join(self.class_bases)
        class_methods_str = '\n'.join(method.code for method in self.class_methods)
        class_properties_str = '\n'.join(prop.code for prop in self.class_properties)
        return f"""public class {self.class_name} : {class_bases_str}
{{
{class_properties_str}
{class_methods_str}
}}
"""
    
    def find_method(self, name: str):
        for method in self.class_methods:
            if method.name == name:
                return method


assets_folder = Path.cwd() / 'assets'

def make_build_files(build_dir: Path, mod_name: str):
    properties_folder = build_dir / 'Properties'
    properties_folder.mkdir(exist_ok=True)

    launch_settings_json = properties_folder / 'launchSettings.json'
    launch_settings_json.write_text("""{
    "profiles": {
        "Terraria": {
            "commandName": "Executable",
            "executablePath": "$(DotNetName)",
            "commandLineArgs": "$(tMLPath)",
            "workingDirectory": "$(tMLSteamPath)"
        },
        "TerrariaServer": {
          "commandName": "Executable",
          "executablePath": "$(DotNetName)",
          "commandLineArgs": "$(tMLServerPath)",
          "workingDirectory": "$(tMLSteamPath)"
        }
    }
}""")
    
    tmodloader_targets = assets_folder / 'tModLoader.targets'
    
    # manually add in a .csproj template
    csproj = build_dir / f'{mod_name}.csproj'
    csproj.write_text(f"""<Project Sdk="Microsoft.NET.Sdk">
  <Import Project="{tmodloader_targets.as_posix()}" />
  <PropertyGroup>
    <AssemblyName>{mod_name}</AssemblyName>
    <LangVersion>latest</LangVersion>
  </PropertyGroup>
  <ItemGroup>
  </ItemGroup>
</Project>
""")
    
    return csproj

def build_project(project: Project):
    mod_name = project.internal_name
    build_dir = project.path / mod_name
    build_dir.mkdir(exist_ok=True)

    main = build_dir / f'{mod_name}.cs'
    main.write_text(f"""using Terraria.ModLoader;

namespace {mod_name}
{{
    public class {mod_name} : Mod
    {{
    }}
}}
""")
    
    description_txt = build_dir / 'description.txt'
    description_txt.write_text(project.config.description)

    buildIgnore_str = ', '.join(project.config.buildIgnore)

    build_txt = build_dir / 'build.txt'
    build_txt.write_text(f"""author = {project.config.author}
displayName = {project.name}
hideCode = {project.config.hideCode}
hideResources = {project.config.hideResources}
includeSource = {project.config.includeSource}
buildIgnore = {buildIgnore_str}
version = {project.config.version}
""")
    
    csproj = make_build_files(build_dir, mod_name)
    
    icon_path = project.config.icon
    if not icon_path.exists():
        raise FileNotFoundError(f'Icon file not found: {icon_path}')

    copyfile(icon_path, build_dir / 'icon.png')

    localization_folder = build_dir / 'Localization'
    localization_folder.mkdir(exist_ok=True)

    en_US = localization_folder / f'en-US_Mods.{mod_name}.hjson'
    en_US.touch()
    
    content_dir = build_dir / 'Content'
    content_dir.mkdir(exist_ok=True)
    for content in project.content:
        build_ctx = BuildContext(mod_name, build_dir, project, content.get_internal_name())
        content.build(build_ctx)
        localization = content.build_localization(build_ctx)
        en_US.write_text(localization.code)

        content_path = content_dir / f'{content.get_internal_name()}.cs'
        content_path.write_text(f"""using Terraria;
using Terraria.ID;
using Terraria.ModLoader;
using Terraria.Localization;

namespace {mod_name}.Content
{{
{build_ctx.class_code}
}}
""")
    
    tmod_targets = Path('C:/Program Files (x86)/Steam/steamapps/common/tModLoader/tMLMod.targets')
    if not tmod_targets.exists():
        return False

    res = run(f'dotnet msbuild {csproj.as_posix()} -restore')
    if res.returncode != 0:
        return False
    
    res = run(f'dotnet msbuild {csproj.as_posix()} -t:build')
    if res.returncode != 0:
        return False
    
    return True
