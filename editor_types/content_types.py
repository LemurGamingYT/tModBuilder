from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import override
from shutil import copyfile

from editor_types.data_types import Int, Float, String, Bool, Image, Rarity, CoinValue
from pages.editor.builder import BuildContext, Localization, Method, Property, PropertyFlags


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

    @override
    def get_name(self):
        return self.name.value
    
    @override
    def build_localization(self, ctx):
        return Localization(
            f'Items.{self.get_internal_name()}',
            {
                'DisplayName': self.get_name(),
                'Tooltip': self.tooltip.value
            }
        )
    
    @override
    def build(self, ctx: BuildContext):
        width, height = self.texture.image.size

        copyfile(self.texture.path, ctx.build_dir / 'Content' / f'{self.get_internal_name()}.png')
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
    
    @override
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

    @override
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

@dataclass
class Accessory(Item):
    movement_speed: Float = field(default_factory=Float)
    jump_height: Float = field(default_factory=Float)
    no_fall_damage: Bool = field(default_factory=Bool)
    
    @override
    def build_localization(self, ctx):
        local = super().build_localization(ctx)
        
        accessory_tooltips = []
        if self.movement_speed.value > 0:
            accessory_tooltips.append('Increases movement speed by {0}%')
        elif self.movement_speed.value < 0:
            accessory_tooltips.append('Decreases movement speed by {0}%')
        
        if self.jump_height.value > 0:
            accessory_tooltips.append('Increases jump height')
        elif self.jump_height.value < 0:
            accessory_tooltips.append('Decreases jump height')
        
        if self.no_fall_damage.value:
            accessory_tooltips.append('Negates fall damage')
        
        accessory_tooltips_str = '\n'.join(accessory_tooltips)
        local.keys['Tooltip'] = f"""'''{accessory_tooltips_str}
{local.keys['Tooltip']}
'''"""
        
        return local

    @override
    def build(self, ctx: BuildContext):
        super().build(ctx)

        set_defaults = ctx.find_method('SetDefaults')
        assert set_defaults is not None

        set_defaults.body_code += """
Item.accessory = true;
"""

        ctx.class_properties.append(Property(
            'MovementSpeedIncrease', 'float', str(self.movement_speed), flags=PropertyFlags(readonly=True)
        ))
        
        ctx.class_properties.append(Property(
            'IncreaseJumpHeight', 'float', str(self.jump_height), flags=PropertyFlags(readonly=True)
        ))
        
        ctx.class_properties.append(Property(
            'Tooltip', 'LocalizedText', 'base.Tooltip.WithFormatArgs(MovementSpeedIncrease)', False,
            flags=PropertyFlags(override=True)
        ))
        
        ctx.class_methods.append(Method(
            'UpdateAccessory', [('Player', 'player'), ('bool', 'hideVisual')],
            'void', f"""
player.moveSpeed += {self.movement_speed} / 100f;
player.jumpSpeedBoost += {self.jump_height} / 100f;
player.noFallDmg = {self.no_fall_damage};
"""))


CONTENT_TYPES = [Item, Material, Accessory, Sword]
