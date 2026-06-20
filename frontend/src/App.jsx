import { useState, useEffect, useRef, useCallback } from "react"
import axios from "axios"

const API = "http://localhost:8000"

// ─── Fonts + Base Styles ─────────────────────────────────────────
if (typeof document !== "undefined" && !document.getElementById("fm-styles")) {
  const link = document.createElement("link")
  link.rel = "stylesheet"
  link.href = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap"
  document.head.appendChild(link)

  const s = document.createElement("style")
  s.id = "fm-styles"
  s.innerHTML = `
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { font-size: 14px; }
    body { font-family: 'Inter', -apple-system, sans-serif; transition: background 0.25s, color 0.25s; }

    @keyframes fadeUp    { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
    @keyframes fadeIn    { from{opacity:0} to{opacity:1} }
    @keyframes shimmer   { 0%{background-position:-600px 0} 100%{background-position:600px 0} }
    @keyframes ticker    { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
    @keyframes pulse     { 0%,100%{opacity:1} 50%{opacity:0.35} }
    @keyframes bounce3   { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-7px)} }
    @keyframes slideDown { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }
    @keyframes scaleIn   { from{opacity:0;transform:scale(0.96)} to{opacity:1;transform:scale(1)} }

    .fade-up   { animation: fadeUp  0.3s ease both; }
    .fade-in   { animation: fadeIn  0.2s ease both; }
    .scale-in  { animation: scaleIn 0.2s ease both; }

    ::-webkit-scrollbar { width:4px; height:4px; }
    ::-webkit-scrollbar-track { background:transparent; }
    ::-webkit-scrollbar-thumb { background:#d1d5db; border-radius:4px; }

    input,textarea,button,select { font-family:inherit; }
    button { cursor:pointer; border:none; background:none; }
    input[type=range] { cursor:pointer; }

    .desktop-only { display:flex !important; }
    .mobile-only  { display:none  !important; }
    @media(max-width:768px){
      .desktop-only { display:none  !important; }
      .mobile-only  { display:flex  !important; }
      .two-col   { grid-template-columns:1fr !important; }
      .three-col { grid-template-columns:1fr 1fr !important; }
      .four-col  { grid-template-columns:1fr 1fr !important; }
      .six-col   { grid-template-columns:repeat(3,1fr) !important; }
    }
    @media(max-width:480px){
      .three-col { grid-template-columns:1fr !important; }
      .six-col   { grid-template-columns:repeat(2,1fr) !important; }
    }
  `
  document.head.appendChild(s)
}

// ─── Theme tokens ────────────────────────────────────────────────
const THEMES = {
  light: {
    bg:        "#ffffff",
    bgSub:     "#f7f7f8",
    bgTer:     "#f0f0f2",
    text:      "#0a0a0a",
    textSub:   "#6b7280",
    textTer:   "#9ca3af",
    accent:    "#2563eb",
    accentBg:  "#eff6ff",
    accentHov: "#1d4ed8",
    green:     "#16a34a",
    greenBg:   "#f0fdf4",
    greenBd:   "#bbf7d0",
    red:       "#dc2626",
    redBg:     "#fef2f2",
    redBd:     "#fecaca",
    amber:     "#d97706",
    amberBg:   "#fffbeb",
    amberBd:   "#fde68a",
    border:    "rgba(0,0,0,0.08)",
    borderEm:  "rgba(0,0,0,0.15)",
    shadow:    "0 2px 12px rgba(0,0,0,0.07)",
    mono:      "'JetBrains Mono', monospace",
    chartGrid: "rgba(0,0,0,0.05)",
    chartText: "#9ca3af",
    navBg:     "rgba(255,255,255,0.95)",
    skeletonA: "#f0f0f0",
    skeletonB: "#e0e0e0",
  },
  dark: {
    bg:        "#111111",
    bgSub:     "#1a1a1a",
    bgTer:     "#222222",
    text:      "#f1f1f1",
    textSub:   "#9ca3af",
    textTer:   "#6b7280",
    accent:    "#3b82f6",
    accentBg:  "#1e3a5f",
    accentHov: "#2563eb",
    green:     "#22c55e",
    greenBg:   "#052e16",
    greenBd:   "#166534",
    red:       "#ef4444",
    redBg:     "#2d0a0a",
    redBd:     "#7f1d1d",
    amber:     "#f59e0b",
    amberBg:   "#1c1408",
    amberBd:   "#78350f",
    border:    "rgba(255,255,255,0.08)",
    borderEm:  "rgba(255,255,255,0.14)",
    shadow:    "0 2px 20px rgba(0,0,0,0.4)",
    mono:      "'JetBrains Mono', monospace",
    chartGrid: "rgba(255,255,255,0.05)",
    chartText: "#6b7280",
    navBg:     "rgba(17,17,17,0.96)",
    skeletonA: "#1e1e1e",
    skeletonB: "#2a2a2a",
  }
}

// ─── Helpers ─────────────────────────────────────────────────────
const fmt = v => (!v && v !== 0) || v === "N/A" ? "—" : typeof v === "number" ? v.toLocaleString("en-IN", { maximumFractionDigits: 2 }) : v
const pct = v => { if (!v && v !== 0) return "—"; const n = parseFloat(v); return `${n >= 0 ? "▲" : "▼"} ${Math.abs(n).toFixed(2)}%` }
const clrVal = (v, T) => parseFloat(v) >= 0 ? T.green : T.red

function getVerdict(report) {
  if (!report) return null
  if (report.includes("BUY"))  return { text: "BUY",  k: "green" }
  if (report.includes("SELL")) return { text: "SELL", k: "red" }
  return { text: "HOLD", k: "amber" }
}

// ─── Shared primitives ───────────────────────────────────────────
function Card({ children, style, onClick, T }) {
  const [hov, setHov] = useState(false)
  return (
    <div onClick={onClick}
      onMouseEnter={() => onClick && setHov(true)}
      onMouseLeave={() => onClick && setHov(false)}
      style={{
        background: T.bg, border: `1px solid ${hov ? T.borderEm : T.border}`,
        borderRadius: 12, padding: "16px 18px",
        boxShadow: hov ? T.shadow : "none",
        cursor: onClick ? "pointer" : "default",
        transition: "border-color 0.15s, box-shadow 0.15s",
        ...style
      }}>
      {children}
    </div>
  )
}

function SLabel({ children, T }) {
  return <div style={{ fontSize: 11, fontWeight: 600, color: T.textTer, textTransform: "uppercase", letterSpacing: "1px", marginBottom: 10 }}>{children}</div>
}

function Badge({ children, color, bg, border, T }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center",
      fontSize: 11, fontWeight: 600, padding: "3px 10px", borderRadius: 20,
      color: color || T.textSub, background: bg || T.bgSub,
      border: `1px solid ${border || T.border}`
    }}>{children}</span>
  )
}

function Btn({ children, onClick, loading, full, style, T }) {
  const [hov, setHov] = useState(false)
  return (
    <button onClick={onClick} disabled={loading}
      onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)}
      style={{
        display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
        padding: "10px 20px", borderRadius: 8, fontSize: 13, fontWeight: 500,
        background: loading ? T.textTer : hov ? T.accentHov : T.accent,
        color: "#fff", width: full ? "100%" : undefined,
        transition: "background 0.15s", ...style
      }}>
      {loading ? <ThinkDots /> : children}
    </button>
  )
}

function ThinkDots({ label }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 5 }}>
      {label && <span style={{ fontSize: 12 }}>{label}</span>}
      {[0, 0.15, 0.3].map((d, i) => (
        <span key={i} style={{ width: 5, height: 5, borderRadius: "50%", background: "#fff", display: "inline-block", animation: `bounce3 1s ${d}s ease infinite` }} />
      ))}
    </span>
  )
}

function FInput({ value, onChange, onKeyDown, placeholder, type = "text", T, style }) {
  const [foc, setFoc] = useState(false)
  return (
    <input type={type} value={value} onChange={onChange} onKeyDown={onKeyDown} placeholder={placeholder}
      onFocus={() => setFoc(true)} onBlur={() => setFoc(false)}
      style={{
        width: "100%", padding: "10px 14px", fontSize: 13,
        border: `1px solid ${foc ? T.accent : T.borderEm}`,
        boxShadow: foc ? `0 0 0 3px ${T.accent}22` : "none",
        borderRadius: 8, background: T.bg, color: T.text, outline: "none",
        transition: "border-color 0.15s, box-shadow 0.15s",
        ...style
      }}
    />
  )
}

function DataRow({ label, value, color, T }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "7px 0", borderBottom: `1px solid ${T.border}` }}>
      <span style={{ fontSize: 12, color: T.textSub }}>{label}</span>
      <span style={{ fontSize: 12, fontWeight: 500, color: color || T.text, fontFamily: T.mono }}>{value || "—"}</span>
    </div>
  )
}

function Skeleton({ h, T, style }) {
  return (
    <div style={{
      height: h || 20, borderRadius: 8,
      background: `linear-gradient(90deg, ${T.skeletonA} 25%, ${T.skeletonB} 50%, ${T.skeletonA} 75%)`,
      backgroundSize: "600px 100%",
      animation: "shimmer 1.4s ease infinite",
      ...style
    }} />
  )
}

// ─── ENHANCED Candlestick Chart ───────────────────────────────────
function CandlestickChart({ chartData, T }) {
  const { labels = [], open = [], high = [], low = [], close = [] } = chartData || {}
  const [hoverIdx, setHoverIdx] = useState(null)
  const svgRef = useRef(null)

  if (!close || close.length < 2) return (
    <div style={{ padding: 24, textAlign: "center", color: T.textTer, fontSize: 12 }}>Chart data unavailable</div>
  )

  const W = 560, H = 160, padT = 16, padB = 24, padL = 52, padR = 12
  const allVals = [...high, ...low]
  const minV = Math.min(...allVals), maxV = Math.max(...allVals), range = maxV - minV || 1
  const n = close.length
  const slot = (W - padL - padR) / n
  const cw = Math.min(slot * 0.55, 18)
  const y = v => padT + ((maxV - v) / range) * (H - padT - padB)
  const x = i => padL + i * slot + slot / 2

  // Y axis labels
  const yTicks = 4
  const yLabels = Array.from({ length: yTicks + 1 }, (_, i) => {
    const val = minV + (range * i) / yTicks
    return { val: val.toFixed(val > 1000 ? 0 : 2), y: y(val) }
  })

  const handleMouseMove = (e) => {
    const rect = svgRef.current?.getBoundingClientRect()
    if (!rect) return
    const mouseX = (e.clientX - rect.left) * (W / rect.width)
    const idx = Math.round((mouseX - padL) / slot)
    if (idx >= 0 && idx < n) setHoverIdx(idx)
    else setHoverIdx(null)
  }

  const hi = hoverIdx !== null ? hoverIdx : null

  return (
    <div>
      <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: 160, cursor: "crosshair" }}
        preserveAspectRatio="none"
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setHoverIdx(null)}>

        {/* Grid lines */}
        {yLabels.map((l, i) => (
          <line key={i} x1={padL} y1={l.y} x2={W - padR} y2={l.y} stroke={T.chartGrid} strokeWidth="1" />
        ))}

        {/* Y axis labels */}
        {yLabels.map((l, i) => (
          <text key={i} x={padL - 6} y={l.y + 4} textAnchor="end" fontSize={9} fill={T.chartText} fontFamily={T.mono}>{l.val}</text>
        ))}

        {/* Candles */}
        {close.map((_, i) => {
          const isUp = close[i] >= open[i]
          const color = isUp ? T.green : T.red
          const cx = x(i)
          const bT = y(Math.max(open[i], close[i]))
          const bB = y(Math.min(open[i], close[i]))
          const isHov = hi === i
          return (
            <g key={i} opacity={hi !== null && !isHov ? 0.4 : 1} style={{ transition: "opacity 0.1s" }}>
              <line x1={cx} y1={y(high[i])} x2={cx} y2={y(low[i])} stroke={color} strokeWidth={isHov ? 2 : 1.5} />
              <rect x={cx - cw / 2} y={bT} width={cw} height={Math.max(bB - bT, 1.5)}
                fill={isUp ? color : color} stroke={color} strokeWidth="0.5"
                rx="1" opacity={isHov ? 1 : 0.85}
              />
              {isHov && <line x1={cx} y1={padT} x2={cx} y2={H - padB} stroke={T.accent} strokeWidth="1" strokeDasharray="3 3" />}
            </g>
          )
        })}

        {/* X axis labels */}
        {[0, Math.floor(n / 2), n - 1].map(i => (
          <text key={i} x={x(i)} y={H - 4} textAnchor="middle" fontSize={9} fill={T.chartText} fontFamily={T.mono}>{labels[i]}</text>
        ))}
      </svg>

      {/* Hover tooltip */}
      {hi !== null && (
        <div className="fade-in" style={{
          background: T.bgSub, border: `1px solid ${T.borderEm}`, borderRadius: 8,
          padding: "8px 12px", marginTop: 6, display: "flex", gap: 16, flexWrap: "wrap"
        }}>
          <span style={{ fontSize: 11, color: T.textSub }}>🕐 {labels[hi]}</span>
          {[["O", open[hi]], ["H", high[hi]], ["L", low[hi]], ["C", close[hi]]].map(([k, v]) => (
            <span key={k} style={{ fontSize: 11, fontFamily: T.mono }}>
              <span style={{ color: T.textTer }}>{k}: </span>
              <span style={{ color: k === "C" ? clrVal(close[hi] - open[hi], T) : T.text, fontWeight: 500 }}>{v?.toFixed(2)}</span>
            </span>
          ))}
          <span style={{ fontSize: 11, color: close[hi] >= open[hi] ? T.green : T.red, fontWeight: 600 }}>
            {close[hi] >= open[hi] ? "▲" : "▼"} {Math.abs(((close[hi] - open[hi]) / open[hi]) * 100).toFixed(2)}%
          </span>
        </div>
      )}

      <div style={{ display: "flex", gap: 14, justifyContent: "center", marginTop: 8 }}>
        {[["Bullish", T.green], ["Bearish", T.red]].map(([l, c]) => (
          <span key={l} style={{ fontSize: 10, color: c, display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ width: 8, height: 8, background: c, borderRadius: 1, display: "inline-block" }} /> {l}
          </span>
        ))}
      </div>
    </div>
  )
}

// ─── Market Ticker ────────────────────────────────────────────────
function MarketTicker({ T }) {
  const [stocks, setStocks] = useState([])
  const [paused, setPaused] = useState(false)
  useEffect(() => {
    const go = async () => { try { const r = await axios.get(`${API}/ticker`); setStocks(r.data.data) } catch {} }
    go(); const iv = setInterval(go, 60000); return () => clearInterval(iv)
  }, [])
  if (!stocks.length) return <div style={{ fontSize: 11, color: T.textSub }}>Loading market data...</div>
  const items = [...stocks, ...stocks]
  return (
    <div style={{ overflow: "hidden" }} onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)}>
      <div style={{ display: "flex", gap: 28, animation: paused ? "none" : "ticker 32s linear infinite", whiteSpace: "nowrap" }}>
        {items.map((s, i) => (
          <span key={i} style={{ display: "inline-flex", alignItems: "center", gap: 8, fontSize: 12 }}>
            <span style={{ fontWeight: 500, color: T.text }}>{s.name}</span>
            {s.price ? <span style={{ fontSize: 11, fontFamily: T.mono, color: T.textSub }}>₹{s.price.toLocaleString("en-IN")}</span> : null}
            <span style={{ fontSize: 10, fontWeight: 600, padding: "1px 7px", borderRadius: 12, color: s.val >= 0 ? T.green : T.red, background: s.val >= 0 ? T.greenBg : T.redBg }}>
              {s.val >= 0 ? "▲" : "▼"} {Math.abs(s.val).toFixed(2)}%
            </span>
          </span>
        ))}
      </div>
    </div>
  )
}

// ─── RISK PROFILE MODAL ───────────────────────────────────────────
function RiskModal({ onSave, T }) {
  const [selected, setSelected] = useState(null)
  const profiles = [
    { key: "conservative", icon: "🛡️", label: "Conservative", desc: "Capital protection first. FD, PPF, debt funds. Low risk, steady returns." },
    { key: "moderate",     icon: "⚖️", label: "Moderate",     desc: "Balanced approach. Mix of equity + debt. Medium risk, medium returns." },
    { key: "aggressive",   icon: "🚀", label: "Aggressive",   desc: "Maximum growth. Direct stocks, small-cap, crypto. High risk, high reward." },
  ]
  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", zIndex: 500, display: "flex", alignItems: "center", justifyContent: "center", padding: 20 }}>
      <div className="scale-in" style={{ background: T.bg, border: `1px solid ${T.borderEm}`, borderRadius: 16, padding: 28, maxWidth: 480, width: "100%" }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div style={{ fontSize: 32, marginBottom: 10 }}>📋</div>
          <div style={{ fontSize: 18, fontWeight: 600, color: T.text, marginBottom: 6 }}>Risk Profile Setup</div>
          <div style={{ fontSize: 13, color: T.textSub, lineHeight: 1.6 }}>Aapka investment risk tolerance kya hai? Isse main aapko better advice de sakta hun.</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 20 }}>
          {profiles.map(p => (
            <div key={p.key} onClick={() => setSelected(p.key)}
              style={{
                padding: "14px 16px", borderRadius: 10, cursor: "pointer",
                border: `2px solid ${selected === p.key ? T.accent : T.border}`,
                background: selected === p.key ? T.accentBg : T.bgSub,
                transition: "all 0.15s", display: "flex", alignItems: "flex-start", gap: 12
              }}>
              <span style={{ fontSize: 22 }}>{p.icon}</span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: selected === p.key ? T.accent : T.text, marginBottom: 3 }}>{p.label}</div>
                <div style={{ fontSize: 12, color: T.textSub, lineHeight: 1.5 }}>{p.desc}</div>
              </div>
            </div>
          ))}
        </div>
        <Btn onClick={() => selected && onSave(selected)} full T={T} style={{ padding: 12, borderRadius: 10, opacity: selected ? 1 : 0.5 }}>
          {selected ? `Set Risk Profile: ${profiles.find(p => p.key === selected)?.label}` : "Select a profile to continue"}
        </Btn>
        <div style={{ textAlign: "center", marginTop: 10 }}>
          <button onClick={() => onSave("moderate")} style={{ fontSize: 12, color: T.textTer, textDecoration: "underline", background: "none", border: "none", cursor: "pointer" }}>
            Skip for now (set to Moderate)
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── HOME PAGE ────────────────────────────────────────────────────
function HomePage({ setTab, setInput, chatInputRef, T, watchlist, setWatchlist, analyzeStock }) {
  const features = [
    { icon: "💬", title: "AI Financial Advisor", desc: "CA + Broker level personalized advice", tab: "chat" },
    { icon: "📊", title: "Stock Analysis",        desc: "AI-powered Buy / Hold / Sell reports",  tab: "stocks" },
    { icon: "🧾", title: "Tax Calculator",        desc: "Old vs New regime — 2024-25",           tab: "tax" },
    { icon: "📈", title: "SIP Planner",           desc: "Goal planning & returns calculator",    tab: "sip" },
  ]
  const quickAsks = ["SIP kaise shuru karun?", "80C mein kya invest karun?", "Emergency fund kya hota hai?", "ELSS vs PPF — kaunsa better?"]
  return (
    <div style={{ maxWidth: 860, margin: "0 auto", padding: "32px 20px 80px" }}>
      <div className="fade-up" style={{ textAlign: "center", marginBottom: 36 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: T.accent, textTransform: "uppercase", letterSpacing: "2px", marginBottom: 10 }}>
          AI-Powered · CA + Broker Intelligence
        </div>
        <h1 style={{ fontSize: 34, fontWeight: 600, color: T.text, lineHeight: 1.2, marginBottom: 10, letterSpacing: "-0.5px" }}>
          Your personal CA, Broker<br />& Financial Advisor — in one.
        </h1>
        <p style={{ fontSize: 14, color: T.textSub, marginBottom: 22, lineHeight: 1.7, maxWidth: 480, margin: "0 auto 22px" }}>
          Stock entry/exit levels, tax planning, SIP calculations — ask anything in Hindi or English.
        </p>
        <div style={{ display: "flex", gap: 8, justifyContent: "center", flexWrap: "wrap", marginBottom: 22 }}>
          {quickAsks.map((q, i) => (
            <button key={i} onClick={() => { setInput(q); setTab("chat"); setTimeout(() => chatInputRef.current?.focus(), 100) }}
              style={{ padding: "7px 16px", border: `1px solid ${T.border}`, borderRadius: 20, fontSize: 12, color: T.textSub, background: T.bg, transition: "all 0.15s" }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = T.accent; e.currentTarget.style.color = T.accent; e.currentTarget.style.background = T.accentBg }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.color = T.textSub; e.currentTarget.style.background = T.bg }}>
              {q}
            </button>
          ))}
        </div>
        <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
          <Btn onClick={() => setTab("chat")} T={T} style={{ padding: "11px 24px" }}>Ask FinMate AI →</Btn>
          <button onClick={() => setTab("stocks")}
            style={{ padding: "11px 24px", border: `1px solid ${T.borderEm}`, borderRadius: 8, fontSize: 13, color: T.text, background: T.bg, transition: "background 0.15s" }}
            onMouseEnter={e => e.currentTarget.style.background = T.bgSub}
            onMouseLeave={e => e.currentTarget.style.background = T.bg}>
            Analyze a Stock
          </button>
        </div>
      </div>

      <div className="two-col" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
        {features.map((f, i) => (
          <Card key={i} onClick={() => setTab(f.tab)} T={T} style={{ padding: "18px 20px", animationDelay: `${i * 0.06}s` }} className="fade-up">
            <div style={{ fontSize: 24, marginBottom: 10 }}>{f.icon}</div>
            <div style={{ fontSize: 14, fontWeight: 500, color: T.text, marginBottom: 4 }}>{f.title}</div>
            <div style={{ fontSize: 12, color: T.textSub, lineHeight: 1.6 }}>{f.desc}</div>
          </Card>
        ))}
      </div>

      <Card T={T} style={{ padding: 0, overflow: "hidden" }}>
        <div className="four-col" style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)" }}>
          {[["60+", "Symbols covered"], ["LLaMA 3.3", "AI model"], ["2024-25", "Tax year"], ["Hi / En", "Languages"]].map(([v, l], i) => (
            <div key={i} style={{ padding: "16px 14px", textAlign: "center", borderRight: i < 3 ? `1px solid ${T.border}` : "none" }}>
              <div style={{ fontSize: 18, fontWeight: 600, color: T.accent, fontFamily: T.mono }}>{v}</div>
              <div style={{ fontSize: 11, color: T.textSub, marginTop: 3 }}>{l}</div>
            </div>
          ))}
        </div>
      </Card>

      <WatchlistSection watchlist={watchlist} setWatchlist={setWatchlist} analyzeStock={analyzeStock} setTab={setTab} T={T} />
    </div>
  )
}

// ─── CHAT PAGE — CA + BROKER LEVEL ───────────────────────────────
function ChatPage({ messages, input, setInput, loading, sendMessage, chatEndRef, chatInputRef, lastStockData, lastStockReport, riskProfile, T }) {
  const [rows, setRows] = useState(1)

  // Context chips based on last analyzed stock
  const stockCtxChips = lastStockData ? [
    `${lastStockData.name?.split(" ")[0]} khareedun?`,
    `${lastStockData.symbol} ka target price kya hai?`,
    `Stop loss kahan rakhu?`,
  ] : []

  const generalChips = ["SIP calculate karo", "Tax regime compare karo", "Portfolio rebalance karo", "Best ELSS funds 2024"]
  const chips = [...stockCtxChips, ...generalChips].slice(0, 5)

  const handleKey = e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage() }
  }

  return (
    <div className="fade-in" style={{ maxWidth: 780, margin: "0 auto", padding: "18px 20px 0", height: "calc(100vh - 130px)", display: "flex", flexDirection: "column" }}>

      {/* Header */}
      <div style={{ marginBottom: 12, paddingBottom: 12, borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 38, height: 38, borderRadius: "50%", background: T.accentBg, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>🤖</div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 500, color: T.text }}>FinMate AI — CA + Broker</div>
            <div style={{ fontSize: 11, color: T.green, display: "flex", alignItems: "center", gap: 4 }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: T.green, display: "inline-block", animation: "pulse 2s infinite" }} />
              Online · Risk: <strong style={{ textTransform: "capitalize", marginLeft: 3 }}>{riskProfile}</strong>
            </div>
          </div>
        </div>
        {lastStockData && (
          <div style={{ fontSize: 11, color: T.textSub, background: T.bgSub, border: `1px solid ${T.border}`, borderRadius: 8, padding: "5px 10px", display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ color: T.accent }}>📊</span>
            Context: <strong style={{ color: T.text, marginLeft: 3 }}>{lastStockData.symbol}</strong>
          </div>
        )}
      </div>

      {/* Chips */}
      <div style={{ display: "flex", gap: 6, marginBottom: 12, flexWrap: "wrap" }}>
        {chips.map((q, i) => (
          <button key={i} onClick={() => setInput(q)}
            style={{ padding: "5px 12px", border: `1px solid ${T.border}`, borderRadius: 16, fontSize: 11, color: T.textSub, background: T.bg, transition: "all 0.15s" }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = T.accent; e.currentTarget.style.color = T.accent }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.color = T.textSub }}>
            {i < stockCtxChips.length ? "📊 " : ""}{q}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", paddingRight: 4, paddingBottom: 8 }}>
        {messages.map((msg, i) => (
          <div key={i} className="fade-up" style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start", marginBottom: 14, alignItems: "flex-end", gap: 8 }}>
            {msg.role === "bot" && (
              <div style={{ width: 28, height: 28, borderRadius: "50%", background: T.accentBg, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, flexShrink: 0 }}>🤖</div>
            )}
            <div style={{
              maxWidth: "74%", padding: "11px 15px", borderRadius: 12, fontSize: 13, lineHeight: 1.8, whiteSpace: "pre-wrap",
              background: msg.role === "user" ? T.accent : T.bg,
              color: msg.role === "user" ? "#fff" : T.text,
              border: msg.role === "user" ? "none" : `1px solid ${T.border}`,
              borderBottomLeftRadius: msg.role === "bot" ? 4 : 12,
              borderBottomRightRadius: msg.role === "user" ? 4 : 12,
            }}>
              {msg.text}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: "flex", alignItems: "flex-end", gap: 8, marginBottom: 14 }}>
            <div style={{ width: 28, height: 28, borderRadius: "50%", background: T.accentBg, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13 }}>🤖</div>
            <div style={{ padding: "11px 16px", border: `1px solid ${T.border}`, borderRadius: "12px 12px 12px 4px", background: T.bg }}>
              <ThinkDots label="Analyzing" />
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div style={{ paddingTop: 10, paddingBottom: 14, borderTop: `1px solid ${T.border}` }}>
        <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
          <textarea ref={chatInputRef} value={input}
            onChange={e => { setInput(e.target.value); setRows(Math.min(4, e.target.value.split("\n").length)) }}
            onKeyDown={handleKey}
            placeholder="Kuch bhi puchho — stock entry level, tax saving, SIP, portfolio review..."
            rows={rows}
            style={{
              flex: 1, padding: "11px 16px", fontSize: 13, resize: "none",
              border: `1px solid ${T.borderEm}`, borderRadius: 10,
              background: T.bg, color: T.text, outline: "none",
              transition: "border-color 0.15s, box-shadow 0.15s", lineHeight: 1.6
            }}
            onFocus={e => { e.target.style.borderColor = T.accent; e.target.style.boxShadow = `0 0 0 3px ${T.accent}22` }}
            onBlur={e => { e.target.style.borderColor = T.borderEm; e.target.style.boxShadow = "none" }}
          />
          <Btn onClick={sendMessage} loading={loading} T={T} style={{ padding: "11px 18px", borderRadius: 10, flexShrink: 0, alignSelf: "flex-end" }}>
            Send →
          </Btn>
        </div>
        <div style={{ fontSize: 10, color: T.textTer, marginTop: 6 }}>Enter to send · Shift+Enter for new line</div>
      </div>
    </div>
  )
}

// ─── STOCKS PAGE ──────────────────────────────────────────────────
function StocksPage({ symbol, setSymbol, suggestions, stockData, stockReport, stockLoading, stockError, analyzeStock, T, addToWatchlist, isWatched }) {
  const verdict = getVerdict(stockReport)
  const [activeCategory, setActiveCategory] = useState("All")
  const vColors = verdict ? { color: T[verdict.k], bg: T[`${verdict.k}Bg`], border: T[`${verdict.k}Bd`] } : null

  return (
    <div className="fade-in" style={{ maxWidth: 960, margin: "0 auto", padding: "20px 20px 80px" }}>
      <div style={{ marginBottom: 18 }}>
        <h2 style={{ fontSize: 20, fontWeight: 500, color: T.text, marginBottom: 4 }}>Stock Analysis</h2>
        <p style={{ fontSize: 13, color: T.textSub }}>Search any stock, crypto, forex, or commodity — AI-powered analysis.</p>
      </div>

      {/* Search */}
      <div style={{ position: "relative", marginBottom: 14 }}>
        <div style={{ position: "relative" }}>
          <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", fontSize: 15, color: T.textTer, pointerEvents: "none" }}>🔍</span>
          <input value={symbol} onChange={e => setSymbol(e.target.value)} onKeyDown={e => e.key === "Enter" && analyzeStock()}
            placeholder="Search — Apple, Reliance, TCS, Bitcoin, Gold, USD/INR..."
            style={{ width: "100%", padding: "13px 130px 13px 42px", fontSize: 14, border: `1px solid ${T.borderEm}`, borderRadius: 10, background: T.bg, color: T.text, outline: "none", transition: "border-color 0.15s, box-shadow 0.15s" }}
            onFocus={e => { e.target.style.borderColor = T.accent; e.target.style.boxShadow = `0 0 0 3px ${T.accent}22` }}
            onBlur={e => { e.target.style.borderColor = T.borderEm; e.target.style.boxShadow = "none" }}
          />
          <Btn onClick={() => analyzeStock()} loading={stockLoading} T={T} style={{ position: "absolute", right: 6, top: "50%", transform: "translateY(-50%)", padding: "7px 16px", fontSize: 12, borderRadius: 7 }}>
            {stockLoading ? "..." : "Analyze →"}
          </Btn>
        </div>

        {suggestions.length > 0 && (
          <div className="scale-in" style={{ position: "absolute", top: "100%", left: 0, right: 0, marginTop: 4, background: T.bg, border: `1px solid ${T.borderEm}`, borderRadius: 10, boxShadow: T.shadow, zIndex: 200, overflow: "hidden" }}>
            {suggestions.map((s, i) => (
              <div key={i} onClick={() => analyzeStock(s.symbol)}
                style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 14px", cursor: "pointer", borderBottom: i < suggestions.length - 1 ? `1px solid ${T.border}` : "none", transition: "background 0.1s" }}
                onMouseEnter={e => e.currentTarget.style.background = T.bgSub}
                onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                <span style={{ fontSize: 13, fontWeight: 500, color: T.text }}>{s.name}</span>
                <div style={{ display: "flex", gap: 6 }}>
                  <Badge T={T}>{s.symbol}</Badge>
                  <Badge color={T.accent} bg={T.accentBg} border={T.accent} T={T}>{s.exchange}</Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Category pills */}
      <div style={{ display: "flex", gap: 6, marginBottom: 20, flexWrap: "wrap" }}>
        {["All", "India", "US", "Crypto", "Forex", "Commodities"].map(c => (
          <button key={c} onClick={() => setActiveCategory(c)}
            style={{ padding: "5px 14px", borderRadius: 16, fontSize: 12, fontWeight: 500, border: `1px solid ${activeCategory === c ? T.accent : T.border}`, background: activeCategory === c ? T.accentBg : T.bg, color: activeCategory === c ? T.accent : T.textSub, transition: "all 0.15s" }}>
            {c}
          </button>
        ))}
      </div>

      {stockError && (
        <div className="fade-in" style={{ background: T.redBg, border: `1px solid ${T.redBd}`, borderRadius: 10, padding: "12px 16px", color: T.red, marginBottom: 16, fontSize: 13 }}>
          ❌ {stockError}
        </div>
      )}

      {stockLoading && (
        <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <Skeleton h={110} T={T} />
          <Skeleton h={180} T={T} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <Skeleton h={220} T={T} />
            <Skeleton h={220} T={T} />
          </div>
          <Skeleton h={160} T={T} />
          <div style={{ textAlign: "center", fontSize: 12, color: T.textSub, marginTop: 4 }}>Fetching live data + generating AI report (20–30s)...</div>
        </div>
      )}

      {stockData && !stockLoading && (
        <div className="fade-up">
          {/* Price card */}
          <Card T={T} style={{ marginBottom: 12, padding: 0, overflow: "hidden" }}>
            <div style={{ padding: "10px 16px", background: T.bgSub, borderBottom: `1px solid ${T.border}`, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 6 }}>
              <span style={{ fontSize: 11, color: T.textSub, fontWeight: 500 }}>
                {stockData.symbol} · {stockData.sector !== "N/A" ? stockData.sector : "Global Market"}
              </span>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <button
                  onClick={() => addToWatchlist(stockData.symbol, stockData.name)}
                  title={isWatched(stockData.symbol) ? "Already in watchlist" : "Add to watchlist"}
                  style={{ fontSize: 16, lineHeight: 1, padding: "2px 6px", borderRadius: 6, border: `1px solid ${T.border}`, background: isWatched(stockData.symbol) ? "#fef9c3" : T.bgSub, cursor: "pointer", transition: "all 0.15s" }}>
                  {isWatched(stockData.symbol) ? "⭐" : "☆"}
                </button>
                {vColors && (
                  <span style={{ fontSize: 12, fontWeight: 600, padding: "3px 14px", borderRadius: 20, color: vColors.color, background: vColors.bg, border: `1px solid ${vColors.border}` }}>
                    {verdict.text}
                  </span>
                )}
              </div>
            </div>
            <div style={{ padding: "16px 18px" }}>
              <div style={{ fontSize: 12, color: T.textSub, marginBottom: 6 }}>{stockData.name}</div>
              <div style={{ display: "flex", alignItems: "baseline", gap: 14, flexWrap: "wrap" }}>
                <span style={{ fontSize: 30, fontWeight: 600, color: T.text, fontFamily: T.mono }}>{stockData.currency} {fmt(stockData.current_price)}</span>
                <span style={{ fontSize: 14, fontWeight: 500, color: clrVal(stockData.price_change_1d, T) }}>{pct(stockData.price_change_1d)} today</span>
                <span style={{ fontSize: 12, color: T.textSub }}>{stockData.trend}</span>
              </div>
            </div>
            <div className="six-col" style={{ display: "grid", gridTemplateColumns: "repeat(6,1fr)", borderTop: `1px solid ${T.border}` }}>
              {[["1M", pct(stockData.price_change_1m), clrVal(stockData.price_change_1m, T)], ["1Y", pct(stockData.price_change_1y), clrVal(stockData.price_change_1y, T)], ["52W H", fmt(stockData["52w_high"]), T.green], ["52W L", fmt(stockData["52w_low"]), T.red], ["Vol", stockData.volume ? (stockData.volume / 100000).toFixed(1) + "L" : "—", T.text], ["Mkt Cap", stockData.market_cap ? (stockData.market_cap / 1e12).toFixed(2) + "T" : "—", T.text]].map(([l, v, c], i) => (
                <div key={i} style={{ padding: "10px 12px", textAlign: "center", borderRight: i < 5 ? `1px solid ${T.border}` : "none" }}>
                  <div style={{ fontSize: 10, color: T.textTer, textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 3 }}>{l}</div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: c, fontFamily: T.mono }}>{v}</div>
                </div>
              ))}
            </div>
          </Card>

          {/* Chart */}
          {stockData.chart_1h?.close?.length > 1 && (
            <Card T={T} style={{ marginBottom: 12 }}>
              <SLabel T={T}>Price Chart · Last 1 Hour (hover for OHLC)</SLabel>
              <CandlestickChart chartData={stockData.chart_1h} T={T} />
            </Card>
          )}

          {/* Technical + Fundamental */}
          <div className="two-col" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
            <Card T={T}>
              <SLabel T={T}>Technical Analysis</SLabel>
              <DataRow T={T} label="RSI" value={`${fmt(stockData.rsi)} · ${stockData.rsi_signal || "—"}`} color={parseFloat(stockData.rsi) < 30 ? T.green : parseFloat(stockData.rsi) > 70 ? T.red : T.text} />
              <DataRow T={T} label="MACD signal" value={stockData.macd_signal} color={stockData.macd_signal?.includes("Bull") ? T.green : T.red} />
              <DataRow T={T} label="MA 50" value={fmt(stockData.ma50)} />
              <DataRow T={T} label="MA 200" value={fmt(stockData.ma200)} />
              <DataRow T={T} label="Support" value={fmt(stockData.support)} color={T.green} />
              <DataRow T={T} label="Resistance" value={fmt(stockData.resistance)} color={T.red} />
              <DataRow T={T} label="Bollinger upper" value={fmt(stockData.bb_upper)} />
              <DataRow T={T} label="Bollinger lower" value={fmt(stockData.bb_lower)} />
            </Card>
            <Card T={T}>
              <SLabel T={T}>Fundamental Analysis</SLabel>
              <DataRow T={T} label="P/E ratio" value={fmt(stockData.pe_ratio)} />
              <DataRow T={T} label="EPS" value={fmt(stockData.eps)} />
              <DataRow T={T} label="Revenue" value={stockData.revenue && stockData.revenue !== "N/A" ? "₹" + (stockData.revenue / 1e12).toFixed(2) + "T" : "—"} />
              <DataRow T={T} label="Profit margin" value={stockData.profit_margin && stockData.profit_margin !== "N/A" ? (stockData.profit_margin * 100).toFixed(2) + "%" : "—"} />
              <DataRow T={T} label="ROE" value={stockData.roe && stockData.roe !== "N/A" ? (stockData.roe * 100).toFixed(2) + "%" : "—"} />
              <DataRow T={T} label="Debt / equity" value={fmt(stockData.debt_to_equity)} />
              <DataRow T={T} label="Dividend yield" value={stockData.dividend_yield && stockData.dividend_yield !== "N/A" ? stockData.dividend_yield + "%" : "—"} />
              <DataRow T={T} label="Market cap" value={stockData.market_cap ? (stockData.market_cap / 1e12).toFixed(2) + "T" : "—"} />
            </Card>
          </div>

          {/* AI Report */}
          {stockReport && (
            <Card T={T} style={{ padding: 0, overflow: "hidden" }}>
              <div style={{ padding: "10px 16px", background: T.bgSub, borderBottom: `1px solid ${T.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 11, fontWeight: 600, color: T.textSub, textTransform: "uppercase", letterSpacing: "1px" }}>🤖 AI Analysis Report</span>
                {vColors && <span style={{ fontSize: 12, fontWeight: 600, padding: "3px 14px", borderRadius: 20, color: vColors.color, background: vColors.bg, border: `1px solid ${vColors.border}` }}>{verdict.text}</span>}
              </div>
              <div style={{ padding: "16px 18px" }}>
                <pre style={{ whiteSpace: "pre-wrap", fontSize: 13, lineHeight: 1.85, color: T.text, fontFamily: "inherit" }}>{stockReport}</pre>
              </div>
            </Card>
          )}
        </div>
      )}

      {!stockData && !stockLoading && !stockError && (
        <div style={{ textAlign: "center", padding: "60px 20px", color: T.textTer }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>📊</div>
          <div style={{ fontSize: 14, fontWeight: 500, color: T.textSub, marginBottom: 6 }}>Search for any asset above</div>
          <div style={{ fontSize: 12 }}>Stocks · Crypto · Forex · Commodities · Indices</div>
        </div>
      )}
    </div>
  )
}

// ─── TAX PAGE ─────────────────────────────────────────────────────
function TaxPage({ taxForm, setTaxForm, taxResult, taxLoading, calculateTax, T }) {
  const fields = [
    { key: "annual_salary",   label: "Annual salary",          placeholder: "e.g. 800000", help: "Total gross CTC per year" },
    { key: "investments_80c", label: "80C investments",        placeholder: "e.g. 150000", help: "PPF, ELSS, LIC — max ₹1,50,000" },
    { key: "insurance_80d",   label: "Health insurance (80D)", placeholder: "e.g. 25000",  help: "Medical premium — max ₹25,000" },
    { key: "hra",             label: "HRA exemption",          placeholder: "e.g. 120000", help: "If HRA received from employer" },
  ]
  return (
    <div className="fade-in" style={{ maxWidth: 680, margin: "0 auto", padding: "20px 20px 80px" }}>
      <div style={{ marginBottom: 18 }}>
        <h2 style={{ fontSize: 20, fontWeight: 500, color: T.text, marginBottom: 4 }}>Tax Calculator 2024-25</h2>
        <p style={{ fontSize: 13, color: T.textSub }}>Old vs New regime — find which saves you more money.</p>
      </div>
      <Card T={T} style={{ marginBottom: 16 }}>
        <SLabel T={T}>Your details</SLabel>
        <div className="two-col" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 16 }}>
          {fields.map(f => (
            <div key={f.key}>
              <label style={{ display: "block", fontSize: 12, fontWeight: 500, color: T.textSub, marginBottom: 6 }}>{f.label} (₹)</label>
              <FInput T={T} type="number" value={taxForm[f.key]} onChange={e => setTaxForm(p => ({ ...p, [f.key]: e.target.value }))} placeholder={f.placeholder} />
              <div style={{ fontSize: 11, color: T.textTer, marginTop: 4 }}>{f.help}</div>
            </div>
          ))}
        </div>
        <Btn onClick={calculateTax} loading={taxLoading} full T={T} style={{ padding: 12, borderRadius: 8 }}>Calculate Tax →</Btn>
      </Card>

      {taxResult && (
        <div className="fade-up">
          <div style={{ background: T.greenBg, border: `1px solid ${T.greenBd}`, borderRadius: 12, padding: "18px 20px", marginBottom: 14, textAlign: "center" }}>
            <div style={{ fontSize: 11, color: T.green, fontWeight: 600, textTransform: "uppercase", letterSpacing: "1px", marginBottom: 6 }}>Best option for you</div>
            <div style={{ fontSize: 24, fontWeight: 600, color: T.text, marginBottom: 6 }}>{taxResult.better_regime} ✅</div>
            <div style={{ fontSize: 13, color: T.textSub }}>You save <strong style={{ color: T.green, fontSize: 16 }}>₹{taxResult.you_save?.toLocaleString()}</strong> per year</div>
          </div>
          <div className="two-col" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
            {[{ label: "Old Regime", val: taxResult.old_regime_tax, monthly: taxResult.monthly_old, c: T.amber, better: taxResult.better_regime?.toLowerCase().includes("old") }, { label: "New Regime", val: taxResult.new_regime_tax, monthly: taxResult.monthly_new, c: T.green, better: taxResult.better_regime?.toLowerCase().includes("new") }].map((r, i) => (
              <Card key={i} T={T} style={{ textAlign: "center", border: r.better ? `2px solid ${T.green}` : `1px solid ${T.border}` }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: r.c, textTransform: "uppercase", letterSpacing: "1px", marginBottom: 8 }}>{r.label}</div>
                <div style={{ fontSize: 24, fontWeight: 600, color: T.text, fontFamily: T.mono }}>₹{r.val?.toLocaleString()}</div>
                <div style={{ fontSize: 12, color: T.textSub, marginTop: 4 }}>₹{r.monthly?.toLocaleString()}/month</div>
              </Card>
            ))}
          </div>
          <Card T={T} style={{ marginBottom: 12 }}>
            <SLabel T={T}>Breakdown</SLabel>
            <DataRow T={T} label="Annual salary" value={`₹${taxResult.annual_salary?.toLocaleString()}`} />
            <DataRow T={T} label="Total deductions" value={`₹${taxResult.deductions_used?.toLocaleString()}`} />
            <DataRow T={T} label="Effective tax rate" value={`${taxResult.effective_rate}%`} />
          </Card>
          <Card T={T}>
            <SLabel T={T}>💡 Tax saving tips</SLabel>
            {taxResult.suggestions?.map((s, i) => (
              <div key={i} style={{ padding: "8px 0", borderBottom: i < taxResult.suggestions.length - 1 ? `1px solid ${T.border}` : "none", fontSize: 13, color: T.text, lineHeight: 1.6, display: "flex", gap: 8 }}>
                <span style={{ color: T.accent, flexShrink: 0 }}>→</span> {s}
              </div>
            ))}
          </Card>
        </div>
      )}
    </div>
  )
}

// ─── SIP PAGE ─────────────────────────────────────────────────────
function SipPage({ sipMode, setSipMode, sipForm, setSipForm, sipResult, sipLoading, calculateSip, T }) {
  const calcFields = [
    { key: "monthly_investment", label: "Monthly SIP", suffix: "₹", min: 500,   max: 100000, step: 500,  fmt: v => `₹${parseInt(v || 0).toLocaleString("en-IN")}` },
    { key: "annual_return",      label: "Expected returns", suffix: "%", min: 1, max: 30,     step: 0.5, fmt: v => `${v}%` },
    { key: "years",              label: "Time period", suffix: "yrs", min: 1, max: 40,     step: 1,   fmt: v => `${v} years` },
  ]
  const goalFields = [
    { key: "target_amount", label: "Target amount", suffix: "₹", min: 10000, max: 10000000, step: 10000, fmt: v => `₹${parseInt(v || 0).toLocaleString("en-IN")}` },
    { key: "goal_return",   label: "Expected returns", suffix: "%", min: 1, max: 30, step: 0.5, fmt: v => `${v}%` },
    { key: "goal_years",    label: "Time period", suffix: "yrs", min: 1, max: 40, step: 1, fmt: v => `${v} years` },
  ]
  const fields = sipMode === "calculate" ? calcFields : goalFields

  const DonutChart = ({ invested, returns }) => {
    const total = (invested || 0) + (returns || 0); if (!total) return null
    const r = 46, cx = 58, cy = 58, circ = 2 * Math.PI * r
    const dash = circ * (invested / total)
    return (
      <svg width={116} height={116} viewBox="0 0 116 116">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={T.bgTer} strokeWidth={13} />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={T.green} strokeWidth={13}
          strokeDasharray={`${circ - dash} ${dash}`} strokeLinecap="butt"
          transform={`rotate(-90 ${cx} ${cy})`} />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={T.accent} strokeWidth={13}
          strokeDasharray={`${dash} ${circ - dash}`} strokeLinecap="butt"
          transform={`rotate(-90 ${cx} ${cy})`} />
        <text x={cx} y={cy - 5} textAnchor="middle" fontSize={9} fill={T.textTer} fontFamily="Inter,sans-serif">returns</text>
        <text x={cx} y={cy + 10} textAnchor="middle" fontSize={13} fontWeight={600} fill={T.green} fontFamily="JetBrains Mono,monospace">
          {Math.round((returns / total) * 100)}%
        </text>
      </svg>
    )
  }

  return (
    <div className="fade-in" style={{ maxWidth: 680, margin: "0 auto", padding: "20px 20px 80px" }}>
      <div style={{ marginBottom: 18 }}>
        <h2 style={{ fontSize: 20, fontWeight: 500, color: T.text, marginBottom: 4 }}>SIP Calculator</h2>
        <p style={{ fontSize: 13, color: T.textSub }}>Calculate returns or find the monthly SIP needed for your goal.</p>
      </div>

      <div style={{ display: "flex", background: T.bgSub, borderRadius: 10, padding: 3, marginBottom: 18, border: `1px solid ${T.border}` }}>
        {[["calculate", "📊 Calculate Returns"], ["goal", "🎯 Goal Planning"]].map(([m, label]) => (
          <button key={m} onClick={() => setSipMode(m)}
            style={{ flex: 1, padding: "9px 16px", borderRadius: 8, fontSize: 13, fontWeight: 500, background: sipMode === m ? T.bg : "transparent", color: sipMode === m ? T.text : T.textSub, border: sipMode === m ? `1px solid ${T.border}` : "none", transition: "all 0.15s", boxShadow: sipMode === m ? T.shadow : "none" }}>
            {label}
          </button>
        ))}
      </div>

      <Card T={T} style={{ marginBottom: 16 }}>
        <SLabel T={T}>{sipMode === "calculate" ? "SIP details" : "Goal details"}</SLabel>
        <div style={{ display: "flex", flexDirection: "column", gap: 18, marginBottom: 18 }}>
          {fields.map(f => (
            <div key={f.key}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <label style={{ fontSize: 12, fontWeight: 500, color: T.textSub }}>{f.label}</label>
                <span style={{ fontSize: 14, fontWeight: 600, color: T.text, fontFamily: T.mono }}>{f.fmt(sipForm[f.key])}</span>
              </div>
              <input type="range" min={f.min} max={f.max} step={f.step} value={sipForm[f.key] || f.min}
                onChange={e => setSipForm(p => ({ ...p, [f.key]: e.target.value }))}
                style={{ width: "100%", accentColor: T.accent, height: 4 }}
              />
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 3 }}>
                <span style={{ fontSize: 10, color: T.textTer }}>{f.suffix === "₹" ? `₹${f.min.toLocaleString()}` : `${f.min}${f.suffix}`}</span>
                <span style={{ fontSize: 10, color: T.textTer }}>{f.suffix === "₹" ? `₹${f.max.toLocaleString()}` : `${f.max}${f.suffix}`}</span>
              </div>
            </div>
          ))}
        </div>
        <Btn onClick={calculateSip} loading={sipLoading} full T={T} style={{ padding: 12, borderRadius: 8 }}>
          {sipMode === "calculate" ? "Calculate Returns →" : "Calculate Monthly SIP →"}
        </Btn>
      </Card>

      {sipResult?.mode === "calculate" && (
        <div className="fade-up">
          <Card T={T} style={{ marginBottom: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 20, flexWrap: "wrap" }}>
              <DonutChart invested={sipResult.result.total_invested} returns={sipResult.result.total_returns} />
              <div style={{ flex: 1, minWidth: 180 }}>
                <div className="three-col" style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
                  {[["Invested", `₹${sipResult.result.total_invested?.toLocaleString()}`, T.textSub], ["Future value", `₹${sipResult.result.future_value?.toLocaleString()}`, T.accent], ["Returns", `₹${sipResult.result.total_returns?.toLocaleString()}`, T.green], ["Wealth gained", `${sipResult.result.wealth_gained}%`, T.green], ["Period", `${sipResult.result.years} yrs`, T.text], ["Monthly end", `₹${sipResult.result.monthly_at_maturity?.toLocaleString()}`, T.accent]].map(([l, v, c], i) => (
                    <div key={i} style={{ background: T.bgSub, borderRadius: 8, padding: "9px 10px" }}>
                      <div style={{ fontSize: 10, color: T.textTer, marginBottom: 3 }}>{l}</div>
                      <div style={{ fontSize: 12, fontWeight: 600, color: c, fontFamily: T.mono }}>{v}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
          {sipResult.suggestions?.length > 0 && (
            <Card T={T}>
              <SLabel T={T}>💡 Fund recommendations</SLabel>
              {sipResult.suggestions.map((s, i) => (
                <div key={i} style={{ padding: "8px 0", borderBottom: i < sipResult.suggestions.length - 1 ? `1px solid ${T.border}` : "none", fontSize: 13, color: T.text, lineHeight: 1.6, display: "flex", gap: 8 }}>
                  <span style={{ color: T.accent, flexShrink: 0 }}>→</span> {s}
                </div>
              ))}
            </Card>
          )}
        </div>
      )}

      {sipResult?.mode === "goal" && (
        <div className="fade-up">
          <Card T={T} style={{ textAlign: "center", padding: "32px 20px" }}>
            <div style={{ fontSize: 12, color: T.textSub, marginBottom: 8 }}>Monthly SIP needed to reach your goal</div>
            <div style={{ fontSize: 40, fontWeight: 600, color: T.accent, fontFamily: T.mono, marginBottom: 6 }}>₹{sipResult.monthly_required?.toLocaleString()}</div>
            <div style={{ fontSize: 13, color: T.textSub }}>per month 🎯</div>
          </Card>
        </div>
      )}
    </div>
  )
}


// ─── WATCHLIST SECTION (used in HomePage) ────────────────────────
function WatchlistSection({ watchlist, setWatchlist, analyzeStock, setTab, T }) {
  const [prices, setPrices] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!watchlist.length) return
    const fetchPrices = async () => {
      setLoading(true)
      try {
        const r = await axios.post(`${API}/watchlist/prices`, { symbols: watchlist.map(w => w.symbol) })
        const map = {}
        r.data.data.forEach(d => { map[d.symbol] = d })
        setPrices(map)
      } catch {} finally { setLoading(false) }
    }
    fetchPrices()
    const iv = setInterval(fetchPrices, 60000)
    return () => clearInterval(iv)
  }, [watchlist])

  const remove = (sym) => setWatchlist(prev => prev.filter(w => w.symbol !== sym))

  if (!watchlist.length) return null

  return (
    <div style={{ marginTop: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <div style={{ fontSize: 13, fontWeight: 500, color: T.text }}>⭐ Watchlist</div>
        <span style={{ fontSize: 11, color: T.textTer }}>{watchlist.length} stocks · auto-refresh 60s</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {watchlist.map((w, i) => {
          const p = prices[w.symbol]
          const isUp = p && p.change >= 0
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px", background: T.bg, border: `1px solid ${T.border}`, borderRadius: 10, transition: "border-color 0.15s" }}
              onMouseEnter={e => e.currentTarget.style.borderColor = T.borderEm}
              onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer" }}
                onClick={() => { setTab("stocks"); setTimeout(() => analyzeStock(w.symbol), 100) }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: T.accentBg, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, color: T.accent }}>
                  {w.name?.charAt(0) || w.symbol?.charAt(0)}
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: T.text }}>{w.name || w.symbol}</div>
                  <div style={{ fontSize: 11, color: T.textTer }}>{w.symbol}</div>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                {p ? (
                  <>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: 13, fontWeight: 600, color: T.text, fontFamily: T.mono }}>{p.currency === "USD" ? "$" : "₹"}{p.price?.toLocaleString("en-IN") || "—"}</div>
                      <div style={{ fontSize: 11, fontWeight: 500, color: isUp ? T.green : T.red }}>{isUp ? "▲" : "▼"} {Math.abs(p.change).toFixed(2)}%</div>
                    </div>
                  </>
                ) : loading ? (
                  <div style={{ fontSize: 11, color: T.textTer }}>Loading...</div>
                ) : null}
                <button onClick={() => remove(w.symbol)} style={{ fontSize: 16, color: T.textTer, padding: 2, lineHeight: 1, transition: "color 0.15s" }}
                  onMouseEnter={e => e.currentTarget.style.color = T.red}
                  onMouseLeave={e => e.currentTarget.style.color = T.textTer}>✕</button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── NEWS PAGE ────────────────────────────────────────────────────
function NewsPage({ T }) {
  const [query, setQuery] = useState("")
  const [inputVal, setInputVal] = useState("")
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const trendingTopics = ["RELIANCE.NS", "TCS.NS", "NIFTY", "BTC-USD", "INFY.NS", "HDFCBANK.NS"]

  const fetchNews = async (sym) => {
    const s = sym || query; if (!s.trim()) return
    setQuery(s); setLoading(true); setArticles([]); setError("")
    try {
      const r = await axios.get(`${API}/news/${encodeURIComponent(s)}`)
      if (r.data.articles.length === 0) setError("No news found for this symbol. Try a different one.")
      setArticles(r.data.articles)
    } catch { setError("News fetch karne mein error aaya. Backend check karo.") }
    finally { setLoading(false) }
  }

  const sentimentStyle = (s) => ({
    "Positive": { color: T.green, bg: T.greenBg, border: T.greenBd },
    "Negative": { color: T.red,   bg: T.redBg,   border: T.redBd },
    "Neutral" : { color: T.amber, bg: T.amberBg,  border: T.amberBd },
  }[s] || { color: T.textSub, bg: T.bgSub, border: T.border })

  return (
    <div className="fade-in" style={{ maxWidth: 780, margin: "0 auto", padding: "20px 20px 80px" }}>
      <div style={{ marginBottom: 18 }}>
        <h2 style={{ fontSize: 20, fontWeight: 500, color: T.text, marginBottom: 4 }}>📰 Market News</h2>
        <p style={{ fontSize: 13, color: T.textSub }}>Kisi bhi stock ya index ki latest news — AI Hinglish summary ke saath.</p>
      </div>

      {/* Search */}
      <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
        <input value={inputVal} onChange={e => setInputVal(e.target.value)}
          onKeyDown={e => e.key === "Enter" && fetchNews(inputVal)}
          placeholder="Stock symbol ya naam — e.g. RELIANCE.NS, TCS, BTC-USD..."
          style={{ flex: 1, padding: "11px 16px", fontSize: 13, border: `1px solid ${T.borderEm}`, borderRadius: 10, background: T.bg, color: T.text, outline: "none", transition: "border-color 0.15s, box-shadow 0.15s" }}
          onFocus={e => { e.target.style.borderColor = T.accent; e.target.style.boxShadow = `0 0 0 3px ${T.accent}22` }}
          onBlur={e => { e.target.style.borderColor = T.borderEm; e.target.style.boxShadow = "none" }}
        />
        <button onClick={() => fetchNews(inputVal)}
          style={{ padding: "11px 20px", background: loading ? T.textTer : T.accent, color: "#fff", borderRadius: 10, fontSize: 13, fontWeight: 500, transition: "background 0.15s" }}>
          {loading ? "..." : "Get News →"}
        </button>
      </div>

      {/* Trending chips */}
      <div style={{ display: "flex", gap: 6, marginBottom: 20, flexWrap: "wrap" }}>
        <span style={{ fontSize: 11, color: T.textTer, alignSelf: "center" }}>Trending:</span>
        {trendingTopics.map((t_, i) => (
          <button key={i} onClick={() => { setInputVal(t_); fetchNews(t_) }}
            style={{ padding: "4px 12px", border: `1px solid ${T.border}`, borderRadius: 16, fontSize: 11, color: T.textSub, background: T.bg, transition: "all 0.15s", cursor: "pointer" }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = T.accent; e.currentTarget.style.color = T.accent }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.color = T.textSub }}>
            {t_}
          </button>
        ))}
      </div>

      {error && (
        <div style={{ background: T.redBg, border: `1px solid ${T.redBd}`, borderRadius: 10, padding: "12px 16px", color: T.red, marginBottom: 16, fontSize: 13 }}>❌ {error}</div>
      )}

      {/* Loading skeletons */}
      {loading && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {[1,2,3,4].map(i => (
            <div key={i} style={{ background: T.bg, border: `1px solid ${T.border}`, borderRadius: 12, padding: "16px 18px" }}>
              <div style={{ height: 14, background: `linear-gradient(90deg, ${T.skeletonA} 25%, ${T.skeletonB} 50%, ${T.skeletonA} 75%)`, backgroundSize: "600px 100%", animation: "shimmer 1.4s ease infinite", borderRadius: 6, marginBottom: 10, width: "80%" }} />
              <div style={{ height: 11, background: `linear-gradient(90deg, ${T.skeletonA} 25%, ${T.skeletonB} 50%, ${T.skeletonA} 75%)`, backgroundSize: "600px 100%", animation: "shimmer 1.4s ease infinite", borderRadius: 6, width: "50%" }} />
            </div>
          ))}
          <div style={{ textAlign: "center", fontSize: 12, color: T.textSub, marginTop: 4 }}>AI Hinglish summaries generate ho rahi hain...</div>
        </div>
      )}

      {/* Articles */}
      {!loading && articles.length > 0 && (
        <div className="fade-up" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{ fontSize: 12, color: T.textSub, marginBottom: 4 }}>
            {articles.length} articles found for <strong style={{ color: T.text }}>{query}</strong>
          </div>
          {articles.map((art, i) => {
            const sc = sentimentStyle(art.sentiment)
            return (
              <a key={i} href={art.link} target="_blank" rel="noopener noreferrer" style={{ textDecoration: "none" }}>
                <div style={{ background: T.bg, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px", transition: "border-color 0.15s, box-shadow 0.15s", cursor: "pointer" }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = T.borderEm; e.currentTarget.style.boxShadow = T.shadow }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.boxShadow = "none" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 10, marginBottom: 8 }}>
                    <div style={{ fontSize: 13, fontWeight: 500, color: T.text, lineHeight: 1.5, flex: 1 }}>{art.title}</div>
                    <span style={{ fontSize: 10, fontWeight: 600, padding: "3px 9px", borderRadius: 16, flexShrink: 0, color: sc.color, background: sc.bg, border: `1px solid ${sc.border}` }}>
                      {art.sentiment === "Positive" ? "📈" : art.sentiment === "Negative" ? "📉" : "➖"} {art.sentiment}
                    </span>
                  </div>
                  <div style={{ fontSize: 12, color: T.accent, lineHeight: 1.5, marginBottom: 8, padding: "6px 10px", background: T.accentBg, borderRadius: 7, borderLeft: `3px solid ${T.accent}` }}>
                    🤖 {art.ai_summary}
                  </div>
                  <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                    <span style={{ fontSize: 10, color: T.textTer }}>{art.source}</span>
                    <span style={{ fontSize: 10, color: T.textTer }}>·</span>
                    <span style={{ fontSize: 10, color: T.textTer }}>{art.pub}</span>
                    <span style={{ fontSize: 10, color: T.accent, marginLeft: "auto" }}>Read full →</span>
                  </div>
                </div>
              </a>
            )
          })}
        </div>
      )}

      {!loading && !articles.length && !error && (
        <div style={{ textAlign: "center", padding: "60px 20px", color: T.textTer }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>📰</div>
          <div style={{ fontSize: 14, fontWeight: 500, color: T.textSub, marginBottom: 6 }}>Search karo ya trending topic choose karo</div>
          <div style={{ fontSize: 12 }}>AI Hinglish summary + sentiment analysis milega</div>
        </div>
      )}
    </div>
  )
}

// ─── COMPARE PAGE ─────────────────────────────────────────────────
function ComparePage({ T, analyzeStock, setTab }) {
  const [sym1, setSym1] = useState("")
  const [sym2, setSym2] = useState("")
  const [sug1, setSug1] = useState([])
  const [sug2, setSug2] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  // Autocomplete for sym1
  useEffect(() => {
    if (sym1.length < 2) { setSug1([]); return }
    const t = setTimeout(async () => {
      try { const r = await axios.get(`${API}/search/${sym1}`); setSug1(r.data.results.slice(0,5)) } catch {}
    }, 300)
    return () => clearTimeout(t)
  }, [sym1])

  // Autocomplete for sym2
  useEffect(() => {
    if (sym2.length < 2) { setSug2([]); return }
    const t = setTimeout(async () => {
      try { const r = await axios.get(`${API}/search/${sym2}`); setSug2(r.data.results.slice(0,5)) } catch {}
    }, 300)
    return () => clearTimeout(t)
  }, [sym2])

  const compare = async () => {
    if (!sym1.trim() || !sym2.trim()) return
    setLoading(true); setResult(null); setError("")
    try {
      const r = await axios.get(`${API}/compare/${encodeURIComponent(sym1)}/${encodeURIComponent(sym2)}`)
      setResult(r.data)
    } catch { setError("Comparison failed. Symbols check karo.") }
    finally { setLoading(false) }
  }

  const presets = [["TCS.NS", "INFY.NS"], ["RELIANCE.NS", "HDFCBANK.NS"], ["BTC-USD", "ETH-USD"], ["AAPL", "MSFT"]]

  const MetricRow = ({ label, v1, v2, higherIsBetter = true, T }) => {
    const n1 = parseFloat(v1), n2 = parseFloat(v2)
    const valid = !isNaN(n1) && !isNaN(n2)
    const w1 = valid && (higherIsBetter ? n1 > n2 : n1 < n2)
    const w2 = valid && (higherIsBetter ? n2 > n1 : n2 < n1)
    return (
      <div style={{ display: "grid", gridTemplateColumns: "1fr 120px 1fr", gap: 8, padding: "8px 0", borderBottom: `1px solid ${T.border}`, alignItems: "center" }}>
        <div style={{ fontSize: 12, fontWeight: w1 ? 600 : 400, color: w1 ? T.green : T.text, fontFamily: T.mono, textAlign: "right" }}>
          {v1 || "—"}{w1 && " ✓"}
        </div>
        <div style={{ fontSize: 11, color: T.textTer, textAlign: "center" }}>{label}</div>
        <div style={{ fontSize: 12, fontWeight: w2 ? 600 : 400, color: w2 ? T.green : T.text, fontFamily: T.mono }}>
          {w2 && "✓ "}{v2 || "—"}
        </div>
      </div>
    )
  }

  const d1 = result?.sym1?.data
  const d2 = result?.sym2?.data

  return (
    <div className="fade-in" style={{ maxWidth: 900, margin: "0 auto", padding: "20px 20px 80px" }}>
      <div style={{ marginBottom: 18 }}>
        <h2 style={{ fontSize: 20, fontWeight: 500, color: T.text, marginBottom: 4 }}>⚖️ Stock Comparison</h2>
        <p style={{ fontSize: 13, color: T.textSub }}>Do stocks side-by-side compare karo — technical, fundamental aur AI verdict.</p>
      </div>

      {/* Preset pairs */}
      <div style={{ display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap" }}>
        <span style={{ fontSize: 11, color: T.textTer, alignSelf: "center" }}>Quick compare:</span>
        {presets.map(([a, b], i) => (
          <button key={i} onClick={() => { setSym1(a); setSym2(b); setSug1([]); setSug2([]) }}
            style={{ padding: "4px 12px", border: `1px solid ${T.border}`, borderRadius: 16, fontSize: 11, color: T.textSub, background: T.bg, cursor: "pointer", transition: "all 0.15s" }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = T.accent; e.currentTarget.style.color = T.accent }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.color = T.textSub }}>
            {a.replace(".NS","").replace("-USD","")} vs {b.replace(".NS","").replace("-USD","")}
          </button>
        ))}
      </div>

      {/* Search inputs */}
      <div className="two-col" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
        {[
          { val: sym1, setVal: setSym1, sug: sug1, setSug: setSug1, placeholder: "Stock 1 — e.g. TCS.NS" },
          { val: sym2, setVal: setSym2, sug: sug2, setSug: setSug2, placeholder: "Stock 2 — e.g. INFY.NS" },
        ].map((field, idx) => (
          <div key={idx} style={{ position: "relative" }}>
            <input value={field.val} onChange={e => field.setVal(e.target.value)}
              onKeyDown={e => e.key === "Enter" && compare()}
              placeholder={field.placeholder}
              style={{ width: "100%", padding: "11px 16px", fontSize: 13, border: `1px solid ${T.borderEm}`, borderRadius: 10, background: T.bg, color: T.text, outline: "none", transition: "border-color 0.15s, box-shadow 0.15s" }}
              onFocus={e => { e.target.style.borderColor = T.accent; e.target.style.boxShadow = `0 0 0 3px ${T.accent}22` }}
              onBlur={e => { e.target.style.borderColor = T.borderEm; e.target.style.boxShadow = "none" }}
            />
            {field.sug.length > 0 && (
              <div style={{ position: "absolute", top: "100%", left: 0, right: 0, marginTop: 4, background: T.bg, border: `1px solid ${T.borderEm}`, borderRadius: 10, boxShadow: T.shadow, zIndex: 200, overflow: "hidden" }}>
                {field.sug.map((s, i) => (
                  <div key={i} onClick={() => { field.setVal(s.symbol); field.setSug([]) }}
                    style={{ padding: "9px 14px", cursor: "pointer", fontSize: 12, color: T.text, borderBottom: i < field.sug.length - 1 ? `1px solid ${T.border}` : "none", transition: "background 0.1s", display: "flex", justifyContent: "space-between" }}
                    onMouseEnter={e => e.currentTarget.style.background = T.bgSub}
                    onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                    <span>{s.name}</span>
                    <span style={{ fontSize: 10, color: T.textTer }}>{s.symbol}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <button onClick={compare} disabled={loading || !sym1 || !sym2}
        style={{ width: "100%", padding: 12, background: loading || !sym1 || !sym2 ? T.textTer : T.accent, color: "#fff", borderRadius: 10, fontSize: 14, fontWeight: 500, marginBottom: 20, transition: "background 0.15s" }}>
        {loading ? "Comparing... (30-40s)" : "⚖️ Compare Now →"}
      </button>

      {error && (
        <div style={{ background: T.redBg, border: `1px solid ${T.redBd}`, borderRadius: 10, padding: "12px 16px", color: T.red, marginBottom: 16, fontSize: 13 }}>❌ {error}</div>
      )}

      {loading && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            {[0,1].map(i => <div key={i} style={{ height: 120, background: `linear-gradient(90deg, ${T.skeletonA} 25%, ${T.skeletonB} 50%, ${T.skeletonA} 75%)`, backgroundSize: "600px 100%", animation: "shimmer 1.4s ease infinite", borderRadius: 12 }} />)}
          </div>
          <div style={{ height: 200, background: `linear-gradient(90deg, ${T.skeletonA} 25%, ${T.skeletonB} 50%, ${T.skeletonA} 75%)`, backgroundSize: "600px 100%", animation: "shimmer 1.4s ease infinite", borderRadius: 12 }} />
          <div style={{ textAlign: "center", fontSize: 12, color: T.textSub }}>Dono stocks ka data fetch ho raha hai + AI comparison...</div>
        </div>
      )}

      {result && d1 && d2 && (
        <div className="fade-up">
          {/* Price headers side by side */}
          <div className="two-col" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 12 }}>
            {[
              { data: d1, raw: sym1, isWinner: result.winner && d1.name && result.winner.toLowerCase().includes(d1.name.toLowerCase().split(" ")[0]) },
              { data: d2, raw: sym2, isWinner: result.winner && d2.name && result.winner.toLowerCase().includes(d2.name.toLowerCase().split(" ")[0]) },
            ].map(({ data: d, raw, isWinner }, idx) => {
              const verdict = getVerdict(isWinner ? "BUY" : "")
              return (
                <div key={idx} style={{ background: T.bg, border: `2px solid ${isWinner ? T.green : T.border}`, borderRadius: 12, padding: "14px 16px", position: "relative", transition: "border-color 0.3s" }}>
                  {isWinner && (
                    <div style={{ position: "absolute", top: -10, left: "50%", transform: "translateX(-50%)", background: T.green, color: "#fff", fontSize: 10, fontWeight: 700, padding: "2px 12px", borderRadius: 20 }}>
                      ✓ WINNER
                    </div>
                  )}
                  <div style={{ fontSize: 11, color: T.textTer, marginBottom: 4 }}>{raw}</div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: T.text, marginBottom: 6 }}>{d.name}</div>
                  <div style={{ fontSize: 22, fontWeight: 600, color: T.text, fontFamily: T.mono }}>{d.currency} {fmt(d.current_price)}</div>
                  <div style={{ fontSize: 12, color: clrVal(d.price_change_1d, T), marginTop: 2 }}>{pct(d.price_change_1d)} today</div>
                </div>
              )
            })}
          </div>

          {/* Metrics comparison table */}
          <div style={{ background: T.bg, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px", marginBottom: 12 }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 120px 1fr", gap: 8, padding: "0 0 10px", marginBottom: 6, borderBottom: `2px solid ${T.border}` }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: T.accent, textAlign: "right" }}>{d1.name?.split(" ")[0]}</div>
              <div style={{ fontSize: 11, color: T.textTer, textAlign: "center" }}>Metric</div>
              <div style={{ fontSize: 12, fontWeight: 600, color: T.accent }}>{d2.name?.split(" ")[0]}</div>
            </div>
            <MetricRow T={T} label="RSI" v1={d1.rsi?.toFixed(1)} v2={d2.rsi?.toFixed(1)} higherIsBetter={false} />
            <MetricRow T={T} label="1Y Return %" v1={d1.price_change_1y?.toFixed(2)} v2={d2.price_change_1y?.toFixed(2)} higherIsBetter={true} />
            <MetricRow T={T} label="1M Return %" v1={d1.price_change_1m?.toFixed(2)} v2={d2.price_change_1m?.toFixed(2)} higherIsBetter={true} />
            <MetricRow T={T} label="P/E Ratio" v1={fmt(d1.pe_ratio)} v2={fmt(d2.pe_ratio)} higherIsBetter={false} />
            <MetricRow T={T} label="MA50" v1={fmt(d1.ma50)} v2={fmt(d2.ma50)} higherIsBetter={true} />
            <MetricRow T={T} label="52W High" v1={fmt(d1["52w_high"])} v2={fmt(d2["52w_high"])} higherIsBetter={true} />
            <MetricRow T={T} label="MACD" v1={d1.macd_signal} v2={d2.macd_signal} higherIsBetter={true} />
            <MetricRow T={T} label="Trend" v1={d1.trend} v2={d2.trend} higherIsBetter={true} />
          </div>

          {/* AI Verdict */}
          <div style={{ background: T.bg, border: `1px solid ${T.border}`, borderRadius: 12, padding: 0, overflow: "hidden" }}>
            <div style={{ padding: "10px 16px", background: T.bgSub, borderBottom: `1px solid ${T.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 11, fontWeight: 600, color: T.textSub, textTransform: "uppercase", letterSpacing: "1px" }}>🤖 AI Comparison Verdict</span>
              {result.winner && <span style={{ fontSize: 11, fontWeight: 600, color: T.green, background: T.greenBg, border: `1px solid ${T.greenBd}`, padding: "3px 12px", borderRadius: 20 }}>Winner: {result.winner}</span>}
            </div>
            <div style={{ padding: "14px 16px" }}>
              <pre style={{ whiteSpace: "pre-wrap", fontSize: 13, lineHeight: 1.8, color: T.text, fontFamily: "inherit" }}>{result.verdict}</pre>
            </div>
            <div style={{ padding: "10px 16px", borderTop: `1px solid ${T.border}`, display: "flex", gap: 8 }}>
              <button onClick={() => { setTab("stocks"); setTimeout(() => analyzeStock(sym1), 100) }}
                style={{ flex: 1, padding: "9px", border: `1px solid ${T.border}`, borderRadius: 8, fontSize: 12, color: T.text, background: T.bgSub, cursor: "pointer", transition: "background 0.15s" }}
                onMouseEnter={e => e.currentTarget.style.background = T.bgTer}
                onMouseLeave={e => e.currentTarget.style.background = T.bgSub}>
                Full Analysis: {sym1.replace(".NS","").replace("-USD","")} →
              </button>
              <button onClick={() => { setTab("stocks"); setTimeout(() => analyzeStock(sym2), 100) }}
                style={{ flex: 1, padding: "9px", border: `1px solid ${T.border}`, borderRadius: 8, fontSize: 12, color: T.text, background: T.bgSub, cursor: "pointer", transition: "background 0.15s" }}
                onMouseEnter={e => e.currentTarget.style.background = T.bgTer}
                onMouseLeave={e => e.currentTarget.style.background = T.bgSub}>
                Full Analysis: {sym2.replace(".NS","").replace("-USD","")} →
              </button>
            </div>
          </div>
        </div>
      )}

      {!result && !loading && !error && (
        <div style={{ textAlign: "center", padding: "50px 20px", color: T.textTer }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>⚖️</div>
          <div style={{ fontSize: 14, fontWeight: 500, color: T.textSub, marginBottom: 6 }}>Do stocks select karo upar se</div>
          <div style={{ fontSize: 12 }}>Technical + Fundamental + AI verdict ek saath milega</div>
        </div>
      )}
    </div>
  )
}

// ─── ROOT APP ─────────────────────────────────────────────────────
export default function App() {
  // Dark mode
  const [darkMode, setDarkMode] = useState(() => {
    try { return localStorage.getItem("fm-dark") === "true" } catch { return false }
  })
  const T = THEMES[darkMode ? "dark" : "light"]

  useEffect(() => {
    document.body.style.background = T.bgSub
    document.body.style.color = T.text
    try { localStorage.setItem("fm-dark", darkMode) } catch {}
  }, [darkMode, T])

  // Risk profile
  const [riskProfile, setRiskProfile] = useState(() => {
    try { return localStorage.getItem("fm-risk") || null } catch { return null }
  })
  const [showRiskModal, setShowRiskModal] = useState(false)

  // Nav
  const [tab, setTab] = useState("home")
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Chat state
  const [messages, setMessages] = useState([{
    role: "bot",
    text: "Namaste! 💰 Main FinMate AI hun — aapka personal CA, broker, aur financial advisor.\n\nMujhe batao:\n• Koi stock analyze karna hai?\n• Tax planning chahiye?\n• SIP ya investment advice?\n\nMain specific numbers ke saath advice dunga — sirf theory nahi."
  }])
  const [input, setInput] = useState("")
  const [chatLoading, setChatLoading] = useState(false)
  const chatEndRef = useRef(null)
  const chatInputRef = useRef(null)

  // Stock state
  const [symbol, setSymbol] = useState("")
  const [suggestions, setSuggestions] = useState([])
  const [stockData, setStockData] = useState(null)
  const [stockReport, setStockReport] = useState("")
  const [stockLoading, setStockLoading] = useState(false)
  const [stockError, setStockError] = useState("")

  // Tax
  const [taxForm, setTaxForm] = useState({ annual_salary: "", investments_80c: "", insurance_80d: "", hra: "" })
  const [taxResult, setTaxResult] = useState(null)
  const [taxLoading, setTaxLoading] = useState(false)

  // SIP
  const [sipMode, setSipMode] = useState("calculate")
  const [sipForm, setSipForm] = useState({ monthly_investment: "5000", annual_return: "12", years: "10", target_amount: "1000000", goal_return: "12", goal_years: "10" })
  const [sipResult, setSipResult] = useState(null)
  const [sipLoading, setSipLoading] = useState(false)

  // Watchlist
  const [watchlist, setWatchlist] = useState(() => {
    try { return JSON.parse(localStorage.getItem("fm-watchlist") || "[]") } catch { return [] }
  })
  useEffect(() => {
    try { localStorage.setItem("fm-watchlist", JSON.stringify(watchlist)) } catch {}
  }, [watchlist])

  const addToWatchlist = (symbol, name) => {
    setWatchlist(prev => {
      if (prev.find(w => w.symbol === symbol)) return prev
      return [...prev, { symbol, name }]
    })
  }
  const isWatched = (symbol) => watchlist.some(w => w.symbol === symbol)

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }) }, [messages])

  // Autocomplete
  useEffect(() => {
    if (symbol.length < 2) { setSuggestions([]); return }
    const t = setTimeout(async () => {
      try { const r = await axios.get(`${API}/search/${symbol}`); setSuggestions(r.data.results) } catch { setSuggestions([]) }
    }, 300)
    return () => clearTimeout(t)
  }, [symbol])

  // Show risk modal if no profile set and user goes to chat
  useEffect(() => {
    if (tab === "chat" && !riskProfile) setShowRiskModal(true)
  }, [tab, riskProfile])

  const saveRisk = (r) => {
    setRiskProfile(r)
    try { localStorage.setItem("fm-risk", r) } catch {}
    setShowRiskModal(false)
  }

  // ── UPGRADED sendMessage — CA + Broker AI ──
  const sendMessage = async () => {
    if (!input.trim()) return
    const userMsg = input; setInput("")
    setMessages(p => [...p, { role: "user", text: userMsg }])
    setChatLoading(true)

    // Build stock context string if a stock was analyzed
    const stockContext = stockData ? `
LAST ANALYZED STOCK (use this data to answer stock-related questions):
Symbol: ${stockData.symbol}
Company: ${stockData.name}
Current Price: ${stockData.currency} ${stockData.current_price}
Sector: ${stockData.sector}
Change 1D: ${stockData.price_change_1d}%  | 1M: ${stockData.price_change_1m}%  | 1Y: ${stockData.price_change_1y}%
RSI: ${stockData.rsi} (${stockData.rsi_signal})
MACD: ${stockData.macd_signal}
MA50: ${stockData.ma50} | MA200: ${stockData.ma200}
Support: ${stockData.support} | Resistance: ${stockData.resistance}
Trend: ${stockData.trend}
P/E: ${stockData.pe_ratio} | EPS: ${stockData.eps}
Market Cap: ${stockData.market_cap}
AI Report Summary: ${stockReport ? stockReport.substring(0, 500) + "..." : "N/A"}
` : ""

    try {
      const r = await axios.post(`${API}/chat`, {
        message       : userMsg,
        extra_context : stockContext,
        risk_profile  : riskProfile || "moderate"
      })
      setMessages(p => [...p, { role: "bot", text: r.data.reply }])
    } catch {
      setMessages(p => [...p, { role: "bot", text: "Server se connection nahi ho pa raha. Backend check karo." }])
    } finally { setChatLoading(false) }
  }

  const analyzeStock = async (sym) => {
    const s = sym || symbol; if (!s.trim()) return
    setSymbol(s); setSuggestions([]); setStockLoading(true)
    setStockData(null); setStockReport(""); setStockError("")
    try {
      const r = await axios.get(`${API}/analyze/${s}`)
      setStockData(r.data.data); setStockReport(r.data.report)
    } catch { setStockError("Stock not found. Check the name or symbol and try again.") }
    finally { setStockLoading(false) }
  }

  const calculateTax = async () => {
    setTaxLoading(true); setTaxResult(null)
    try {
      const r = await axios.post(`${API}/tax`, { annual_salary: parseInt(taxForm.annual_salary) || 0, investments_80c: parseInt(taxForm.investments_80c) || 0, insurance_80d: parseInt(taxForm.insurance_80d) || 0, hra: parseInt(taxForm.hra) || 0 })
      setTaxResult(r.data.result)
    } catch { alert("Tax calculation error. Check backend.") }
    finally { setTaxLoading(false) }
  }

  const calculateSip = async () => {
    setSipLoading(true); setSipResult(null)
    try {
      const payload = sipMode === "calculate"
        ? { mode: "calculate", monthly_investment: parseInt(sipForm.monthly_investment) || 0, annual_return: parseFloat(sipForm.annual_return) || 12, years: parseInt(sipForm.years) || 10 }
        : { mode: "goal", target_amount: parseInt(sipForm.target_amount) || 0, annual_return: parseFloat(sipForm.goal_return) || 12, years: parseInt(sipForm.goal_years) || 10 }
      const r = await axios.post(`${API}/sip`, payload)
      setSipResult(r.data)
    } catch { alert("SIP calculation error.") }
    finally { setSipLoading(false) }
  }

  const tabs = [{ key: "home", label: "Home", icon: "🏠" }, { key: "chat", label: "AI Chat", icon: "💬" }, { key: "stocks", label: "Stocks", icon: "📊" }, { key: "news", label: "News", icon: "📰" }, { key: "compare", label: "Compare", icon: "⚖️" }, { key: "tax", label: "Tax", icon: "🧾" }, { key: "sip", label: "SIP", icon: "📈" }]

  return (
    <div style={{ background: T.bgSub, minHeight: "100vh", color: T.text, transition: "background 0.25s, color 0.25s" }}>

      {/* Risk modal */}
      {showRiskModal && <RiskModal onSave={saveRisk} T={T} />}

      {/* ── TOPBAR ── */}
      <div style={{ position: "sticky", top: 0, zIndex: 300, background: T.navBg, backdropFilter: "blur(12px)", borderBottom: `1px solid ${T.border}`, padding: "0 20px", height: 52, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, transition: "background 0.25s, border-color 0.25s" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
          <span style={{ fontSize: 20 }}>💰</span>
          <span style={{ fontSize: 15, fontWeight: 600, color: T.text }}>FinMate</span>
          <span style={{ fontSize: 15, fontWeight: 600, color: T.accent }}>AI</span>
          <span className="desktop-only" style={{ fontSize: 10, color: T.accent, background: T.accentBg, padding: "2px 8px", borderRadius: 20, fontWeight: 600, marginLeft: 2 }}>BETA</span>
        </div>

        <nav className="desktop-only" style={{ gap: 2 }}>
          {tabs.map(tab_ => (
            <button key={tab_.key} onClick={() => setTab(tab_.key)} style={{ padding: "6px 14px", borderRadius: 7, fontSize: 13, fontWeight: 500, background: tab === tab_.key ? T.bgTer : "transparent", color: tab === tab_.key ? T.text : T.textSub, border: `1px solid ${tab === tab_.key ? T.border : "transparent"}`, transition: "all 0.15s" }}>
              {tab_.icon} {tab_.label}
            </button>
          ))}
        </nav>

        {/* Right controls */}
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {/* Dark mode toggle */}
          <button onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            style={{ width: 36, height: 20, borderRadius: 12, background: darkMode ? T.accent : T.bgTer, border: `1px solid ${T.borderEm}`, position: "relative", transition: "background 0.25s", flexShrink: 0 }}>
            <span style={{ position: "absolute", top: 2, left: darkMode ? 17 : 2, width: 14, height: 14, borderRadius: "50%", background: darkMode ? "#fff" : T.textSub, transition: "left 0.2s", fontSize: 8, display: "flex", alignItems: "center", justifyContent: "center" }}>
              {darkMode ? "🌙" : "☀️"}
            </span>
          </button>

          {/* Risk profile button */}
          {riskProfile && (
            <button onClick={() => setShowRiskModal(true)} className="desktop-only"
              style={{ fontSize: 11, fontWeight: 600, padding: "4px 10px", borderRadius: 8, border: `1px solid ${T.border}`, color: T.textSub, background: T.bgSub, textTransform: "capitalize" }}>
              {riskProfile === "conservative" ? "🛡️" : riskProfile === "moderate" ? "⚖️" : "🚀"} {riskProfile}
            </button>
          )}

          {/* Mobile hamburger */}
          <button className="mobile-only" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} style={{ fontSize: 20, padding: 4, color: T.textSub }}>
            {mobileMenuOpen ? "✕" : "☰"}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="mobile-only fade-in" style={{ position: "fixed", top: 52, left: 0, right: 0, bottom: 0, background: T.bg, zIndex: 250, flexDirection: "column", padding: 16, gap: 4 }}>
          {tabs.map(tab_ => (
            <button key={tab_.key} onClick={() => { setTab(tab_.key); setMobileMenuOpen(false) }}
              style={{ display: "flex", alignItems: "center", gap: 12, padding: "14px 16px", borderRadius: 10, fontSize: 14, fontWeight: 500, background: tab === tab_.key ? T.accentBg : "transparent", color: tab === tab_.key ? T.accent : T.text, width: "100%", transition: "all 0.15s" }}>
              <span style={{ fontSize: 20 }}>{tab_.icon}</span> {tab_.label}
            </button>
          ))}
          <div style={{ marginTop: "auto", padding: "12px 0" }}>
            <button onClick={() => { setDarkMode(!darkMode); setMobileMenuOpen(false) }} style={{ display: "flex", alignItems: "center", gap: 10, padding: "12px 16px", borderRadius: 10, fontSize: 14, color: T.text, width: "100%" }}>
              <span style={{ fontSize: 20 }}>{darkMode ? "☀️" : "🌙"}</span> {darkMode ? "Light mode" : "Dark mode"}
            </button>
            <button onClick={() => { setShowRiskModal(true); setMobileMenuOpen(false) }} style={{ display: "flex", alignItems: "center", gap: 10, padding: "12px 16px", borderRadius: 10, fontSize: 14, color: T.text, width: "100%" }}>
              <span style={{ fontSize: 20 }}>📋</span> Risk Profile: <strong style={{ textTransform: "capitalize", marginLeft: 4 }}>{riskProfile || "not set"}</strong>
            </button>
          </div>
        </div>
      )}

      {/* ── TICKER ── */}
      <div style={{ background: T.bg, borderBottom: `1px solid ${T.border}`, padding: "8px 20px", overflow: "hidden", transition: "background 0.25s" }}>
        <MarketTicker T={T} />
      </div>

      {/* ── PAGES ── */}
      {tab === "home"   && <HomePage setTab={setTab} setInput={setInput} chatInputRef={chatInputRef} T={T} watchlist={watchlist} setWatchlist={setWatchlist} analyzeStock={analyzeStock} />}
      {tab === "chat"   && <ChatPage messages={messages} input={input} setInput={setInput} loading={chatLoading} sendMessage={sendMessage} chatEndRef={chatEndRef} chatInputRef={chatInputRef} lastStockData={stockData} lastStockReport={stockReport} riskProfile={riskProfile} T={T} />}
      {tab === "stocks" && <StocksPage symbol={symbol} setSymbol={setSymbol} suggestions={suggestions} stockData={stockData} stockReport={stockReport} stockLoading={stockLoading} stockError={stockError} analyzeStock={analyzeStock} T={T} addToWatchlist={addToWatchlist} isWatched={isWatched} />}
      {tab === "tax"    && <TaxPage taxForm={taxForm} setTaxForm={setTaxForm} taxResult={taxResult} taxLoading={taxLoading} calculateTax={calculateTax} T={T} />}
      {tab === "sip"     && <SipPage sipMode={sipMode} setSipMode={setSipMode} sipForm={sipForm} setSipForm={setSipForm} sipResult={sipResult} sipLoading={sipLoading} calculateSip={calculateSip} T={T} />}
      {tab === "news"    && <NewsPage T={T} />}
      {tab === "compare" && <ComparePage T={T} analyzeStock={analyzeStock} setTab={setTab} />}

      {/* ── BOTTOM NAV (mobile) ── */}
      <div className="mobile-only" style={{ position: "fixed", bottom: 0, left: 0, right: 0, background: T.navBg, backdropFilter: "blur(10px)", borderTop: `1px solid ${T.border}`, zIndex: 200 }}>
        {tabs.map(tab_ => (
          <button key={tab_.key} onClick={() => setTab(tab_.key)}
            style={{ flex: 1, padding: "10px 4px", display: "flex", flexDirection: "column", alignItems: "center", gap: 3, fontSize: 10, fontWeight: 500, color: tab === tab_.key ? T.accent : T.textTer, transition: "color 0.15s", minWidth: 0 }}>
            <span style={{ fontSize: 18 }}>{tab_.icon}</span>
            {tab_.label}
          </button>
        ))}
      </div>

      {/* ── FOOTER ── */}
      <div style={{ borderTop: `1px solid ${T.border}`, padding: "14px 20px", textAlign: "center", background: T.bg, marginBottom: 60, transition: "background 0.25s" }}>
        <p style={{ fontSize: 11, color: T.textTer, lineHeight: 1.8 }}>
          💰 FinMate AI · Built by Ajay Singh | SAU · Data via Yahoo Finance
        </p>
      </div>
    </div>
  )
}