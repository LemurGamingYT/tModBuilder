from dataclasses import dataclass, field
from shutil import copyfile
from subprocess import run
from pathlib import Path

from project import Project


@dataclass
class Method:
    name: str
    params: list[str]
    return_type: str
    body_code: str

    @property
    def code(self):
        return f"""public override {self.return_type} {self.name}({', '.join(self.params)}) {{
    {self.body_code}
}}
"""

@dataclass
class Localization:
    name: str
    keys: dict[str, str] = field(default_factory=dict)

    @property
    def code(self):
        return f"""{self.name}: {{
    {', '.join(f'    {key}: {value}' for key, value in self.keys.items())}
}}
"""

@dataclass
class BuildContext:
    mod_name: str
    build_dir: Path
    project: Project
    class_name: str
    class_bases: list[str]
    class_methods: list[Method]

    @property
    def class_code(self):
        return f"""public class {self.class_name} : {', '.join(self.class_bases)}
{{
    {'\n'.join(method.code for method in self.class_methods)}
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
        build_ctx = BuildContext(mod_name, build_dir, project, content.get_internal_name(), [], [])
        content.build(build_ctx)
        localization = content.build_localization(build_ctx)
        en_US.write_text(localization.code)

        content_path = content_dir / f'{content.get_internal_name()}.cs'
        content_path.write_text(f"""namespace {mod_name}.Content
{{
{build_ctx.class_code}
}}
""")

    run(f'dotnet msbuild {csproj.as_posix()} -restore')
    run(f'dotnet msbuild {csproj.as_posix()} -t:build')
