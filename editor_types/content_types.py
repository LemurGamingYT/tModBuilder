from editor_types.data_types import Int, Float, String, Bool, Image, Rarity, CoinValue
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from shutil import copyfile

from editor.builder import BuildContext, Localization, Method


@dataclass
class ContentType(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """The name that appears on the 'Mod Content' bar in the editor."""
    
    def get_internal_name(self) -> str:
        """The name that appears in the .cs file. Must not have special characters.
Defaults to removing all spaces from the result of `.get_name()`."""

        return self.get_name().replace(' ', '')
    
    @abstractmethod
    def build(self, ctx: BuildContext):
        """Build the content type into C# code."""

    @abstractmethod
    def build_localization(self, ctx: BuildContext) -> Localization:
        """Build the localization code for this content type."""


@dataclass
class Item(ContentType):
    name: String = field(default_factory=String)
    tooltip: String = field(default_factory=String)

    value: CoinValue = field(default_factory=CoinValue)
    texture: Image = field(default_factory=Image)
    rarity: Rarity = field(default_factory=Rarity)

    def get_name(self):
        return self.name.value
    
    def build_localization(self, _):
        return Localization(
            f'Items.{self.get_internal_name()}',
            {
                'DisplayName': self.get_name(),
                'Tooltip': self.tooltip
            }
        )
    
    def build(self, ctx: BuildContext):
        width, height = self.texture.image.size

        copyfile(self.texture.path, ctx.build_dir / self.texture.path.name)
        ctx.class_bases.append('ModItem')
        ctx.class_methods.append(Method(
            'SetDefaults', [], 'void', f"""Item.height = {height};
Item.width = {width};

Item.rare = {self.rarity};
Item.value = {self.value};
"""
        ))

@dataclass
class Material(Item):
    max_stack: Int = field(default_factory=lambda: Int(9999))
    research_amount: Int = field(default_factory=lambda: Int(99))
    
    def build(self, ctx: BuildContext):
        super().build(ctx)

        ctx.class_methods.append(Method(
            'SetStaticDefaults', [], 'void', f'Item.ResearchUnlockCount = {self.research_amount};'
        ))

        set_defaults = ctx.find_method('SetDefaults')
        assert set_defaults is not None

        set_defaults.body_code += f'\nItem.maxStack = {self.max_stack};'

@dataclass
class Sword(Item):
    damage: Int = field(default_factory=Int)
    knockback: Float = field(default_factory=Float)
    crit_chance: Int = field(default_factory=Int)
    auto_reuse: Bool = field(default_factory=lambda: Bool(True))
    use_time: Int = field(default_factory=lambda: Int(20))
    use_animation: Int = field(default_factory=lambda: Int(20))
    use_turn: Bool = field(default_factory=lambda: Bool(True))

    def build(self, ctx: BuildContext):
        super().build(ctx)

        set_defaults = ctx.find_method('SetDefaults')
        assert set_defaults is not None

        set_defaults.body_code += f"""
Item.autoReuse = {self.auto_reuse};
Item.useTime = {self.use_time};
Item.useAnimation = {self.use_animation};
Item.useTurn = {self.use_turn};
Item.DamageType = DamageClass.Melee;
Item.useStyle = ItemUseStyleID.Swing;

Item.SetWeaponValues({self.damage}, {self.knockback}, {self.crit_chance});
"""


CONTENT_TYPES = [Sword, Material]
