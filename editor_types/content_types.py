from editor_types.data_types import Int, Float, String, Bool, Image, Rarity, CoinValue
from abc import ABC, abstractmethod
from dataclasses import dataclass
from shutil import copyfile
from pathlib import Path


@dataclass
class ContentType(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """The name that appears on the 'Mod Content' bar in the editor."""
    
    def get_internal_name(self) -> str:
        """The name that appears in the .cs file. Must not have special characters.
Defaults to removing all spaces from the result of `.get_name()`."""

        return self.get_name().replace(' ', '')
    
    @staticmethod
    @abstractmethod
    def default():
        """The default value for this content type."""
    
    @abstractmethod
    def build(self, build_folder: Path):
        """Build the content type into C# code.
Should return a string of what should be written to the .cs file."""

    @abstractmethod
    def build_localization(self):
        """Build the localization code for this content type.
Should return a string of what should be written to the .hjson localization file."""


@dataclass
class Item(ContentType):
    name: String
    tooltip: String

    value: CoinValue
    texture: Image
    rarity: Rarity

    def get_name(self):
        return self.name.value
    
    @staticmethod
    def default():
        return Item(String(), String(), CoinValue(), Image(), Rarity())
    
    def build_localization(self):
        return f"""Items.{self.get_internal_name()}: {{
    DisplayName: {self.get_name()}
    Tooltip: {self.tooltip}
}}"""
    
    def build(self, build_folder):
        width, height = self.texture.image.size

        copyfile(self.texture.path, build_folder / self.texture.path.name)
        return f"""using Terraria;
using Terraria.ID;
using Terraria.ModLoader;

public class {self.get_internal_name()} : ModItem
{{
    public override void SetDefaults()
    {{
        Item.height = {height};
        Item.width = {width};

        Item.rare = {self.rarity};
        Item.value = {self.value};
    }}
}}
"""

@dataclass
class Material(Item):
    max_stack: Int
    research_amount: Int

    @staticmethod
    def default():
        return Material(
            String(), String(), CoinValue(), Image(), Rarity(), Int(9999), Int(99)
        )
    
    def build(self, build_folder):
        super().build(build_folder)
        width, height = self.texture.image.size

        return f"""using Terraria.ModLoader;
using Terraria.ID;
using Terraria;

public class {self.get_internal_name()} : ModItem
{{
    public override void SetStaticDefaults()
    {{
        Item.ResearchUnlockCount = {self.research_amount};
    }}

    public override void SetDefaults()
    {{
        Item.maxStack = {self.max_stack};
        Item.height = {height};
        Item.width = {width};

        Item.material = true;

        Item.rare = {self.rarity};
        Item.value = {self.value};
    }}
}}
"""

@dataclass
class Sword(Item):
    damage: Int
    knockback: Float
    crit_chance: Int
    auto_reuse: Bool

    @staticmethod
    def default():
        return Sword(
            String('Unnamed Sword'), String(), CoinValue(), Image(), Rarity(), Int(), Float(),
            Int(), Bool()
        )

    def build(self, build_folder):
        super().build(build_folder)
        width, height = self.texture.image.size

        return f"""using Terraria.ModLoader;
using Terraria.ID;
using Terraria;

public class {self.get_internal_name()} : ModItem
{{
    public override void SetDefaults()
    {{
        Item.height = {height};
        Item.width = {width};

        Item.damage = {self.damage};
        Item.knockBack = {self.knockback};
        Item.crit = {self.crit_chance};

        Item.autoReuse = {self.auto_reuse};

        Item.rare = {self.rarity};

        Item.useTime = 20;
        Item.useTurn = true;
        Item.useAnimation = 20;
        Item.DamageType = DamageClass.Melee;
        Item.useStyle = ItemUseStyleID.Swing;
        Item.value = {self.value};
    }}
}}
"""


CONTENT_TYPES = [Sword, Material]
