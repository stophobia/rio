from __future__ import annotations

import typing as t
from dataclasses import KW_ONLY, dataclass

from uniserde import Jsonable

import rio

from . import color, deprecations
from . import text_style as text_style_module

__all__ = [
    "Palette",
    "Theme",
]


T = t.TypeVar("T")


def _derive_color(
    color: rio.Color,
    offset: float,
    *,
    bias_to_bright: float = 0,
    target_color: rio.Color | None = None,
) -> rio.Color:
    """
    Given a base color, derive a related, but different color. The idea is to
    shift the color slightly to create a new color that can be used to create
    visual interest.

    ## Params

    `base_color`: The color to derive a new color from.

    `offset`: Controls how much the color should be shifted. A value of `0` will
        return the original color, while a value of `1` will return a massively
        different color.

    `bias_to_bright`: A value between `-1` and `1` that controls how much the
        new color should be biased towards brighter or darker colors. A value
        of `-1` will always return a darker color, while a value of `1` will
        always return a brighter color.

    `target_color`: If provided, the new color will be biased towards this
        color. This can be used to tint the color towards a specific hue.
    """
    assert 0 <= offset <= 1, f"The offset must be between 0 and 1, not {offset}"
    assert (
        -1 <= bias_to_bright <= 1
    ), f'The "bias_to_bright" must be between -1 and 1, not {bias_to_bright}'

    # If a target color was provided, move towards that color
    #
    # The more different the two colors are, the less the new color will be
    # used. This helps e.g. with dark themes, which look bonkers if the target
    # color is very light.
    if target_color is not None:
        difference = abs(
            target_color.perceived_brightness - color.perceived_brightness
        )

        if difference < 0.01:
            offset_scale = 1
        else:
            offset_scale = min(1.5 / difference, 1)

        result = color.blend(target_color, offset * offset_scale)

    # Otherwise change the color's brightness
    else:
        threshold = 0.5 + 0.5 * bias_to_bright
        perceived_brightness = color.perceived_brightness
        brighten = perceived_brightness <= threshold

        # Calculate the new color
        if brighten:
            result = color.brighter(offset)
        else:
            result = color.darker(offset)

    return result


def _make_semantic_palette(color: rio.Color) -> Palette:
    return Palette(
        background=color,
        background_variant=_derive_color(
            color,
            0.08,
            bias_to_bright=-0.4,
        ),
        background_active=_derive_color(
            color,
            0.15,
            bias_to_bright=0.8,
        ),
        foreground=_derive_color(
            color,
            0.4,
        ),
    )


@t.final
@dataclass()
class Palette:
    background: rio.Color
    background_variant: rio.Color
    background_active: rio.Color

    foreground: rio.Color

    @staticmethod
    def from_color(
        color: rio.Color,
        *,
        offset: float = 1,
        target_color: rio.Color | None = None,
    ) -> Palette:
        """
        ## Metadata

        experimental: True
        """
        return Palette(
            background=color,
            background_variant=_derive_color(
                color,
                offset=0.1 * offset,
                bias_to_bright=-0.3,
                target_color=target_color,
            ),
            background_active=_derive_color(
                color,
                offset=0.2 * offset,
                bias_to_bright=-0.3,
                target_color=target_color,
            ),
            foreground=_derive_color(
                color,
                offset=0.8,
            ),
        )


@t.final
@dataclass()
class Theme:
    """
    Defines the visual style of the application.

    The `Theme` contains all colors, text styles, and other visual properties
    that are used throughout the application. If you wish to change the
    appearance of your app, this is the place to do it.

    Warning: The exact attributes available in themes are still subject to
        change. The recommended way to create themes is using either the
        `from_colors` or `pair_from_colors` method, as they provide a more
        stable interface.
    """

    _: KW_ONLY

    primary_palette: Palette
    secondary_palette: Palette

    background_palette: Palette
    neutral_palette: Palette
    hud_palette: Palette
    disabled_palette: Palette

    success_palette: Palette
    warning_palette: Palette
    danger_palette: Palette

    # Other
    corner_radius_small: float
    corner_radius_medium: float
    corner_radius_large: float

    shadow_color: rio.Color

    monospace_font: text_style_module.Font

    # Text styles
    heading1_style: rio.TextStyle
    heading2_style: rio.TextStyle
    heading3_style: rio.TextStyle
    text_style: rio.TextStyle

    def __init__(self) -> None:
        # Themes are still very much in flux. New attributes will be added,
        # removed and changed. Stop anyone from trying to create a theme
        # manually, as that is an endeavor doomed to fail.
        """
        Do not use. Themes are still in flux and should be created using the
        `from_colors` or `pair_from_colors` methods.

        ## Metadata

        `public`: False
        """

    @staticmethod
    def _create_new(
        primary_palette: Palette,
        secondary_palette: Palette,
        background_palette: Palette,
        neutral_palette: Palette,
        hud_palette: Palette,
        disabled_palette: Palette,
        success_palette: Palette,
        warning_palette: Palette,
        danger_palette: Palette,
        corner_radius_small: float,
        corner_radius_medium: float,
        corner_radius_large: float,
        shadow_color: rio.Color,
        monospace_font: text_style_module.Font,
        heading1_style: rio.TextStyle,
        heading2_style: rio.TextStyle,
        heading3_style: rio.TextStyle,
        text_style: rio.TextStyle,
    ) -> Theme:
        """
        The Theme's constructor is blocked to prevent users from creating themes
        manually. This is an internal method that bypasses that block.
        """
        self = object.__new__(Theme)

        self.__dict__.update(
            {
                "primary_palette": primary_palette,
                "secondary_palette": secondary_palette,
                "background_palette": background_palette,
                "neutral_palette": neutral_palette,
                "hud_palette": hud_palette,
                "disabled_palette": disabled_palette,
                "success_palette": success_palette,
                "warning_palette": warning_palette,
                "danger_palette": danger_palette,
                "corner_radius_small": corner_radius_small,
                "corner_radius_medium": corner_radius_medium,
                "corner_radius_large": corner_radius_large,
                "shadow_color": shadow_color,
                "monospace_font": monospace_font,
                "heading1_style": heading1_style,
                "heading2_style": heading2_style,
                "heading3_style": heading3_style,
                "text_style": text_style,
            }
        )

        return self

    @classmethod
    @deprecations.parameter_remapped(
        since="0.9.0",
        old_name="light",
        new_name="mode",
        remap=lambda light: "light" if light else "dark",
    )
    def from_colors(
        cls,
        *,
        primary_color: rio.Color | None = None,
        secondary_color: rio.Color | None = None,
        background_color: rio.Color | None = None,
        neutral_color: rio.Color | None = None,
        hud_color: rio.Color | None = None,
        disabled_color: rio.Color | None = None,
        success_color: rio.Color | None = None,
        warning_color: rio.Color | None = None,
        danger_color: rio.Color | None = None,
        corner_radius_small: float = 0.4,
        corner_radius_medium: float = 0.8,
        corner_radius_large: float = 1.8,
        heading_fill: t.Literal["primary", "plain", "auto"]
        | text_style_module._TextFill = "auto",
        text_color: rio.Color | None = None,
        font: rio.Font = text_style_module.Font.ROBOTO,
        heading_font: rio.Font | None = None,
        monospace_font: text_style_module.Font = text_style_module.Font.ROBOTO_MONO,
        mode: t.Literal["light", "dark"] = "light",
    ) -> rio.Theme:
        """
        Creates a new theme based on the provided colors.

        Themes store a large number of colors and text styles that are used
        throughout the app. This function provides a convenient way to only
        specify the most important colors of your theme, and have Rio handle the
        rest. It is the recommended way to create a new theme.

        To use a custom theme in your app first create a theme, and then pass it
        to your app instance

        ```python
        # Create a new theme
        theme = rio.Theme.from_colors(
            # Configure your theme here
        )

        # And apply it to your app
        app = rio.App(
            theme=theme,
            # ...
        )
        ```

        Alternatively, there is also `pair_from_colors`, which creates both a
        light and a dark theme at the same time. This is useful if you want Rio
        to automatically switch between the two based on the user's system
        preferences.


        ## Parameters

        `primary_color`: The main color of your app. This color will be used to
            tint the background and by some large components to fill large
            spaces with color.

        `secondary_color`: A color that nicely complements the primary color. It
            is often used by small components such as buttons and switches.

        `background_color`: The app's background color. This should be a neutral
            color that doesn't distract from the content.

        `neutral_color`: Similar to the background color, it is also used for
            neutral areas. It should however be slightly different, allowing you
            to create a visual hierarchy. This is the default color of large
            elements such as cards.

        `hud_color`: Used for elements that pop over the content, such as
            tooltips.

        `disabled_color`: Used by insensitive components to indicate that they
            are not interactive. Typically a shade of gray.

        `success_color`: A color to give positive feedback the user. Typically
            a shade of green.

        `warning_color`: A color to indicate that something might be wrong, but
            isn't critical. Typically orange.

        `danger_color`: A color to indicate that something is wrong and needs
            immediate attention. Typically a shade of red.

        `corner_radius_small`: The corner radius of small components such as
            text inputs

        `corner_radius_medium`: The corner radius of medium-sized components,
            such as small cards.

        `corner_radius_large`: The corner radius of large components, such as
            large cards and dialogs.

        `heading_fill`: The fill to use for headings. This allows you to specify
            a more interesting color, or even a gradient. If set to `"auto"`,
            Rio will automatically switch between the primary color and a plain
            text color based on legibility.

            This only affects headings in background and neutral contexts.

        `text_color`: The default text color to use for regular text. Please
            note that this only applies to text in a neutral or background
            context. Text that's e.g. placed on a `rio.Card` with
            `color="primary"` will use a different color to ensure legibility.

        `font`: The default font to use when no other is specified.

        `heading_font`: The font to use for text headings ("heading1",
            "heading2", ...). If not provided, the regular font will be used

        `monospace_font`: The font to use for monospace text, such as code.

        `mode`: Whether to create a light or dark theme. This affects the
            default values for some colors, such as the background.
        """

        # Primary palette
        if primary_color is None:
            primary_color = rio.Color.from_hex("01dffd")

        primary_palette = Palette.from_color(primary_color)

        # Secondary palette
        if secondary_color is None:
            secondary_color = rio.Color.from_hex("0083ff")

        secondary_palette = Palette.from_color(secondary_color)

        # Background palette
        if background_color is None:
            if mode == "light":
                background_color = rio.Color.from_rgb(0.96, 0.96, 0.93)
            else:
                background_color = rio.Color.from_gray(0.10)

        if text_color is None:
            neutral_and_background_text_color = (
                # Gray tones look good on bright themes
                rio.Color.from_gray(0.3)
                if background_color.perceived_brightness > 0.5
                # ... but not on dark ones. Go very bright here.
                else rio.Color.from_gray(0.9)
            )
        else:
            neutral_and_background_text_color = text_color

        del text_color

        if neutral_color is None:
            neutral_color = _derive_color(
                background_color,
                0.04,
            ).blend(primary_color, 0.06)

        background_palette = Palette(
            background=background_color,
            background_variant=neutral_color,
            background_active=_derive_color(
                background_color,
                0.25,
                bias_to_bright=0.15,
                target_color=primary_color,
            ),
            foreground=neutral_and_background_text_color,
        )

        # Neutral palette
        neutral_palette = Palette(
            background=neutral_color,
            background_variant=_derive_color(
                neutral_color,
                0.15,
                bias_to_bright=0.15,
                target_color=primary_color,
            ),
            background_active=_derive_color(
                neutral_color,
                0.25,
                bias_to_bright=0.15,
                target_color=primary_color,
            ),
            foreground=neutral_and_background_text_color,
        )

        # HUD palette
        if hud_color is None:
            if mode == "light":
                hud_color = rio.Color.from_gray(0.15)
            else:
                hud_color = rio.Color.from_gray(0.02)

        hud_palette = Palette(
            background=hud_color,
            background_variant=_derive_color(
                hud_color,
                0.08,
            ),
            background_active=_derive_color(
                hud_color,
                0.15,
            ),
            foreground=(
                rio.Color.from_gray(0.1)
                if hud_color.perceived_brightness > 0.5
                else rio.Color.from_gray(0.9)
            ),
        )

        # Keep the disabled palette subdued. It's not meant to be perfectly
        # readable
        if disabled_color is None:
            disabled_color = background_palette.background.blend(
                background_palette.foreground, 0.5
            )

        disabled_palette = Palette(
            background=disabled_color,
            background_variant=_derive_color(
                disabled_color, 0.2, bias_to_bright=-0.3
            ),
            background_active=_derive_color(
                disabled_color, 0.3, bias_to_bright=-0.3
            ),
            foreground=_derive_color(disabled_color, 0.4, bias_to_bright=0.2),
        )

        # Shadow color
        if mode == "light":
            shadow_color = rio.Color.from_rgb(0.1, 0.1, 0.2, 0.5)
        else:
            shadow_color = rio.Color.BLACK

        # Semantic colors
        if success_color is None:
            success_color = rio.Color.from_hex("1e8e3e")

        if warning_color is None:
            warning_color = rio.Color.from_hex("f9a825")

        if danger_color is None:
            danger_color = rio.Color.from_hex("b3261e")

        success_palette = _make_semantic_palette(success_color)
        warning_palette = _make_semantic_palette(warning_color)
        danger_palette = _make_semantic_palette(danger_color)

        # Colorful headings can be a problem when the primary color is similar
        # to the background/neutral color. If the `color_headings` argument is
        # set to `auto`, disable coloring if the colors are close.
        if heading_fill == "auto":
            brightness1 = primary_palette.background.perceived_brightness
            brightness2 = background_palette.background.perceived_brightness

            heading_fill = (
                "primary" if abs(brightness1 - brightness2) > 0.3 else "plain"
            )

        if heading_fill == "primary":
            heading_fill = primary_color
        elif heading_fill == "plain":
            heading_fill = neutral_and_background_text_color
        else:
            heading_fill = heading_fill

        # Text styles
        heading1_style = rio.TextStyle(
            font=font if heading_font is None else heading_font,
            fill=heading_fill,
            font_size=2.3,
        )
        heading2_style = heading1_style.replace(font_size=1.7)
        heading3_style = heading1_style.replace(font_size=1.2)
        text_style = heading1_style.replace(
            font=font,
            font_size=1,
            fill=neutral_and_background_text_color,
        )

        # Build the final theme
        # Instantiate the theme. `__init__` is blocked to prevent users from
        # doing something foolish. Work around that.
        return rio.Theme._create_new(
            primary_palette=primary_palette,
            secondary_palette=secondary_palette,
            background_palette=background_palette,
            neutral_palette=neutral_palette,
            hud_palette=hud_palette,
            disabled_palette=disabled_palette,
            success_palette=success_palette,
            warning_palette=warning_palette,
            danger_palette=danger_palette,
            corner_radius_small=corner_radius_small,
            corner_radius_medium=corner_radius_medium,
            corner_radius_large=corner_radius_large,
            shadow_color=shadow_color,
            monospace_font=monospace_font,
            heading1_style=heading1_style,
            heading2_style=heading2_style,
            heading3_style=heading3_style,
            text_style=text_style,
        )

    @classmethod
    def pair_from_colors(
        cls,
        *,
        primary_color: rio.Color | None = None,
        secondary_color: rio.Color | None = None,
        background_color: rio.Color | None = None,
        neutral_color: rio.Color | None = None,
        hud_color: rio.Color | None = None,
        disabled_color: rio.Color | None = None,
        success_color: rio.Color | None = None,
        warning_color: rio.Color | None = None,
        danger_color: rio.Color | None = None,
        corner_radius_small: float = 0.4,
        corner_radius_medium: float = 0.8,
        corner_radius_large: float = 1.8,
        text_color: rio.Color
        | tuple[rio.Color | None, rio.Color | None]
        | None = None,
        font: text_style_module.Font = text_style_module.Font.ROBOTO,
        heading_font: rio.Font | None = None,
        monospace_font: text_style_module.Font = text_style_module.Font.ROBOTO_MONO,
        heading_fill: t.Literal["primary", "plain", "auto"]
        | text_style_module._TextFill = "auto",
    ) -> tuple[Theme, Theme]:
        """
        This function is very similar to `from_colors`, but it returns two
        themes: A light and a dark one. When applying two themes to your app,
        Rio will automatically switch between them based on the user's system
        preferences.

        ```python
        # Create a theme pair
        themes = rio.Theme.pair_from_colors(
            # Configure your theme here
        )

        # And apply them to your app
        app = rio.App(
            theme=themes,
            # ...
        )
        ```

        ## Parameters

        `primary_color`: The main color of your app. This color will be used to
            tint the background and by some large components to fill large
            spaces with color

        `secondary_color`: A color that nicely complements the primary color. It
            is often used by small components such as buttons and switches.

        `background_color`: The app's background color. This should be a neutral
            color that doesn't distract from the content.

        `neutral_color`: Similar to the background color, it is also used for
            neutral areas. It should however be slightly different, allowing you
            to create a visual hierarchy. This is the default color of large
            elements such as cards.

        `hud_color`: Used for elements that pop over the content, such as
            tooltips.

        `disabled_color`: Used by insensitive components to indicate that they
            are not interactive. Typically a shade of gray.

        `success_color`: A color to give positive feedback the user. Typically
            a shade of green.

        `warning_color`: A color to indicate that something might be wrong, but
            isn't critical. Typically orange.

        `danger_color`: A color to indicate that something is wrong and needs
            immediate attention. Typically a shade of red.

        `corner_radius_small`: The corner radius of small components such as
            text inputs

        `corner_radius_medium`: The corner radius of medium-sized components,
            such as small cards.

        `corner_radius_large`: The corner radius of large components, such as
            large cards and dialogs.

        `heading_fill`: The fill to use for headings. This allows you to specify
            a more interesting color, or even a gradient. If set to `"auto"`,
            Rio will automatically switch between the primary color and a plain
            text color based on legibility.

            This only affects headings in background and neutral contexts.

        `text_color`: The default text color to use for regular text. Please
            note that this only applies to text in a neutral or background
            context. Text that's e.g. placed on a `rio.Card` with
            `color="primary"` will use a different color to ensure legibility.

            You can also specify a tuple of two colors to use different text
            colors for light and dark themes.

        `font`: The default font to use when no other is specified.

        `heading_font`: The font to use for text headings ("heading1",
            "heading2", ...). If not provided, the regular font will be used

        `monospace_font`: The font to use for monospace text, such as code.
        """
        if not isinstance(text_color, tuple):
            text_color = (text_color, text_color)

        themes = list[Theme]()
        for mode, text_color in zip(("light", "dark"), text_color):
            themes.append(
                cls.from_colors(
                    primary_color=primary_color,
                    secondary_color=secondary_color,
                    background_color=background_color,
                    neutral_color=neutral_color,
                    hud_color=hud_color,
                    disabled_color=disabled_color,
                    success_color=success_color,
                    warning_color=warning_color,
                    danger_color=danger_color,
                    corner_radius_small=corner_radius_small,
                    corner_radius_medium=corner_radius_medium,
                    corner_radius_large=corner_radius_large,
                    font=font,
                    heading_font=heading_font,
                    monospace_font=monospace_font,
                    heading_fill=heading_fill,
                    text_color=text_color,
                    mode=mode,
                )
            )

        return tuple(themes)  # type: ignore (length mismatch)

    def text_color_for(self, color: rio.Color) -> rio.Color:
        """
        Given the color of a background, return a legible text color to use on
        top of it.
        """
        return _derive_color(color, offset=0.8)

    def _serialize_colorset(self, color: color.ColorSet) -> Jsonable:
        # A colorset more-or-less translates to a switcheroo. Thus, this
        # function needs to provide all information needed to create one.

        # If the color is a string, just pass it through. In this case there is
        # an actual switcheroo which can be used.
        if isinstance(color, str):
            return color

        # TODO: If the color is identical/very similar to a theme color use the
        #       corresponding switcheroo.

        # Otherwise create all the necessary variables to emulate a switcheroo.
        palette = Palette.from_color(color)

        return {
            "localBg": palette.background.srgba,
            "localBgVariant": palette.background_variant.srgba,
            "localBgActive": palette.background_active.srgba,
            "localFg": palette.foreground.srgba,
        }

    @property
    def is_light_theme(self) -> bool:
        return self.background_palette.background.perceived_brightness >= 0.5

    @property
    def primary_color(self) -> rio.Color:
        return self.primary_palette.background

    @property
    def secondary_color(self) -> rio.Color:
        return self.secondary_palette.background

    @property
    def background_color(self) -> rio.Color:
        return self.background_palette.background

    @property
    def neutral_color(self) -> rio.Color:
        return self.neutral_palette.background

    @property
    def hud_color(self) -> rio.Color:
        return self.hud_palette.background

    @property
    def disabled_color(self) -> rio.Color:
        return self.disabled_palette.background

    @property
    def success_color(self) -> rio.Color:
        return self.success_palette.background

    @property
    def warning_color(self) -> rio.Color:
        return self.warning_palette.background

    @property
    def danger_color(self) -> rio.Color:
        return self.danger_palette.background

    @property
    def font(self) -> text_style_module.Font:
        assert (
            self.text_style.font is not None
        ), f"The theme's text style must have a font set"
        return self.text_style.font
