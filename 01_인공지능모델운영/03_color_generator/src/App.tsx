import { useEffect, useMemo, useState } from 'react'
import './App.css'

type RgbColor = {
  r: number
  g: number
  b: number
}

type Locale = 'ko' | 'en'

const TEXT = {
  ko: {
    eyebrow: 'Background mood',
    title: '색으로 분위기를 바꿔보세요',
    description: '클릭 한 번으로 배경을 바꾸고, 색상 코드를 바로 확인하세요.',
    change: '배경색 변경',
    copy: 'HEX 코드 복사',
    copied: '복사 완료!',
    langToggle: 'English',
    hexLabel: 'HEX',
    hslLabel: 'HSL',
    brand: 'Color Studio',
  },
  en: {
    eyebrow: 'Background mood',
    title: 'Change the mood with color',
    description: 'Switch backgrounds in one tap and grab the color code instantly.',
    change: 'Change color',
    copy: 'Copy HEX',
    copied: 'Copied!',
    langToggle: '한국어',
    hexLabel: 'HEX',
    hslLabel: 'HSL',
    brand: 'Color Studio',
  },
} satisfies Record<Locale, Record<string, string>>

const randomColor = (): RgbColor => ({
  r: Math.floor(Math.random() * 256),
  g: Math.floor(Math.random() * 256),
  b: Math.floor(Math.random() * 256),
})

const rgbToHex = ({ r, g, b }: RgbColor) =>
  `#${[r, g, b].map((value) => value.toString(16).padStart(2, '0')).join('')}`

const rgbToHsl = ({ r, g, b }: RgbColor) => {
  const red = r / 255
  const green = g / 255
  const blue = b / 255
  const max = Math.max(red, green, blue)
  const min = Math.min(red, green, blue)
  const delta = max - min

  let hue = 0
  if (delta !== 0) {
    switch (max) {
      case red:
        hue = ((green - blue) / delta) % 6
        break
      case green:
        hue = (blue - red) / delta + 2
        break
      default:
        hue = (red - green) / delta + 4
        break
    }
  }

  hue = Math.round(hue * 60)
  if (hue < 0) hue += 360

  const lightness = (max + min) / 2
  const saturation =
    delta === 0 ? 0 : delta / (1 - Math.abs(2 * lightness - 1))

  return {
    h: Math.round(hue),
    s: Math.round(saturation * 100),
    l: Math.round(lightness * 100),
  }
}

const formatHsl = (color: RgbColor) => {
  const { h, s, l } = rgbToHsl(color)
  return `hsl(${h}°, ${s}%, ${l}%)`
}

function App() {
  const [color, setColor] = useState<RgbColor>(randomColor)
  const [copied, setCopied] = useState(false)
  const [locale, setLocale] = useState<Locale>('ko')

  const hexValue = useMemo(() => rgbToHex(color), [color])
  const hslValue = useMemo(() => formatHsl(color), [color])
  const text = useMemo(() => TEXT[locale], [locale])

  useEffect(() => {
    const root = document.documentElement
    root.style.setProperty('--bg-color', hexValue)
    return () => {
      root.style.removeProperty('--bg-color')
    }
  }, [hexValue])

  const handleCopy = async () => {
    if (!navigator.clipboard) return
    try {
      await navigator.clipboard.writeText(hexValue)
      setCopied(true)
      setTimeout(() => setCopied(false), 1200)
    } catch {
      setCopied(false)
    }
  }

  return (
    <div className="page">
      <div className="topbar">
        <span className="brand">{text.brand}</span>
        <button
          className="pill"
          onClick={() => setLocale((prev) => (prev === 'ko' ? 'en' : 'ko'))}
        >
          {text.langToggle}
        </button>
      </div>

      <div className="panel">
        <div className="header">
          <p className="eyebrow">{text.eyebrow}</p>
          <h1>{text.title}</h1>
          <p className="lede">{text.description}</p>
        </div>

        <div className="preview">
          <div className="swatch" style={{ background: hexValue }}>
            <div className="swatch-glow" />
          </div>
          <div className="codes">
            <div className="code">
              <span>{text.hexLabel}</span>
              <strong>{hexValue}</strong>
            </div>
            <div className="code">
              <span>{text.hslLabel}</span>
              <strong>{hslValue}</strong>
            </div>
          </div>
        </div>

        <div className="controls">
          <button className="primary" onClick={() => setColor(randomColor())}>
            {text.change}
          </button>
          <button className="ghost" onClick={handleCopy}>
            {copied ? text.copied : text.copy}
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
