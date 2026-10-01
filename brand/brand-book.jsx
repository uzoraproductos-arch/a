import { useState } from "react";

// ============================================================================
// Auditavisión: brand book interactivo
// Generado con el skill brand-book-generator (jsx-template.md) a partir de
// DESIGN.md. Cada valor viene de DESIGN.md y de
// assets/auditor/css/auditavision.css: si alguno cambia allá, se cambia aquí.
// ============================================================================

// 1. Color: los dos temas del sitio, con los mismos nombres de variable
const colors = {
  dark: {
    base: "#0c0e15",
    void: "#06070a",
    surface: "rgba(12, 14, 21, 0.72)",
    card: "rgba(18, 21, 32, 0.62)",
    cardAlt: "rgba(23, 27, 41, 0.52)",
    cardHover: "rgba(28, 33, 51, 0.80)",
    borderSubtle: "rgba(255, 255, 255, 0.10)",
    borderAccent: "rgba(255, 255, 255, 0.18)",
    borderGold: "rgba(201, 168, 76, 0.40)",
    gold: "#c9a84c",
    goldBright: "#f3cf65",
    textGold: "#e8c86a",
    goldGlow: "rgba(201, 168, 76, 0.18)",
    goldGradient: "linear-gradient(135deg, #e8c86a 0%, #c9a84c 50%, #9a7828 100%)",
    crimson: "#8b1a1a",
    crimsonBright: "#e74c3c",
    emerald: "#1e824c",
    emeraldBright: "#2ecc71",
    amber: "#f39c12",
    orange: "#e67e22",
    cyan: "#4ecdc4",
    blue: "#3498db",
    textMain: "#f0ede6",
    textSecondary: "#a8a59e",
    textDim: "#6d6b66",
  },
  light: {
    base: "#f6f4ee",
    void: "#f6f4ee",
    surface: "rgba(255, 255, 255, 0.78)",
    card: "rgba(255, 255, 255, 0.65)",
    cardAlt: "rgba(246, 244, 238, 0.55)",
    cardHover: "rgba(255, 255, 255, 0.90)",
    borderSubtle: "rgba(0, 0, 0, 0.10)",
    borderAccent: "rgba(0, 0, 0, 0.16)",
    borderGold: "rgba(160, 120, 30, 0.38)",
    gold: "#967420",
    goldBright: "#7c5c16",
    textGold: "#7c5c16",
    goldGlow: "rgba(160, 120, 30, 0.15)",
    goldGradient: "linear-gradient(135deg, #967420 0%, #7c5c16 50%, #5d440c 100%)",
    crimson: "#942020",
    crimsonBright: "#ba2828",
    emerald: "#196f3d",
    emeraldBright: "#1e824c",
    amber: "#b7791f",
    orange: "#b95c0c",
    cyan: "#167a73",
    blue: "#1f618d",
    navy: "#0b3a6e",
    textMain: "#14171f",
    textSecondary: "#575d6e",
    textDim: "#8b92a2",
  },
};

const fonts = {
  serif: "'Playfair Display', Georgia, 'Times New Roman', serif",
  body: "'Source Serif 4', Georgia, serif",
  sans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  mono: "'JetBrains Mono', 'SF Mono', Consolas, monospace",
};

// Variantes de color del logo (DESIGN.md §2.4)
const logoVariants = [
  { id: "primary-dark", label: "Principal", bg: "dark", coin: "#c9a84c", wings: "#f0ede6", name: "#f0ede6", star: true },
  { id: "primary-light", label: "Principal", bg: "light", coin: "#967420", wings: "#575d6e", name: "#14171f", star: true },
  { id: "white-dark", label: "Marfil, una tinta", bg: "dark", coin: "#f0ede6", wings: "#f0ede6", name: "#f0ede6" },
  { id: "dark-light", label: "Tinta, una tinta", bg: "light", coin: "#14171f", wings: "#14171f", name: "#14171f" },
  { id: "gold-dark", label: "Oro, una tinta", bg: "dark", coin: "#c9a84c", wings: "#c9a84c", name: "#c9a84c" },
  { id: "gold-light", label: "Oro, una tinta", bg: "light", coin: "#967420", wings: "#967420", name: "#967420" },
];

const LOGO_DIR = "../assets/brand/logos";
const ILLUSTRATION = "../assets/auditor/img/logo-auditavision.svg";

// Trazos tomados tal cual de assets/brand/logos/ (no redibujar)
const PATHS = {
  FACE_CUTS:
    "M24.9 34.5A2.1 2.1 0 1 0 29.1 34.5A2.1 2.1 0 1 0 24.9 34.5ZM35 34.5A2 2 0 1 0 39 34.5A2 2 0 1 0 35 34.5ZM39.66 39.1L43.66 43.3A1.3 1.3 0 0 0 45.54 41.5L41.54 37.3A1.3 1.3 0 0 0 39.66 39.1ZM32 38.75C34.04 37.56 36.76 37.73 38.12 39.18C39.23 40.45 39.39 42.92 38.97 45.21C38.72 46.4 37.1 46.48 36.93 45.21C36.76 43.51 35.83 42.15 34.38 41.73C33.36 41.47 32.51 41.73 32 42.15C31.49 41.73 30.64 41.47 29.62 41.73C28.18 42.15 27.24 43.51 27.07 45.21C26.9 46.48 25.29 46.4 25.03 45.21C24.61 42.92 24.77 40.45 25.88 39.18C27.24 37.73 29.96 37.56 32 38.75Z",
  LENS_RING:
    "M31.8 34.5A5.2 5.2 0 1 0 42.2 34.5A5.2 5.2 0 1 0 31.8 34.5ZM33.6 34.5A3.4 3.4 0 1 0 40.4 34.5A3.4 3.4 0 1 0 33.6 34.5Z",
  WING_GAP:
    "M16.1 36A15.9 15.9 0 1 0 47.9 36A15.9 15.9 0 1 0 16.1 36Z",
  WINGS:
    "M23.62 31.68L10.9 11.32A2.5 2.5 0 0 0 6.66 13.97L19.38 34.32A2.5 2.5 0 0 0 23.62 31.68ZM23.11 31.08L4.72 15.66A2.5 2.5 0 0 0 1.51 19.49L19.89 34.92A2.5 2.5 0 0 0 23.11 31.08ZM22.44 30.68L2.97 22.82A2.5 2.5 0 0 0 1.09 27.45L20.56 35.32A2.5 2.5 0 0 0 22.44 30.68ZM21.67 30.51L4.72 29.32A2.5 2.5 0 0 0 4.37 34.31L21.33 35.49A2.5 2.5 0 0 0 21.67 30.51ZM20.9 30.57L9.25 33.48A2.5 2.5 0 0 0 10.46 38.33L22.1 35.43A2.5 2.5 0 0 0 20.9 30.57ZM44.62 34.32L57.34 13.97A2.5 2.5 0 0 0 53.1 11.32L40.38 31.68A2.5 2.5 0 0 0 44.62 34.32ZM44.11 34.92L62.49 19.49A2.5 2.5 0 0 0 59.28 15.66L40.89 31.08A2.5 2.5 0 0 0 44.11 34.92ZM43.44 35.32L62.91 27.45A2.5 2.5 0 0 0 61.03 22.82L41.56 30.68A2.5 2.5 0 0 0 43.44 35.32ZM42.67 35.49L59.63 34.31A2.5 2.5 0 0 0 59.28 29.32L42.33 30.51A2.5 2.5 0 0 0 42.67 35.49ZM41.9 35.43L53.54 38.33A2.5 2.5 0 0 0 54.75 33.48L43.1 30.57A2.5 2.5 0 0 0 41.9 35.43Z",
  COIN:
    "M17.5 36A14.5 14.5 0 1 0 46.5 36A14.5 14.5 0 1 0 17.5 36Z",
  HAT:
    "M24 20.7C23.4 11.9 40.6 11.9 40 20.7C36 21.7 28 21.7 24 20.7ZM19.5 22.2L44.5 22.2A1.3 1.3 0 0 0 44.5 19.6L19.5 19.6A1.3 1.3 0 0 0 19.5 22.2Z",
  WORDMARK:
    "M15.92 14.96 25.6 39.92Q26.16 41.28 26.8 41.86Q27.44 42.44 27.96 42.48V43.28Q26.52 43.2 24.6 43.18Q22.68 43.16 20.68 43.16Q18.64 43.16 16.84 43.18Q15.04 43.2 13.96 43.28V42.48Q16 42.4 16.54 41.78Q17.08 41.16 16.28 39.12L9.88 21.4L10.68 20L5.16 34.36Q4.16 36.96 3.94 38.54Q3.72 40.12 4.12 40.96Q4.52 41.8 5.4 42.12Q6.28 42.44 7.48 42.48V43.28Q6 43.2 4.82 43.18Q3.64 43.16 2.24 43.16Q1.48 43.16 0.62 43.18Q-0.24 43.2 -0.84 43.28V42.48Q0.08 42.32 0.98 41.3Q1.88 40.28 2.84 37.8L11.72 14.96Q12.68 15.04 13.82 15.04Q14.96 15.04 15.92 14.96ZM17.32 31.76V32.56H5.4L5.8 31.76ZM49.6 22.08V38.92Q49.6 40.72 50.1 41.58Q50.6 42.44 51.84 42.44V43.28Q50.6 43.16 49.36 43.16Q47.36 43.16 45.64 43.28Q43.92 43.4 42.4 43.72V40.84Q41.44 42.44 39.82 43.14Q38.2 43.84 36.04 43.84Q34.2 43.84 33.14 43.38Q32.08 42.92 31.52 42.24Q30.92 41.52 30.64 40.32Q30.36 39.12 30.36 37.08V26.88Q30.36 25.08 29.88 24.22Q29.4 23.36 28.12 23.36V22.52Q29.4 22.64 30.6 22.64Q32.6 22.64 34.34 22.5Q36.08 22.36 37.56 22.08V39.24Q37.56 40.08 37.76 40.64Q37.96 41.2 38.4 41.48Q38.84 41.76 39.52 41.76Q40.28 41.76 40.92 41.4Q41.56 41.04 41.98 40.38Q42.4 39.72 42.4 38.88V26.88Q42.4 25.08 41.92 24.22Q41.44 23.36 40.16 23.36V22.52Q41.44 22.64 42.64 22.64Q44.64 22.64 46.38 22.5Q48.12 22.36 49.6 22.08ZM74.04 12V38.88Q74.04 40.68 74.54 41.54Q75.04 42.4 76.28 42.4V43.24Q75.04 43.12 73.8 43.12Q71.8 43.12 70.08 43.24Q68.36 43.36 66.84 43.68V16.8Q66.84 15 66.36 14.14Q65.88 13.28 64.6 13.28V12.44Q65.88 12.56 67.08 12.56Q69.08 12.56 70.82 12.42Q72.56 12.28 74.04 12ZM62.68 21.96Q64.44 21.96 65.64 22.38Q66.84 22.8 67.76 23.72L67.32 24.16Q66.8 23.72 66.16 23.5Q65.52 23.28 64.96 23.28Q63.12 23.28 62.2 25.64Q61.28 28 61.28 32.88Q61.28 36.4 61.64 38.34Q62 40.28 62.62 41.02Q63.24 41.76 63.96 41.76Q65.08 41.76 65.96 40.94Q66.84 40.12 66.84 38.88V40.84Q66.04 42.36 64.88 43.1Q63.72 43.84 61.96 43.84Q59.68 43.84 57.82 42.7Q55.96 41.56 54.88 39.12Q53.8 36.68 53.8 32.76Q53.8 29.12 54.9 26.74Q56 24.36 58 23.16Q60 21.96 62.68 21.96ZM83.36 12Q85.44 12 86.58 12.86Q87.72 13.72 87.72 15.44Q87.72 17.16 86.58 18.02Q85.44 18.88 83.36 18.88Q81.28 18.88 80.14 18.02Q79 17.16 79 15.44Q79 13.72 80.14 12.86Q81.28 12 83.36 12ZM87.2 22.08V39.56Q87.2 41.24 87.7 41.84Q88.2 42.44 89.44 42.44V43.28Q88.64 43.24 87.04 43.18Q85.44 43.12 83.76 43.12Q82.08 43.12 80.36 43.18Q78.64 43.24 77.76 43.28V42.44Q79 42.44 79.5 41.84Q80 41.24 80 39.56V26.88Q80 25.08 79.52 24.22Q79.04 23.36 77.76 23.36V22.52Q79.04 22.64 80.24 22.64Q82.24 22.64 83.98 22.5Q85.72 22.36 87.2 22.08ZM100.2 16.04V22.52H104.12V23.32H100.2V39.92Q100.2 40.68 100.48 41.02Q100.76 41.36 101.4 41.36Q101.84 41.36 102.44 41.1Q103.04 40.84 103.56 40.2L104.16 40.68Q103.32 42.12 101.94 42.98Q100.56 43.84 98.48 43.84Q97.16 43.84 96.1 43.5Q95.04 43.16 94.36 42.48Q93.48 41.6 93.24 40.3Q93 39 93 36.92V23.32H89.96V22.52H93V17.8Q95.12 17.8 96.86 17.38Q98.6 16.96 100.2 16.04ZM110.36 43.56Q108.48 43.56 107.28 42.84Q106.08 42.12 105.54 40.96Q105 39.8 105 38.52Q105 36.84 105.76 35.78Q106.52 34.72 107.74 34.06Q108.96 33.4 110.32 32.96Q111.68 32.52 112.9 32.1Q114.12 31.68 114.88 31.1Q115.64 30.52 115.64 29.6V26.04Q115.64 25.4 115.42 24.64Q115.2 23.88 114.6 23.32Q114 22.76 112.8 22.76Q112.16 22.76 111.58 22.94Q111 23.12 110.56 23.44Q111.96 23.96 112.6 24.9Q113.24 25.84 113.24 26.96Q113.24 28.56 112.12 29.48Q111 30.4 109.48 30.4Q107.88 30.4 107 29.4Q106.12 28.4 106.12 26.92Q106.12 25.68 106.74 24.82Q107.36 23.96 108.6 23.24Q109.8 22.56 111.48 22.26Q113.16 21.96 115 21.96Q116.96 21.96 118.64 22.34Q120.32 22.72 121.52 23.96Q122.36 24.84 122.6 26.16Q122.84 27.48 122.84 29.56V40.28Q122.84 41.28 122.98 41.64Q123.12 42 123.48 42Q123.8 42 124.1 41.8Q124.4 41.6 124.68 41.4L125.08 42.08Q124.2 42.84 122.9 43.2Q121.6 43.56 120.16 43.56Q118.44 43.56 117.5 43.14Q116.56 42.72 116.18 42.02Q115.8 41.32 115.76 40.52Q114.92 41.84 113.66 42.7Q112.4 43.56 110.36 43.56ZM114.16 40.36Q114.6 40.36 114.94 40.22Q115.28 40.08 115.64 39.68V31.24Q115.36 31.76 114.9 32.26Q114.44 32.76 113.96 33.28Q113.48 33.8 113.06 34.4Q112.64 35 112.38 35.78Q112.12 36.56 112.12 37.6Q112.12 39.12 112.7 39.74Q113.28 40.36 114.16 40.36ZM146.2 22.52V23.36Q145.44 23.64 144.74 24.46Q144.04 25.28 143.36 27.24L137.96 43.28Q137 43.2 136.02 43.2Q135.04 43.2 134.08 43.28L127.12 25.6Q126.52 24.08 125.88 23.72Q125.24 23.36 124.8 23.36V22.52Q126.4 22.64 128.12 22.7Q129.84 22.76 131.92 22.76Q133.16 22.76 134.54 22.68Q135.92 22.6 137.12 22.52V23.36Q136.4 23.36 135.82 23.42Q135.24 23.48 134.98 23.78Q134.72 24.08 134.88 24.88L139.36 37.36L138.84 38.16L141.08 31.48Q142 28.76 141.86 27Q141.72 25.24 140.92 24.34Q140.12 23.44 138.92 23.36V22.52Q139.48 22.56 140.28 22.6Q141.08 22.64 141.86 22.66Q142.64 22.68 143.12 22.68Q143.84 22.68 144.8 22.64Q145.76 22.6 146.2 22.52ZM152.6 12Q154.68 12 155.82 12.86Q156.96 13.72 156.96 15.44Q156.96 17.16 155.82 18.02Q154.68 18.88 152.6 18.88Q150.52 18.88 149.38 18.02Q148.24 17.16 148.24 15.44Q148.24 13.72 149.38 12.86Q150.52 12 152.6 12ZM156.44 22.08V39.56Q156.44 41.24 156.94 41.84Q157.44 42.44 158.68 42.44V43.28Q157.88 43.24 156.28 43.18Q154.68 43.12 153 43.12Q151.32 43.12 149.6 43.18Q147.88 43.24 147 43.28V42.44Q148.24 42.44 148.74 41.84Q149.24 41.24 149.24 39.56V26.88Q149.24 25.08 148.76 24.22Q148.28 23.36 147 23.36V22.52Q148.28 22.64 149.48 22.64Q151.48 22.64 153.22 22.5Q154.96 22.36 156.44 22.08ZM168.6 21.96Q170.36 21.96 171.7 22.34Q173.04 22.72 173.64 23.04Q175.04 23.88 175.36 22H176.16Q176.08 23.16 176.04 24.82Q176 26.48 176 29.2H175.2Q175.04 27.72 174.5 26.28Q173.96 24.84 172.94 23.88Q171.92 22.92 170.28 22.92Q169.28 22.92 168.6 23.52Q167.92 24.12 167.92 25.16Q167.92 26.36 168.64 27.3Q169.36 28.24 170.48 29.1Q171.6 29.96 172.72 30.92Q173.96 31.92 174.92 32.88Q175.88 33.84 176.46 34.98Q177.04 36.12 177.04 37.68Q177.04 39.48 175.94 40.88Q174.84 42.28 173.02 43.06Q171.2 43.84 168.96 43.84Q167.56 43.84 166.52 43.54Q165.48 43.24 164.84 42.84Q164.2 42.52 163.74 42.34Q163.28 42.16 162.84 42.16Q162.44 42.16 162.16 42.58Q161.88 43 161.72 43.56H160.92Q161 42.28 161.04 40.44Q161.08 38.6 161.08 35.56H161.88Q162.12 37.68 162.82 39.32Q163.52 40.96 164.62 41.9Q165.72 42.84 167.16 42.84Q167.8 42.84 168.32 42.6Q168.84 42.36 169.16 41.88Q169.48 41.4 169.48 40.64Q169.48 38.88 168.42 37.68Q167.36 36.48 165.76 35.04Q164.56 33.92 163.5 32.86Q162.44 31.8 161.76 30.54Q161.08 29.28 161.08 27.72Q161.08 25.92 162.14 24.64Q163.2 23.36 164.92 22.66Q166.64 21.96 168.6 21.96ZM184.68 12Q186.76 12 187.9 12.86Q189.04 13.72 189.04 15.44Q189.04 17.16 187.9 18.02Q186.76 18.88 184.68 18.88Q182.6 18.88 181.46 18.02Q180.32 17.16 180.32 15.44Q180.32 13.72 181.46 12.86Q182.6 12 184.68 12ZM188.52 22.08V39.56Q188.52 41.24 189.02 41.84Q189.52 42.44 190.76 42.44V43.28Q189.96 43.24 188.36 43.18Q186.76 43.12 185.08 43.12Q183.4 43.12 181.68 43.18Q179.96 43.24 179.08 43.28V42.44Q180.32 42.44 180.82 41.84Q181.32 41.24 181.32 39.56V26.88Q181.32 25.08 180.84 24.22Q180.36 23.36 179.08 23.36V22.52Q180.36 22.64 181.56 22.64Q183.56 22.64 185.3 22.5Q187.04 22.36 188.52 22.08ZM202.96 21.96Q206.08 21.96 208.38 23.02Q210.68 24.08 211.96 26.48Q213.24 28.88 213.24 32.92Q213.24 36.96 211.96 39.36Q210.68 41.76 208.38 42.8Q206.08 43.84 202.96 43.84Q199.88 43.84 197.56 42.8Q195.24 41.76 193.96 39.36Q192.68 36.96 192.68 32.92Q192.68 28.88 193.96 26.48Q195.24 24.08 197.56 23.02Q199.88 21.96 202.96 21.96ZM202.96 22.76Q201.76 22.76 200.96 25.16Q200.16 27.56 200.16 32.92Q200.16 38.28 200.96 40.66Q201.76 43.04 202.96 43.04Q204.16 43.04 204.96 40.66Q205.76 38.28 205.76 32.92Q205.76 27.56 204.96 25.16Q204.16 22.76 202.96 22.76ZM207.4 10.48Q208.2 11.12 208.22 12.2Q208.24 13.28 207.56 14.12Q206.92 14.92 205.98 15.5Q205.04 16.08 203.72 16.9Q202.4 17.72 200.52 19.32L200.08 18.96Q201.24 16.68 201.68 15.18Q202.12 13.68 202.44 12.64Q202.76 11.6 203.48 10.8Q204.12 10.04 205.3 9.86Q206.48 9.68 207.4 10.48ZM231.12 21.96Q232.96 21.96 234.02 22.42Q235.08 22.88 235.64 23.56Q236.24 24.28 236.52 25.48Q236.8 26.68 236.8 28.72V39.56Q236.8 41.24 237.3 41.84Q237.8 42.44 239.04 42.44V43.28Q238.24 43.24 236.62 43.18Q235 43.12 233.44 43.12Q231.76 43.12 230.16 43.18Q228.56 43.24 227.76 43.28V42.44Q228.8 42.44 229.2 41.84Q229.6 41.24 229.6 39.56V26.56Q229.6 25.72 229.4 25.16Q229.2 24.6 228.78 24.32Q228.36 24.04 227.64 24.04Q226.92 24.04 226.26 24.4Q225.6 24.76 225.18 25.42Q224.76 26.08 224.76 26.92V39.56Q224.76 41.24 225.18 41.84Q225.6 42.44 226.6 42.44V43.28Q225.84 43.24 224.36 43.18Q222.88 43.12 221.32 43.12Q219.64 43.12 217.92 43.18Q216.2 43.24 215.32 43.28V42.44Q216.56 42.44 217.06 41.84Q217.56 41.24 217.56 39.56V26.88Q217.56 25.08 217.08 24.22Q216.6 23.36 215.32 23.36V22.52Q216.6 22.64 217.8 22.64Q219.8 22.64 221.54 22.5Q223.28 22.36 224.76 22.08V24.96Q225.72 23.36 227.34 22.66Q228.96 21.96 231.12 21.96Z",
};

// 2. Logo: símbolo, nombre y combinado, con los trazos de los SVG oficiales
let uidCounter = 0;
const useUid = () => useState(() => `av${++uidCounter}`)[0];

const SymbolArt = ({ uid, coin, wings }) => (
  <>
    <defs>
      <mask id={`${uid}-m`} maskUnits="userSpaceOnUse" x="0" y="0" width="64" height="64">
        <rect width="64" height="64" fill="#ffffff" />
        <path fill="#000000" d={PATHS.FACE_CUTS} />
        <path fill="#000000" fillRule="evenodd" d={PATHS.LENS_RING} />
      </mask>
      <mask id={`${uid}-w`} maskUnits="userSpaceOnUse" x="0" y="0" width="64" height="64">
        <rect width="64" height="64" fill="#ffffff" />
        <path fill="#000000" d={PATHS.WING_GAP} />
      </mask>
    </defs>
    <path fill={wings} mask={`url(#${uid}-w)`} d={PATHS.WINGS} />
    <path fill={coin} mask={`url(#${uid}-m)`} d={PATHS.COIN} />
    <path fill={coin} d={PATHS.HAT} />
  </>
);

const BrandSymbol = ({ size = 64, coin, wings, favicon = false }) => {
  const uid = useUid();
  return (
    <svg viewBox="0 0 64 64" width={size} height={size} role="img" aria-label="Símbolo de Auditavisión">
      {favicon && <rect width="64" height="64" rx="12" fill="#0c0e15" />}
      <SymbolArt uid={uid} coin={coin} wings={wings} />
    </svg>
  );
};

const Wordmark = ({ height = 40, fill }) => (
  <svg viewBox="0 9.83 239.48 34.01" height={height} style={{ width: "auto", maxWidth: "100%" }} role="img" aria-label="Auditavisión">
    <path fill={fill} d={PATHS.WORDMARK} />
  </svg>
);

const Combined = ({ height = 48, coin, wings, name }) => {
  const uid = useUid();
  return (
    <svg viewBox="0 -9.9 319.75 68.03" height={height} style={{ width: "auto", maxWidth: "100%" }} role="img" aria-label="Auditavisión">
      <g transform="translate(0 -9.9) scale(1.06)">
        <SymbolArt uid={uid} coin={coin} wings={wings} />
      </g>
      <path fill={name} transform="translate(80.27 0)" d={PATHS.WORDMARK} />
    </svg>
  );
};

// 3. Piezas reutilizables
const Section = ({ t, title, number, lead, children }) => (
  <section className="mb-16">
    <div className="flex items-baseline gap-3 mb-3">
      <span className="text-xs tracking-widest" style={{ fontFamily: fonts.mono, color: t.gold }}>{number}</span>
      <h2 className="text-2xl" style={{ fontFamily: fonts.serif, fontWeight: 700, color: t.textMain, lineHeight: 1.15 }}>{title}</h2>
    </div>
    {lead && (
      <p className="mb-8 text-[15px]" style={{ color: t.textSecondary, maxWidth: "76ch", lineHeight: 1.65 }}>{lead}</p>
    )}
    {!lead && <div className="mb-6" />}
    {children}
  </section>
);

const Card = ({ t, children, gold = false, className = "" }) => (
  <div
    className={`rounded-xl p-6 ${className}`}
    style={{ background: t.card, border: `1px solid ${gold ? t.borderGold : t.borderSubtle}` }}
  >
    {children}
  </div>
);

const Label = ({ t, children, color }) => (
  <span className="text-[11px] uppercase" style={{ fontFamily: fonts.mono, fontWeight: 600, letterSpacing: "0.12em", color: color || t.textSecondary }}>
    {children}
  </span>
);

const ColorSwatch = ({ t, name, hex, role, tall }) => {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    if (navigator.clipboard) navigator.clipboard.writeText(hex).then(() => { setCopied(true); setTimeout(() => setCopied(false), 1200); });
  };
  return (
    <button type="button" onClick={copy} className="flex flex-col gap-1 text-left group" title={`Copiar ${hex}`}>
      <div className={`w-full rounded-lg ${tall ? "h-24" : "h-16"} transition-transform group-hover:-translate-y-0.5`}
        style={{ background: hex, border: `1px solid ${t.borderAccent}` }} />
      <span className="text-xs" style={{ fontFamily: fonts.mono, color: copied ? t.emeraldBright : t.textSecondary }}>
        {copied ? "copiado" : hex}
      </span>
      <span className="text-xs" style={{ fontFamily: fonts.mono, color: t.textMain }}>{name}</span>
      {role && <span className="text-xs" style={{ fontFamily: fonts.sans, color: t.textSecondary }}>{role}</span>}
    </button>
  );
};

const Chip = ({ t, estado }) => {
  const map = {
    oficial: { c: t.emeraldBright, b: "solid" },
    derivado: { c: t.amber, b: "solid" },
    pendiente: { c: t.textSecondary, b: "dashed" },
    contexto: { c: t.cyan, b: "solid" },
  };
  const s = map[estado];
  return (
    <span className="inline-block rounded px-2 py-0.5" style={{
      fontFamily: fonts.mono, fontSize: "9.5px", fontWeight: 500, letterSpacing: "0.07em",
      textTransform: "uppercase", color: s.c, border: `1px ${s.b} ${s.c}`,
    }}>{estado}</span>
  );
};

const DoDont = ({ t, ok, children }) => (
  <div className="rounded-lg p-4 text-sm" style={{
    background: t.cardAlt, border: `1px solid ${t.borderSubtle}`,
    borderLeft: `3px solid ${ok ? t.emeraldBright : t.crimsonBright}`, color: t.textMain, fontFamily: fonts.sans,
  }}>
    <div className="mb-1"><Label t={t} color={ok ? t.emeraldBright : t.crimsonBright}>{ok ? "Sí" : "No"}</Label></div>
    {children}
  </div>
);

const LogoTile = ({ t, bg, children, caption, file }) => {
  const bgHex = bg === "dark" ? colors.dark.base : colors.light.base;
  const fg = bg === "dark" ? colors.dark.textSecondary : colors.light.textSecondary;
  return (
    <div className="rounded-xl overflow-hidden" style={{ border: `1px solid ${t.borderSubtle}` }}>
      <div className="p-10 flex items-center justify-center min-h-[150px]" style={{ background: bgHex }}>{children}</div>
      {(caption || file) && (
        <div className="px-4 py-2 flex items-center justify-between gap-2 text-xs" style={{ background: bgHex, borderTop: `1px solid ${bg === "dark" ? colors.dark.borderSubtle : colors.light.borderSubtle}` }}>
          <span style={{ fontFamily: fonts.mono, color: fg }}>{caption}</span>
          {file && (
            <a href={`${LOGO_DIR}/${file}`} download style={{ fontFamily: fonts.mono, color: bg === "dark" ? colors.dark.gold : colors.light.gold }}>SVG ↓</a>
          )}
        </div>
      )}
    </div>
  );
};

const Table = ({ t, head, rows }) => (
  <div className="overflow-x-auto rounded-xl" style={{ border: `1px solid ${t.borderSubtle}` }}>
    <table className="w-full text-sm" style={{ fontFamily: fonts.sans, borderCollapse: "collapse" }}>
      {head.some(Boolean) && <thead>
        <tr style={{ background: t.cardAlt }}>
          {head.map((h) => (
            <th key={h} className="text-left px-4 py-3"><Label t={t}>{h}</Label></th>
          ))}
        </tr>
      </thead>}
      <tbody>
        {rows.map((r, i) => (
          <tr key={i} style={{ borderTop: `1px solid ${t.borderSubtle}`, background: t.card }}>
            {r.map((c, j) => (
              <td key={j} className="px-4 py-3 align-top" style={{ color: j === 0 ? t.textMain : t.textSecondary }}>{c}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// 4. Contenido de las pestañas (textos de DESIGN.md)
const TabEsencia = ({ t }) => (
  <>
    <Section t={t} number="01" title="Esencia">
      <div className="mb-10">
        <Label t={t} color={t.gold}>Lema</Label>
        <p className="mt-3 text-4xl md:text-5xl italic" style={{ fontFamily: fonts.serif, color: t.textMain, lineHeight: 1.1 }}>
          El gasto público, a la vista.
        </p>
      </div>
      <Table t={t} head={["", ""]} rows={[
        ["Nombre", "Auditavisión, con acento en la o. Nunca «AuditaVision», «Auditavision» ni «AUDITAVISION» en texto corrido."],
        ["Descriptor", "Sistema cívico de fiscalización y geopolítica del gasto público en México"],
        ["Qué hace", "Sigue el dinero público federal, estatal y municipal con documentos oficiales, y lo explica para que cualquier persona lo pueda revisar."],
        ["Para quién", "Ciudadanía general: personas sin formación técnica que quieren saber a dónde va su dinero."],
        ["Qué no es", "No es un sitio oficial. No es del gobierno ni habla en nombre de ninguna institución, aunque cite sus documentos."],
        ["Tono", "Riguroso, cívico, sobrio, didáctico."],
      ]} />
    </Section>

    <Section t={t} number="02" title="Personalidad">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          ["Riguroso", "Toda cifra se rastrea a su documento y lleva su estado (oficial, derivado, pendiente). Lo que no se puede sostener se dice."],
          ["Cívico", "Le habla a una persona que tiene derecho a saber, no a un especialista ni a un cliente."],
          ["Sobrio", "Ni alarma ni celebración: el dato serio basta. Nada de cifras infladas para llamar la atención."],
          ["Didáctico", "Se explica, no se simplifica. Cada término técnico lleva su glosario o su referencia."],
        ].map(([k, v]) => (
          <Card t={t} key={k}>
            <h3 className="text-lg mb-2" style={{ fontFamily: fonts.serif, fontWeight: 700, color: t.textGold }}>{k}</h3>
            <p className="text-[15px]" style={{ color: t.textSecondary, lineHeight: 1.65 }}>{v}</p>
          </Card>
        ))}
      </div>
    </Section>

    <Section t={t} number="03" title="La idea de la marca">
      <Card t={t} gold className="flex flex-col md:flex-row items-center gap-8">
        <img src={ILLUSTRATION} alt="La moneda inspectora de Auditavisión" style={{ height: 120, width: "auto" }} />
        <p className="text-[15px]" style={{ color: t.textMain, lineHeight: 1.65, maxWidth: "62ch" }}>
          La moneda de oro con alas es <strong>el peso público que sale a vigilar a dónde va</strong>. Lleva bombín y
          lupa porque es un inspector, y alas porque el dinero público vuela: se va a obras, a sueldos y a deudas que
          nadie ve. El lema lo resume: <em>el gasto público, a la vista</em>.
        </p>
      </Card>
    </Section>
  </>
);

const TabLogo = ({ t }) => (
  <>
    <Section t={t} number="01" title="La ilustración: la moneda inspectora"
      lead="Para lo grande: encabezado, «Quiénes somos», portadas y presentaciones. Tamaño mínimo 56 px de alto. No se redibuja ni se recolorea.">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <LogoTile t={t} bg="dark" caption="logo-auditavision.svg · oscuro"><img src={ILLUSTRATION} alt="" style={{ height: 110 }} /></LogoTile>
        <LogoTile t={t} bg="light" caption="logo-auditavision.svg · claro"><img src={ILLUSTRATION} alt="" style={{ height: 110 }} /></LogoTile>
      </div>
    </Section>

    <Section t={t} number="02" title="Combinado"
      lead="El símbolo plano a la izquierda y el nombre en Playfair Display Black a la derecha. Ancho mínimo 140 px; por debajo, el símbolo solo.">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {logoVariants.map((v) => (
          <LogoTile key={v.id} t={t} bg={v.bg} caption={`${v.id}${v.star ? " ★" : ""}`} file={`combined/auditavision-combined-${v.id}.svg`}>
            <Combined height={52} coin={v.coin} wings={v.wings} name={v.name} />
          </LogoTile>
        ))}
      </div>
    </Section>

    <Section t={t} number="03" title="Símbolo plano: la moneda con rostro"
      lead="Rellenos planos; los grabados son recortes transparentes, así que funciona a una tinta y sobre cualquier fondo. Para favicon, sellos, marcas de agua y todo lo menor de 56 px.">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {logoVariants.map((v) => (
          <LogoTile key={v.id} t={t} bg={v.bg} caption={v.id} file={`symbol/auditavision-symbol-${v.id}.svg`}>
            <BrandSymbol size={84} coin={v.coin} wings={v.wings} />
          </LogoTile>
        ))}
      </div>
      <div className="mt-6">
        <Card t={t} className="flex flex-wrap items-end gap-6">
          {[64, 32, 16].map((s) => (
            <div key={s} className="flex flex-col items-center gap-2">
              <BrandSymbol size={s} coin="#c9a84c" wings="#f0ede6" favicon />
              <span className="text-xs" style={{ fontFamily: fonts.mono, color: t.textSecondary }}>{s} px</span>
            </div>
          ))}
          <p className="text-sm flex-1 min-w-[220px]" style={{ color: t.textSecondary, fontFamily: fonts.sans }}>
            Favicon: cuadro <code style={{ fontFamily: fonts.mono }}>#0c0e15</code> con radio 12. A 16 px el rostro se reduce
            a dos puntos y el bigote estilo Zapata, pero la silueta alada se sigue leyendo.{" "}
            <a href={`${LOGO_DIR}/symbol/auditavision-favicon.svg`} download style={{ color: t.gold, fontFamily: fonts.mono }}>SVG ↓</a>
          </p>
        </Card>
      </div>
    </Section>

    <Section t={t} number="04" title="Nombre">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {logoVariants.map((v) => (
          <LogoTile key={v.id} t={t} bg={v.bg} caption={v.id} file={`wordmark/auditavision-wordmark-${v.id}.svg`}>
            <Wordmark height={44} fill={v.name} />
          </LogoTile>
        ))}
      </div>
    </Section>

    <Section t={t} number="05" title="Espacio, tamaño y color"
      lead="Alrededor de cualquier versión, un margen igual al radio de la moneda: nada entra ahí. El logo no introduce colores nuevos: usa --gold, --text-main y --text-secondary de cada tema.">
      <Table t={t} head={["Pieza", "Mínimo", "Usa"]} rows={[
        ["Ilustración", "56 px de alto", "Encabezado, portadas, presentaciones"],
        ["Combinado", "140 px de ancho", "Cabeceras, firmas, documentos"],
        ["Símbolo plano", "16 px", "Favicon, ícono de app, sellos, impresión a una tinta"],
      ]} />
    </Section>

    <Section t={t} number="06" title="Qué no hacer con el logo">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {[
          "No lo rotes, estires, inclines ni recortes.",
          "No le pongas sombras, brillos, contornos ni degradados.",
          "No cambies sus colores fuera de las seis variantes.",
          "No lo pongas sobre la fotografía de la ciudad sin una superficie detrás.",
          "No uses la ilustración a menos de 56 px ni el combinado a menos de 140 px.",
          "No reescribas el nombre con otra letra, en mayúsculas o sin acento.",
          "No lo acompañes de escudos, banderas ni emblemas oficiales.",
        ].map((x) => <DoDont key={x} t={t}>{x}</DoDont>)}
      </div>
    </Section>
  </>
);

const TabColor = ({ t, theme }) => {
  const c = colors[theme];
  return (
    <>
      <Section t={t} number="01" title="Marca: oro"
        lead={`Valores del tema ${theme === "dark" ? "oscuro" : "claro"}. Cambia de tema arriba para ver el otro. Clic en una muestra para copiar su valor.`}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ColorSwatch t={t} tall name="--gold ★" hex={c.gold} role="Logo, títulos de sección, controles activos" />
          <ColorSwatch t={t} tall name="--gold-bright" hex={c.goldBright} role="Énfasis y anillo de foco" />
          <ColorSwatch t={t} tall name="--text-gold" hex={c.textGold} role="Texto dorado sobre superficie" />
          <div className="flex flex-col gap-1">
            <div className="w-full h-24 rounded-lg" style={{ background: c.goldGradient }} />
            <span className="text-xs" style={{ fontFamily: fonts.mono, color: t.textMain }}>--gold-gradient</span>
            <span className="text-xs" style={{ fontFamily: fonts.sans, color: t.textSecondary }}>Solo el título del encabezado (135°)</span>
          </div>
        </div>
      </Section>

      <Section t={t} number="02" title="Un acento, un papel"
        lead="Los siete acentos se conservan (decisión del autor, 29-09-2026). Lo que fija la guía es para qué sirve cada uno.">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <ColorSwatch t={t} name="--crimson-bright" hex={c.crimsonBright} role="Alerta: irregularidad, monto observado" />
          <ColorSwatch t={t} name="--emerald-bright" hex={c.emeraldBright} role="Oficial y verificado" />
          <ColorSwatch t={t} name="--amber" hex={c.amber} role="Derivado: cálculo propio" />
          <ColorSwatch t={t} name="--orange" hex={c.orange} role="Advertencia: riesgo medio" />
          <ColorSwatch t={t} name="--cyan" hex={c.cyan} role="Referencia y contexto" />
          <ColorSwatch t={t} name="--blue" hex={c.blue} role="Información neutra" />
          <ColorSwatch t={t} name="--crimson" hex={c.crimson} role="Alerta, tono base" />
          <ColorSwatch t={t} name="--emerald" hex={c.emerald} role="Oficial, tono base" />
          {theme === "light" && <ColorSwatch t={t} name="--navy" hex={c.navy} role="Solo tema claro: títulos, botones, enlaces" />}
        </div>
      </Section>

      <Section t={t} number="03" title="Neutros y superficies"
        lead="Las superficies son translúcidas: en el sitio se ven sobre la fotografía de la ciudad y un ruido de papel al 2.5 %.">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ColorSwatch t={t} name="--text-main" hex={c.textMain} role="Texto" />
          <ColorSwatch t={t} name="--text-secondary" hex={c.textSecondary} role="Bajadas y pies" />
          <ColorSwatch t={t} name="--text-dim" hex={c.textDim} role="Atenuado; nunca cifras" />
          <ColorSwatch t={t} name="Fondo sólido" hex={c.base} role="Logo, favicon, piezas fuera del sitio" />
          <ColorSwatch t={t} name="--bg-surface" hex={c.surface} role="Barras y paneles" />
          <ColorSwatch t={t} name="--bg-card" hex={c.card} role="Tarjetas" />
          <ColorSwatch t={t} name="--bg-card-alt" hex={c.cardAlt} role="Tarjeta alterna" />
          <ColorSwatch t={t} name="--bg-card-hover" hex={c.cardHover} role="Tarjeta al pasar el cursor" />
        </div>
      </Section>

      <Section t={t} number="04" title="Proporción"
        lead="Aproximada, en una pantalla típica del auditor. Si un bloque se ve «de colores», sobran acentos.">
        <div className="flex h-12 rounded-lg overflow-hidden" style={{ border: `1px solid ${t.borderSubtle}` }}>
          {[[70, c.cardHover, "Superficies y fotografía 70 %"], [20, c.textSecondary, "Texto 20 %"], [7, c.gold, "Oro 7 %"], [3, c.crimsonBright, "3 %"]].map(([w, bg, l]) => (
            <div key={l} style={{ width: `${w}%`, background: bg }} title={l} />
          ))}
        </div>
        <div className="flex flex-wrap gap-x-6 gap-y-1 mt-3 text-xs" style={{ fontFamily: fonts.mono, color: t.textSecondary }}>
          <span>Superficies y fotografía 70 %</span><span>Texto 20 %</span><span>Oro 7 %</span><span>Acentos de estado 3 %</span>
        </div>
      </Section>

      <Section t={t} number="05" title="Reglas de color">
        <ol className="space-y-3 text-[15px] list-decimal pl-5" style={{ color: t.textMain, lineHeight: 1.65 }}>
          <li>Un acento, un papel. El carmesí nunca marca algo positivo ni el esmeralda algo sin documento.</li>
          <li>El color nunca va solo: todo estado lleva también texto o forma.</li>
          <li>En componentes, usa siempre la variable, nunca el hexadecimal.</li>
          <li>Texto de cifras en --text-main o --text-secondary, nunca en --text-dim.</li>
          <li>El degradado dorado se reserva al título del encabezado.</li>
          <li>No agregues colores nuevos sin decidirlo con el autor y anotarlo en DESIGN.md.</li>
        </ol>
      </Section>
    </>
  );
};

const typeScale = [
  { size: "clamp(28px, 3.2vw, 36px)", px: 36, name: "Marca", fam: "serif", w: 900, use: "Título del encabezado (vigente)", sample: "Auditavisión", gradient: true },
  { size: "28px", px: 28, name: "Título 1", fam: "serif", w: 700, use: "Título de pestaña", sample: "Presupuesto de Egresos" },
  { size: "22px", px: 22, name: "Título 2", fam: "serif", w: 700, use: "Título de subpestaña o módulo", sample: "Del peso federal al peso local" },
  { size: "18px", px: 18, name: "Título 3", fam: "serif", w: 700, use: "Título de tarjeta", sample: "Gasto federalizado" },
  { size: "15px", px: 15, name: "Texto", fam: "body", w: 400, use: "Texto corrido, interlineado 1.65", sample: "Toda cifra se rastrea a su documento y lleva su estado." },
  { size: "13px", px: 13, name: "Texto chico", fam: "sans", w: 500, use: "Bajadas, pies de gráfica, controles", sample: "Fuente: documento oficial, página y fecha." },
  { size: "11px", px: 11, name: "Etiqueta", fam: "mono", w: 600, use: "Eyebrows y rótulos, espaciado 0.12em", sample: "SISTEMA CÍVICO DE FISCALIZACIÓN", ls: "0.12em" },
  { size: "9.5px", px: 9.5, name: "Chip", fam: "mono", w: 500, use: "Chips de estado, espaciado 0.07em", sample: "OFICIAL · DERIVADO · PENDIENTE", ls: "0.07em" },
];

const TabTipografia = ({ t }) => (
  <>
    <Section t={t} number="01" title="Cuatro familias, cuatro papeles" lead="Todas de Google Fonts.">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          ["--font-serif", "Playfair Display", fonts.serif, "400, 700, 900, itálica 400", "Títulos y nombre de la marca", 700],
          ["--font-body", "Source Serif 4", fonts.body, "400, 600, 700, itálica 400", "Texto corrido", 400],
          ["--font-sans", "Inter", fonts.sans, "400, 500, 600, 700", "Interfaz: botones, pestañas, controles", 500],
          ["--font-mono", "JetBrains Mono", fonts.mono, "400, 500, 700, 800", "Cifras, chips, [Ref. N], eyebrows", 500],
        ].map(([v, fam, ff, w, use, fw]) => (
          <Card t={t} key={v}>
            <Label t={t} color={t.gold}>{v}</Label>
            <p className="text-4xl mt-3 mb-2" style={{ fontFamily: ff, fontWeight: fw, color: t.textMain }}>{fam}</p>
            <p className="text-lg mb-3" style={{ fontFamily: ff, color: t.textSecondary }}>Aa Bb Cc Ññ Áá · 0 1 2 3 4 5 6 7 8 9</p>
            <p className="text-xs" style={{ fontFamily: fonts.mono, color: t.textSecondary }}>{w}</p>
            <p className="text-sm mt-1" style={{ fontFamily: fonts.sans, color: t.textMain }}>{use}</p>
          </Card>
        ))}
      </div>
    </Section>

    <Section t={t} number="02" title="Escala"
      lead="Propuesta de DESIGN.md §4.1: hoy el CSS usa más de veinte tamaños y se reducen a estos al migrar. Cada línea está a su tamaño real.">
      <div className="space-y-6">
        {typeScale.map((s) => (
          <div key={s.name} className="grid grid-cols-1 md:grid-cols-[220px_1fr] gap-2 md:gap-6 items-baseline pb-6" style={{ borderBottom: `1px solid ${t.borderSubtle}` }}>
            <div className="text-xs" style={{ fontFamily: fonts.mono, color: t.textSecondary }}>
              <div style={{ color: t.textMain }}>{s.name} · {s.size}</div>
              <div>{s.use}</div>
            </div>
            <p style={{
              fontFamily: fonts[s.fam], fontSize: s.size, fontWeight: s.w, letterSpacing: s.ls, lineHeight: s.fam === "serif" ? 1.15 : 1.65,
              color: t.textMain,
              ...(s.gradient ? { background: t.goldGradient, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" } : {}),
            }}>{s.sample}</p>
          </div>
        ))}
      </div>
    </Section>

    <Section t={t} number="03" title="Reglas">
      <ol className="space-y-3 text-[15px] list-decimal pl-5" style={{ color: t.textMain, lineHeight: 1.65 }}>
        <li>Playfair solo en títulos. Nunca en párrafos, botones ni cifras de tabla.</li>
        <li>Toda cifra que se compare va en JetBrains Mono con <code style={{ fontFamily: fonts.mono, color: t.cyan }}>font-variant-numeric: tabular-nums</code>.</li>
        <li>Renglones de 80 caracteres o menos (<code style={{ fontFamily: fonts.mono, color: t.cyan }}>max-width: 76ch</code> en bajadas).</li>
        <li>Mayúsculas solo en etiquetas mono, siempre con espaciado de letra.</li>
        <li>Interlineado del cuerpo 1.65; títulos, 1.05 a 1.2.</li>
      </ol>
    </Section>
  </>
);

const TabVoz = ({ t }) => (
  <>
    <Section t={t} number="01" title="Principios">
      <Table t={t} head={["Rasgo", "Sí", "No"]} rows={[
        ["Cercano", "«Tu dinero», «revisa», «pídele a la SSPC»", "«El usuario», «se recomienda al ciudadano»"],
        ["Riguroso", "«$357,887.3 mdp, ASF, Cuenta Pública 2024, auditoría 247, p. 8»", "«Cientos de miles de millones», «según fuentes»"],
        ["Honesto", "«Este dato no se publica; lo marcamos pendiente»", "Rellenar, redondear a ojo o estimar sin decirlo"],
        ["Sobrio", "«La ASF observó $14.1 mdp por recuperar»", "«¡Escándalo!», «saqueo», adjetivos de indignación"],
        ["Didáctico", "Explicar qué es el Ramo 33 la primera vez que aparece", "Dar por sabido el vocabulario técnico"],
      ]} />
    </Section>

    <Section t={t} number="02" title="Reglas de redacción">
      <ol className="space-y-3 text-[15px] list-decimal pl-5" style={{ color: t.textMain, lineHeight: 1.65, maxWidth: "76ch" }}>
        <li><strong>Al lector se le habla de tú</strong> (decisión del autor, 27-09-2026). Las citas textuales de leyes y documentos se dejan como están.</li>
        <li>Español con acentos, siempre: es contenido público.</li>
        <li>Toda cifra lleva fuente y chip de estado. Lo que es interpretación se rotula como «estimación propia».</li>
        <li>Las referencias van en el texto como [Ref. N], no como notas al pie debajo de las gráficas.</li>
        <li>Lo derogado se marca con su vigencia; no se borra.</li>
        <li>Unidades: 1 mdp es un millón de pesos, 1,000 mdp son mil millones y 1,000,000 mdp es un billón. No se usa «mil mdp».</li>
        <li>Solo se nombran limitaciones demostrables.</li>
        <li>Nombres de pestañas y módulos: no se cambian sin decisión del autor.</li>
      </ol>
    </Section>

    <Section t={t} number="03" title="Glosario de marca">
      <Table t={t} head={["Se dice", "No se dice"]} rows={[
        ["Auditavisión", "AuditaVisión, Audita Visión"],
        ["Pendiente (dato sin documento)", "Sin datos, N/D, «próximamente»"],
        ["Derivado (cálculo propio)", "Estimado, aproximado (salvo «estimación propia» para interpretaciones)"],
        ["Mdp (millones de pesos)", "MDP, mmdp, mil mdp"],
      ]} />
    </Section>

    <Section t={t} number="04" title="Sí y no">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {[
          [true, "Usa la ilustración en grande y el símbolo plano en pequeño."],
          [false, "No inventes una cifra, ni para una maqueta."],
          [true, "Toma colores y fuentes siempre de sus variables."],
          [false, "No uses un acento fuera de su papel."],
          [true, "Pon chip de estado a toda cifra."],
          [false, "No imites la imagen de una dependencia de gobierno."],
          [true, "Deja que el oro marque lo importante, y solo eso."],
          [false, "No uses emojis como marca ni como íconos de sección nuevos."],
          [true, "Revisa cada pantalla en los dos temas y a 390 px de ancho."],
          [false, "No quites el anillo de foco."],
        ].map(([ok, x]) => <DoDont key={x} t={t} ok={ok}>{x}</DoDont>)}
      </div>
    </Section>
  </>
);

const TabAplicaciones = ({ t }) => {
  const [focused, setFocused] = useState(false);
  return (
    <>
      <Section t={t} number="01" title="Los tres estados de un dato"
        lead="La pieza más propia del sistema. En el sitio los pinta chipEstado(estado) con la clase .est-chip. El color nunca va solo: el chip dice su estado y «pendiente» lleva borde punteado.">
        <Table t={t} head={["Estado", "Chip", "Significa"]} rows={[
          ["oficial", <Chip t={t} estado="oficial" />, "Tomado de su documento oficial"],
          ["derivado", <Chip t={t} estado="derivado" />, "Calculado por Auditavisión a partir de datos oficiales, con la operación dicha"],
          ["pendiente", <Chip t={t} estado="pendiente" />, "La fuente no lo publica o no se ha podido verificar"],
          ["contexto", <Chip t={t} estado="contexto" />, "Acompaña a lo que no es cifra"],
        ]} />
      </Section>

      <Section t={t} number="02" title="Tarjetas"
        lead="Fondo --bg-card, borde --border-subtle y radio grande. El borde dorado se reserva a la protagonista de su bloque, no a todas. Las cifras son los ejemplos de voz de DESIGN.md §6.1.">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card t={t} gold>
            <Label t={t} color={t.gold}>Protagonista · --border-gold</Label>
            <p className="mt-3 text-3xl" style={{ fontFamily: fonts.mono, fontWeight: 700, color: t.textMain, fontVariantNumeric: "tabular-nums" }}>$357,887.3 mdp</p>
            <p className="mt-2 text-[13px]" style={{ fontFamily: fonts.sans, color: t.textSecondary }}>ASF, Cuenta Pública 2024, auditoría 247, p. 8 <span style={{ fontFamily: fonts.mono, color: t.cyan }}>[Ref. N]</span></p>
            <div className="mt-3"><Chip t={t} estado="oficial" /></div>
          </Card>
          <Card t={t}>
            <Label t={t}>Tarjeta normal · --border-subtle</Label>
            <p className="mt-3 text-[15px]" style={{ fontFamily: fonts.body, color: t.textMain, lineHeight: 1.65 }}>
              La ASF observó <span style={{ fontFamily: fonts.mono, color: t.crimsonBright, fontVariantNumeric: "tabular-nums" }}>$14.1 mdp</span> por recuperar.
            </p>
            <p className="mt-3 text-[15px]" style={{ fontFamily: fonts.body, color: t.textMain, lineHeight: 1.65 }}>
              Este dato no se publica; lo marcamos pendiente. <Chip t={t} estado="pendiente" />
            </p>
          </Card>
        </div>
      </Section>

      <Section t={t} number="03" title="Radios"
        lead="Propuesta de DESIGN.md §5.1: tres radios más la píldora. Al migrar: 3 → 4, 6 → 8, 9 y 10 → 8, 14 → 12. Todavía no existen en el CSS.">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[["--radius-sm", 4, "Chips, etiquetas, foco"], ["--radius-md", 8, "Botones, campos, tarjetas pequeñas"], ["--radius-lg", 12, "Tarjetas, paneles, ventanas"], ["--radius-pill", 999, "Pastillas de filtro"]].map(([n, r, u]) => (
            <div key={n}>
              <div className="h-20 mb-2" style={{ borderRadius: r, background: t.goldGlow, border: `1px solid ${t.borderGold}` }} />
              <div className="text-xs" style={{ fontFamily: fonts.mono, color: t.textMain }}>{n} · {r} px</div>
              <div className="text-xs" style={{ fontFamily: fonts.sans, color: t.textSecondary }}>{u}</div>
            </div>
          ))}
        </div>
      </Section>

      <Section t={t} number="04" title="Foco"
        lead="Todo lo que se opera con teclado muestra outline: 2px solid var(--gold-bright) con outline-offset: 2px. No se quita nunca. Pasa el cursor sobre el botón para verlo.">
        <button type="button" onMouseEnter={() => setFocused(true)} onMouseLeave={() => setFocused(false)}
          onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
          className="px-5 py-2 text-sm"
          style={{
            fontFamily: fonts.sans, fontWeight: 600, borderRadius: 8, color: t.textGold, background: t.goldGlow,
            border: `1px solid ${t.borderGold}`, outline: focused ? `2px solid ${t.goldBright}` : "none", outlineOffset: 2,
          }}>
          Control con foco
        </button>
      </Section>

      <Section t={t} number="05" title="Encabezado"
        lead="La ilustración a 72 × 56 px y el nombre con el degradado dorado: el único lugar donde se usa.">
        <div className="rounded-xl p-6 flex items-center gap-4" style={{ background: t.surface, border: `1px solid ${t.borderSubtle}` }}>
          <img src={ILLUSTRATION} alt="" style={{ width: 72, height: 56 }} />
          <div>
            <div style={{ fontFamily: fonts.serif, fontWeight: 900, fontSize: "clamp(28px, 3.2vw, 36px)", lineHeight: 1.05, background: t.goldGradient, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" }}>
              Auditavisión
            </div>
            <div className="mt-1"><Label t={t}>Sistema cívico de fiscalización</Label></div>
          </div>
        </div>
      </Section>

      <Section t={t} number="06" title="Movimiento">
        <p className="text-[15px]" style={{ color: t.textMain, lineHeight: 1.65, maxWidth: "76ch" }}>
          Las cifras nacen en cero y cuentan con requestAnimationFrame y suavizado cúbico. Con
          prefers-reduced-motion: reduce, el dato aparece completo de inmediato.
        </p>
      </Section>
    </>
  );
};

// 5. Componente principal
const tabs = [
  { id: "esencia", label: "Esencia" },
  { id: "logo", label: "Logo" },
  { id: "color", label: "Color" },
  { id: "tipografia", label: "Tipografía" },
  { id: "voz", label: "Voz y tono" },
  { id: "aplicaciones", label: "Aplicaciones" },
];

export default function AuditavisionBrandGuidelines() {
  const [activeTab, setActiveTab] = useState("esencia");
  const [theme, setTheme] = useState("dark");
  const t = colors[theme];
  const lv = logoVariants.find((v) => v.id === `primary-${theme}`);

  return (
    <div className="min-h-screen" style={{ background: t.base, color: t.textMain, fontFamily: fonts.body }}>
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />

      <header className="sticky top-0 z-50" style={{ background: t.surface, backdropFilter: "blur(20px)", WebkitBackdropFilter: "blur(20px)", borderBottom: `1px solid ${t.borderSubtle}` }}>
        <div className="max-w-6xl mx-auto px-4 md:px-6 pt-4 flex items-center justify-between gap-4">
          <a href="../" aria-label="Volver a Auditavisión"><Combined height={34} coin={lv.coin} wings={lv.wings} name={lv.name} /></a>
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline text-[11px] uppercase" style={{ fontFamily: fonts.mono, letterSpacing: "0.12em", color: t.textSecondary }}>Sistema de marca v1.0</span>
            <button type="button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="px-3 py-1.5 text-xs" style={{ fontFamily: fonts.mono, borderRadius: 8, color: t.textMain, border: `1px solid ${t.borderAccent}`, background: t.card }}>
              {theme === "dark" ? "Tema claro" : "Tema oscuro"}
            </button>
          </div>
        </div>
        <nav className="max-w-6xl mx-auto px-2 md:px-4 mt-3 flex overflow-x-auto" aria-label="Secciones del sistema de marca">
          {tabs.map((tab) => (
            <button key={tab.id} type="button" onClick={() => setActiveTab(tab.id)}
              className="px-4 py-3 text-xs tracking-wider transition-all relative whitespace-nowrap"
              aria-current={activeTab === tab.id ? "page" : undefined}
              style={{ fontFamily: fonts.sans, color: activeTab === tab.id ? t.textMain : t.textSecondary, fontWeight: activeTab === tab.id ? 600 : 400 }}>
              {tab.label}
              {activeTab === tab.id && <div className="absolute bottom-0 left-4 right-4 h-0.5" style={{ background: t.gold }} />}
            </button>
          ))}
        </nav>
      </header>

      <main className="max-w-6xl mx-auto px-4 md:px-6 py-12">
        {activeTab === "esencia" && <TabEsencia t={t} />}
        {activeTab === "logo" && <TabLogo t={t} />}
        {activeTab === "color" && <TabColor t={t} theme={theme} />}
        {activeTab === "tipografia" && <TabTipografia t={t} />}
        {activeTab === "voz" && <TabVoz t={t} />}
        {activeTab === "aplicaciones" && <TabAplicaciones t={t} />}
      </main>

      <footer className="max-w-6xl mx-auto px-4 md:px-6 pb-12 text-xs" style={{ fontFamily: fonts.mono, color: t.textSecondary }}>
        Fuente única: DESIGN.md · Sistema de marca v1.0 · 29-09-2026
      </footer>
    </div>
  );
}
