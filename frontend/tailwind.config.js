/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Warm charcoal/sepia scale in place of Tailwind's default cool
        // gray — shifts every existing bg-gray-*/text-gray-* class toward
        // an "old field journal" mood without touching component code.
        gray: {
          50: "#f7f3ec",
          100: "#ece4d6",
          200: "#d9cbb4",
          300: "#b8a68a",
          400: "#a8977e", // lightened — was too low-contrast for body text
          500: "#8a7860", // lightened — was ~3:1 against the dark bg, now ~5:1
          600: "#6f5f4d", // lightened — was ~2:1, unreadable for empty-state text
          700: "#3a322b",
          800: "#251f1a",
          900: "#171310",
          950: "#0d0a08",
        },
        critical: "#b3402f", // rust
        atrisk: "#c98a2c",   // ochre
        safe: "#5a7d4f",     // moss
        brand: {
          DEFAULT: "#d4a24e", // unearthed gold — primary accent
          light: "#e8c179",
          dark: "#a67c34",
        },
      },
      fontFamily: {
        serif: ["Spectral", "ui-serif", "Georgia", "serif"],
      },
      // Bumped up from Tailwind's defaults across the board — small/muted
      // text throughout the app was hard to read. The dependency graph is
      // unaffected since its node text uses raw inline styles, not these
      // utility classes.
      fontSize: {
        xs: ["0.8125rem", { lineHeight: "1.25rem" }],   // 13px, was 12px
        sm: ["0.9375rem", { lineHeight: "1.4rem" }],     // 15px, was 14px
        base: ["1.0625rem", { lineHeight: "1.65rem" }],  // 17px, was 16px
        lg: ["1.1875rem", { lineHeight: "1.75rem" }],    // 19px, was 18px
        xl: ["1.3125rem", { lineHeight: "1.85rem" }],    // 21px, was 20px
        "2xl": ["1.5625rem", { lineHeight: "2rem" }],    // 25px, was 24px
      },
      keyframes: {
        "loading-slide": {
          "0%": { transform: "translateX(-100%)" },
          "50%": { transform: "translateX(150%)" },
          "100%": { transform: "translateX(400%)" },
        },
      },
      animation: {
        "loading-slide": "loading-slide 1.3s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
