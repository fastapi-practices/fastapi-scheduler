import type { ThemeConfig } from 'antdv-next';
import { defu } from 'defu';
import { addColorAlpha, getColorPalette, getPaletteColorByNumber, getRgb } from '@sa/color';
import { DARK_CLASS } from '@/constants/app';
import { toggleHtmlClass } from '@/utils/common';
import { localStg } from '@/utils/storage';
import { overrideThemeSettings, themeSettings } from '@/theme/settings';
import { themeVars } from '@/theme/vars';

const NAIVE_FONT_SIZE = 14;
const NAIVE_FONT_SIZE_LARGE = 15;
const NAIVE_FONT_SIZE_HUGE = 16;

/** Init theme settings */
export function initThemeSettings() {
  const isProd = import.meta.env.PROD;

  // if it is development mode, the theme settings will not be cached, by update `themeSettings` in `src/theme/settings.ts` to update theme settings
  if (!isProd) return themeSettings;

  // if it is production mode, the theme settings will be cached in localStorage
  // if want to update theme settings when publish new version, please update `overrideThemeSettings` in `src/theme/settings.ts`

  const localSettings = localStg.get('themeSettings');

  let settings = defu(localSettings, themeSettings);

  const isOverride = localStg.get('overrideThemeFlag') === BUILD_TIME;

  if (!isOverride) {
    settings = defu(overrideThemeSettings, settings);

    localStg.set('overrideThemeFlag', BUILD_TIME);
  }

  return settings;
}

/**
 * create theme token css vars value by theme settings
 *
 * @param colors Theme colors
 * @param tokens Theme setting tokens
 * @param [recommended=false] Use recommended color. Default is `false`
 */
export function createThemeToken(
  colors: App.Theme.ThemeColor,
  tokens?: App.Theme.ThemeSetting['tokens'],
  recommended = false
) {
  const paletteColors = createThemePaletteColors(colors, recommended);

  const { light, dark } = tokens || themeSettings.tokens;

  const themeTokens: App.Theme.ThemeTokenCSSVars = {
    colors: {
      ...paletteColors,
      nprogress: paletteColors.primary,
      ...light.colors
    },
    boxShadow: {
      ...light.boxShadow
    }
  };

  const darkThemeTokens: App.Theme.ThemeTokenCSSVars = {
    colors: {
      ...themeTokens.colors,
      ...dark?.colors
    },
    boxShadow: {
      ...themeTokens.boxShadow,
      ...dark?.boxShadow
    }
  };

  return {
    themeTokens,
    darkThemeTokens
  };
}

/**
 * Create theme palette colors
 *
 * @param colors Theme colors
 * @param [recommended=false] Use recommended color. Default is `false`
 */
function createThemePaletteColors(colors: App.Theme.ThemeColor, recommended = false) {
  const colorKeys = Object.keys(colors) as App.Theme.ThemeColorKey[];
  const colorPaletteVar = {} as App.Theme.ThemePaletteColor;

  colorKeys.forEach(key => {
    const colorMap = getColorPalette(colors[key], recommended);

    colorPaletteVar[key] = colorMap.get(500)!;

    colorMap.forEach((hex, number) => {
      colorPaletteVar[`${key}-${number}`] = hex;
    });
  });

  return colorPaletteVar;
}

/**
 * Get css var by tokens
 *
 * @param tokens Theme base tokens
 */
function getCssVarByTokens(tokens: App.Theme.BaseToken) {
  const styles: string[] = [];

  function removeVarPrefix(value: string) {
    return value.replace('var(', '').replace(')', '');
  }

  function removeRgbPrefix(value: string) {
    return value.replace('rgb(', '').replace(')', '');
  }

  for (const [key, tokenValues] of Object.entries(themeVars)) {
    for (const [tokenKey, tokenValue] of Object.entries(tokenValues)) {
      let cssVarsKey = removeVarPrefix(tokenValue);
      let cssValue = tokens[key][tokenKey];

      if (key === 'colors') {
        cssVarsKey = removeRgbPrefix(cssVarsKey);
        const { r, g, b } = getRgb(cssValue);
        cssValue = `${r} ${g} ${b}`;
      }

      styles.push(`${cssVarsKey}: ${cssValue}`);
    }
  }

  const styleStr = styles.join(';');

  return styleStr;
}

/**
 * Add theme vars to global
 *
 * @param tokens
 */
export function addThemeVarsToGlobal(tokens: App.Theme.BaseToken, darkTokens: App.Theme.BaseToken) {
  const cssVarStr = getCssVarByTokens(tokens);
  const darkCssVarStr = getCssVarByTokens(darkTokens);

  const css = `
    :root {
      ${cssVarStr}
    }
  `;

  const darkCss = `
    html.${DARK_CLASS} {
      ${darkCssVarStr}
    }
  `;

  const styleId = 'theme-vars';

  const style = document.querySelector(`#${styleId}`) || document.createElement('style');

  style.id = styleId;

  style.textContent = css + darkCss;

  document.head.appendChild(style);
}

/**
 * Toggle css dark mode
 *
 * @param darkMode Is dark mode
 */
export function toggleCssDarkMode(darkMode = false) {
  const { add, remove } = toggleHtmlClass(DARK_CLASS);

  if (darkMode) {
    add();
  } else {
    remove();
  }
}

/**
 * Toggle auxiliary color modes
 *
 * @param grayscaleMode
 * @param colourWeakness
 */
export function toggleAuxiliaryColorModes(grayscaleMode = false, colourWeakness = false) {
  const htmlElement = document.documentElement;
  htmlElement.style.filter = [grayscaleMode ? 'grayscale(100%)' : '', colourWeakness ? 'invert(80%)' : '']
    .filter(Boolean)
    .join(' ');
}

/**
 * Get Antdv Next theme
 *
 * @param colors Theme colors
 * @param settings Theme settings object
 * @param overrides Optional manual overrides from preset
 */
export function getAntdvTheme(colors: App.Theme.ThemeColor, settings: App.Theme.ThemeSetting, overrides?: ThemeConfig) {
  const primaryHover = getPaletteColorByNumber(colors.primary, 500, settings.recommendColor);
  const primaryActive = getPaletteColorByNumber(colors.primary, 700, settings.recommendColor);

  const theme: ThemeConfig = {
    token: {
      ...getAntdvThemeColors(colors, settings.recommendColor),
      colorPrimary: colors.primary,
      colorInfo: colors.info,
      colorSuccess: colors.success,
      colorWarning: colors.warning,
      colorError: colors.error,
      colorLink: colors.primary,
      colorLinkHover: primaryHover,
      colorLinkActive: primaryActive,
      colorBgContainer: 'rgb(var(--container-bg-color))',
      colorBgLayout: 'rgb(var(--layout-bg-color))',
      colorText: 'rgb(var(--base-text-color))',
      colorTextHeading: 'rgb(var(--base-text-color))',
      colorSplit: 'rgb(var(--base-text-color) / 0.12)',
      fontSize: NAIVE_FONT_SIZE,
      fontSizeSM: NAIVE_FONT_SIZE,
      fontSizeLG: NAIVE_FONT_SIZE_LARGE,
      fontSizeXL: NAIVE_FONT_SIZE_HUGE,
      borderRadius: settings.themeRadius,
      borderRadiusLG: settings.themeRadius,
      borderRadiusSM: Math.max(settings.themeRadius - 2, 2),
      controlHeight: 34,
      controlHeightSM: 28,
      controlHeightLG: 40,
      controlOutline: addColorAlpha(colors.primary, 0.2)
    },
    components: {
      Alert: {
        defaultPadding: '8px 12px',
        withDescriptionPadding: '8px 12px',
        fontSize: NAIVE_FONT_SIZE
      },
      Button: {
        defaultShadow: 'none',
        primaryShadow: 'none',
        dangerShadow: 'none',
        textHoverBg: addColorAlpha(colors.primary, 0.1),
        contentFontSize: NAIVE_FONT_SIZE,
        contentFontSizeSM: NAIVE_FONT_SIZE,
        contentFontSizeLG: NAIVE_FONT_SIZE_LARGE
      },
      Card: {
        bodyPadding: 24,
        bodyPaddingSM: 12,
        headerPadding: 24,
        headerPaddingSM: 16,
        headerFontSize: NAIVE_FONT_SIZE_HUGE,
        headerFontSizeSM: NAIVE_FONT_SIZE
      },
      Input: {
        activeShadow: 'none',
        errorActiveShadow: 'none',
        warningActiveShadow: 'none',
        inputFontSize: NAIVE_FONT_SIZE,
        inputFontSizeSM: NAIVE_FONT_SIZE,
        inputFontSizeLG: NAIVE_FONT_SIZE_LARGE
      },
      InputNumber: {
        activeShadow: 'none',
        errorActiveShadow: 'none',
        warningActiveShadow: 'none',
        inputFontSize: NAIVE_FONT_SIZE,
        inputFontSizeSM: NAIVE_FONT_SIZE,
        inputFontSizeLG: NAIVE_FONT_SIZE_LARGE
      },
      Menu: {
        itemBorderRadius: settings.themeRadius,
        subMenuItemBorderRadius: settings.themeRadius,
        itemSelectedBg: addColorAlpha(colors.primary, 0.1),
        itemSelectedColor: colors.primary,
        itemActiveBg: addColorAlpha(colors.primary, 0.1)
      },
      Select: {
        activeOutlineColor: addColorAlpha(colors.primary, 0.2),
        optionSelectedBg: addColorAlpha(colors.primary, 0.1),
        optionSelectedColor: colors.primary,
        optionFontSize: NAIVE_FONT_SIZE
      },
      Segmented: {
        trackBg: 'rgba(0, 0, 0, 0.06)',
        itemSelectedColor: colors.primary
      },
      Switch: {
        trackHeight: 22,
        trackMinWidth: 40,
        trackHeightSM: 18,
        trackMinWidthSM: 28
      },
      Tag: {
        borderRadiusSM: settings.themeRadius
      },
      Table: {
        headerBg: addColorAlpha(colors.primary, 0.04),
        rowHoverBg: addColorAlpha(colors.primary, 0.06),
        cellFontSize: NAIVE_FONT_SIZE,
        cellFontSizeMD: NAIVE_FONT_SIZE,
        cellFontSizeSM: NAIVE_FONT_SIZE
      }
    }
  };

  // Preset overrides have higher priority than generated tokens
  return overrides ? defu(overrides, theme) : theme;
}

function getAntdvThemeColors(colors: App.Theme.ThemeColor, recommended = false): NonNullable<ThemeConfig['token']> {
  const tokens: Record<string, string> = {};
  const colorEntries = Object.entries(colors) as [App.Theme.ThemeColorKey, string][];

  colorEntries.forEach(([key, color]) => {
    const tokenKey = key.replace(/^\w/, char => char.toUpperCase());
    const hover = getPaletteColorByNumber(color, 500, recommended);
    const active = getPaletteColorByNumber(color, 700, recommended);

    tokens[`color${tokenKey}`] = color;
    tokens[`color${tokenKey}Hover`] = hover;
    tokens[`color${tokenKey}Active`] = active;
    tokens[`color${tokenKey}Bg`] = addColorAlpha(color, 0.1);
    tokens[`color${tokenKey}BgHover`] = addColorAlpha(color, 0.16);
    tokens[`color${tokenKey}Border`] = addColorAlpha(color, 0.28);
    tokens[`color${tokenKey}BorderHover`] = hover;
    tokens[`color${tokenKey}Text`] = color;
    tokens[`color${tokenKey}TextHover`] = hover;
    tokens[`color${tokenKey}TextActive`] = active;
  });

  return tokens as NonNullable<ThemeConfig['token']>;
}
