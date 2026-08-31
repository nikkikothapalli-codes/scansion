import React, { useState, useEffect } from "react";

/**
 * Frontend for the scansion API.
 *
 * Falls back to bundled sample data when the API isn't reachable, so the page
 * demonstrates itself with the backend down.
 */

const API = "http://localhost:8000";

const C = {
  bg: "#F7F3E9",
  panel: "#FCFAF3",
  card: "#F4EFE3",
  ink: "#1C1A16",
  dim: "#6F675A",
  faint: "#9A9285",
  rule: "#DDD4C2",
  mark: "#8C3A32",
  gold: "#A8813C",
};

const SAMPLE = `Shall I compare thee to a summer's day?
Thou art more lovely and more temperate:
Rough winds do shake the darling buds of May,
And summer's lease hath all too short a date:`;

const FALLBACK = {
  dominant_meter: "iambic pentameter",
  rhyme_scheme: "ABAB",
  line_count: 4,
  meter_counts: { "iambic pentameter": 4 },
  lines: [
    { text: "Shall I compare thee to a summer's day?", meter: "iambic pentameter",
      confidence: 0.8, caesura: null,
      words: [
        { text: "shall", stress: "0", certain: true, demoted: false },
        { text: "i", stress: "1", certain: true, demoted: false },
        { text: "compare", stress: "01", certain: true, demoted: false },
        { text: "thee", stress: "1", certain: true, demoted: false },
        { text: "to", stress: "0", certain: true, demoted: true },
        { text: "a", stress: "0", certain: true, demoted: true },
        { text: "summers", stress: "10", certain: true, demoted: false },
        { text: "day", stress: "1", certain: true, demoted: false },
      ],
      substitutions: [{ foot: 4, expected: "01", actual: "00", kind: "pyrrhic (both light — hurries through)" }],
      notes: ["Foot 4: two light syllables — let it run."] },
  ],
};

/* --------------------------------------------------------------------------
 * Display-only syllable splitting.
 *
 * The API returns whole words with a stress string, but scansion is
 * conventionally shown with feet divided, which cuts across words ("com | pare").
 * So the word text has to be chopped into as many pieces as it has syllables.
 *
 * This is orthographic guessing, not phonetics — it only has to look right.
 * The stress count from the dictionary is authoritative; this just distributes
 * letters across that many chunks, splitting after each vowel group.
 * ------------------------------------------------------------------------ */
function splitSyllables(word, count) {
  if (count <= 1) return [word];

  const boundaries = [];
  const re = /[aeiouy]+/gi;
  let m;
  while ((m = re.exec(word)) !== null) boundaries.push(m.index + m[0].length);

  // one cut per syllable after the first
  const cuts = [];
  for (let i = 0; i < count - 1 && i < boundaries.length; i++) {
    let b = boundaries[i];
    // pull a single following consonant into the next chunk, so 'sum|mer'
    // rather than 'summ|er'
    if (b < word.length && !/[aeiouy]/i.test(word[b])) {
      const nextVowel = word.slice(b).search(/[aeiouy]/i);
      if (nextVowel > 1) b += nextVowel - 1;
    }
    if (b > (cuts[cuts.length - 1] || 0) && b < word.length) cuts.push(b);
  }

  const parts = [];
  let prev = 0;
  for (const c of cuts) { parts.push(word.slice(prev, c)); prev = c; }
  parts.push(word.slice(prev));

  // pad or merge if the guess disagreed with the dictionary count
  while (parts.length < count) parts.push("");
  while (parts.length > count) parts[count - 1] += parts.pop();
  return parts;
}

const FOOT_NAME = { "01": "iamb", "10": "trochee", "11": "spondee", "00": "pyrrhic",
                    "001": "anapest", "100": "dactyl" };

function toFeet(words, footSize) {
  const syls = [];
  words.forEach((w, wi) => {
    const parts = splitSyllables(w.text, w.stress.length);
    w.stress.split("").forEach((s, si) => {
      syls.push({ text: parts[si] || "", stress: s, wordIdx: wi,
                  first: si === 0, certain: w.certain, demoted: w.demoted });
    });
  });
  const feet = [];
  for (let i = 0; i < syls.length; i += footSize) {
    const group = syls.slice(i, i + footSize);
    feet.push({ syls: group, pattern: group.map((s) => s.stress).join("") });
  }
  return feet;
}

/* ---------------------------------------------------------------- ornament */

/* Three distinct splatters rather than one repeated — a real spill never
   lands twice the same way, and repetition is what makes decoration read as
   a texture fill. Each has an irregular main blob, mid-size satellites,
   fine droplets, and a couple of directional flicks. */

const SPLATS = {
  a: (
    <>
      <path d="M64 26c14-13 40-14 54 1 11 12 10 31 2 45-6 11-17 21-30 25-14 5-31 4-42-6-13-11-18-30-13-46 4-13 17-11 29-19z
               M64 26c-6 4-13 4-18 9" />
      <path d="M119 14c5-3 12-1 13 5 1 5-4 10-9 9-6-1-9-9-4-14z" />
      <path d="M141 44c3-2 8 0 8 4s-5 7-8 5-3-7 0-9z" />
      <path d="M34 96c6-5 16-3 19 4 3 8-4 16-12 15-9-1-13-13-7-19z" />
      <path d="M72 116c4-3 10-1 11 4s-4 9-9 8-6-9-2-12z" />
      <circle cx="106" cy="127" r="3.4" />
      <circle cx="18" cy="60" r="2.6" />
      <circle cx="129" cy="88" r="2.2" />
      <circle cx="88" cy="140" r="1.8" />
      <circle cx="47" cy="132" r="2.4" />
      <circle cx="152" cy="24" r="1.6" />
      {/* flicks — elongated, radiating from the impact */}
      <path d="M150 62c9 3 17 9 23 17-9-3-18-7-24-13z" />
      <path d="M20 30c-7-4-12-11-14-19 6 5 12 11 16 17z" />
      <path d="M96 152c3 7 3 15 1 22-3-7-4-15-3-22z" />
    </>
  ),
  b: (
    <>
      <path d="M88 18c19-8 43 2 50 21 6 17-3 36-18 46-13 9-31 12-46 6-16-6-27-23-25-40 2-15 14-27 28-31 4-1 7-1 11-2z" />
      <path d="M40 78c8-6 19-2 21 8 2 9-7 17-16 15-10-2-13-17-5-23z" />
      <path d="M132 96c5-4 13-1 14 6 1 6-6 11-12 9s-7-11-2-15z" />
      <path d="M62 122c4-3 11-1 12 5s-5 10-10 8-6-10-2-13z" />
      <circle cx="27" cy="42" r="3.8" />
      <circle cx="106" cy="130" r="3" />
      <circle cx="150" cy="60" r="2.4" />
      <circle cx="14" cy="98" r="2" />
      <circle cx="82" cy="146" r="2.6" />
      <circle cx="140" cy="128" r="1.7" />
      <path d="M156 34c10-1 20 2 28 8-10 1-20-1-28-6z" />
      <path d="M30 136c-6 6-14 9-22 10 5-6 13-10 21-12z" />
    </>
  ),
  c: (
    <>
      <path d="M52 40c12-16 38-20 54-8 15 11 18 33 9 49-8 15-25 25-42 24-18-1-34-15-36-33-2-13 6-24 15-32z" />
      <path d="M112 24c6-5 15-1 16 7 1 7-7 12-13 9s-8-12-3-16z" />
      <path d="M28 104c7-5 17-1 18 8 1 8-8 14-15 11s-9-15-3-19z" />
      <path d="M118 112c4-4 11-2 13 4s-4 11-9 9-8-9-4-13z" />
      <circle cx="82" cy="134" r="3.6" />
      <circle cx="146" cy="76" r="2.8" />
      <circle cx="12" cy="66" r="2.2" />
      <circle cx="60" cy="146" r="2" />
      <circle cx="134" cy="140" r="1.9" />
      <circle cx="96" cy="8" r="2.3" />
      <path d="M18 24c-5-7-8-15-8-24 5 7 8 16 10 24z" />
      <path d="M148 122c8 5 14 12 18 21-8-5-15-12-20-19z" />
    </>
  ),
};

const Splat = ({ variant = "a", style, scale = 1, rotate = 0, flip = false }) => (
  <svg width={190 * scale} height={170 * scale} viewBox="0 0 190 170" aria-hidden="true"
       style={{ position: "absolute", pointerEvents: "none",
                transform: `${flip ? "scaleX(-1) " : ""}rotate(${rotate}deg)`, ...style }}>
    <g fill={C.ink}>{SPLATS[variant]}</g>
  </svg>
);

/* Paper grain. feTurbulence at low opacity does more for the aged-paper feel
   than any amount of background colour tuning. */
const Grain = () => (
  <svg aria-hidden="true" style={{ position: "fixed", inset: 0, width: "100%", height: "100%",
                                   pointerEvents: "none", opacity: .05, zIndex: 0 }}>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.82" numOctaves="4" stitchTiles="stitch" />
      <feColorMatrix type="saturate" values="0" />
    </filter>
    <rect width="100%" height="100%" filter="url(#grain)" />
  </svg>
);

const Quill = ({ size = 26, color }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true"
       style={{ color: color || C.ink }}>
    <g fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3.5 20.5C6 13 11 5.6 20.5 2.8c.4 8.4-4.2 14.6-11.4 16.6-2 .6-4 .8-5.6 1.1z" />
      <path d="M3.5 20.5c3.2-3.4 7.4-5.6 11.8-6.6" />
      <path d="M9 16.2c1.6-2.6 3.6-4.8 6-6.4" />
      <path d="M13.6 11.4c1-1.8 2.2-3.4 3.6-4.8" />
    </g>
  </svg>
);

export default function Scansion() {
  const [text, setText] = useState(SAMPLE);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [offline, setOffline] = useState(false);
  const [tab, setTab] = useState("scansion");
  const [showAll, setShowAll] = useState(false);

  const run = async () => {
    setBusy(true); setOffline(false);
    try {
      const res = await fetch(`${API}/scan`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) throw new Error();
      setResult(await res.json());
    } catch {
      setOffline(true); setResult(FALLBACK);
    } finally { setBusy(false); }
  };

  useEffect(() => { run(); /* eslint-disable-next-line */ }, []);

  const css = `
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=IBM+Plex+Mono:wght@400;500&display=swap');
.sc, .sc * { box-sizing: border-box; }
.sc { font-family: Newsreader, Georgia, serif; color: ${C.ink}; background: ${C.bg};
      min-height: 100vh; position: relative; overflow-x: hidden; -webkit-font-smoothing: antialiased; }
.sc .mono { font-family: 'IBM Plex Mono', ui-monospace, monospace; }
.sc .lab { font-size: 10px; letter-spacing: .17em; text-transform: uppercase;
           color: ${C.dim}; font-weight: 500; }
.sc .panel { background: ${C.panel}; border: 1px solid ${C.rule}; border-radius: 3px;
             box-shadow: 0 1px 2px rgba(28,26,22,.04); }
.sc .btn { font-size: 14px; padding: 11px 22px; border-radius: 4px; cursor: pointer;
           border: 1px solid ${C.ink}; background: ${C.ink}; color: ${C.bg};
           font-family: Newsreader, serif; transition: opacity .15s; }
.sc .btn:hover { opacity: .85; }
.sc .btn.ghost { background: transparent; color: ${C.ink}; border-color: ${C.rule}; }
.sc .btn.ghost:hover { border-color: ${C.ink}; opacity: 1; }
.sc .tab { font-size: 12.5px; padding: 8px 15px; border-radius: 4px; cursor: pointer;
           border: 1px solid transparent; background: transparent; color: ${C.dim};
           font-family: Newsreader, serif; display: inline-flex; align-items: center; gap: 7px;
           transition: all .15s; }
.sc .tab:hover { color: ${C.ink}; }
.sc .tab.on { background: ${C.ink}; color: ${C.bg}; }
.sc textarea { width: 100%; background: transparent; border: none; resize: vertical;
               font-family: Newsreader, Georgia, serif; font-size: 15.5px; line-height: 2;
               color: ${C.ink}; min-height: 300px; }
.sc textarea:focus { outline: none; }
.sc .nav-link { font-size: 14.5px; color: ${C.ink}; text-decoration: none; opacity: .78; }
.sc .nav-link:hover { opacity: 1; }
.sc .foot { display: inline-flex; flex-direction: column; align-items: center;
            padding: 0 9px; border-right: 1px solid ${C.rule}; }
.sc .foot:last-child { border-right: none; }
.sc .syl-row { display: flex; align-items: baseline; gap: 7px; }
.sc .marks-row { display: flex; gap: 7px; margin-bottom: 2px; }
.sc .mk { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: ${C.mark};
          min-width: 1ch; text-align: center; }
.sc .syl { font-size: 19px; line-height: 1.3; min-width: 1ch; text-align: center; }
.sc .syl.quiet { color: ${C.faint}; }
.sc .syl.guess { border-bottom: 1px dotted ${C.mark}; }
.sc .grid { display: grid; grid-template-columns: 340px 1fr; gap: 22px;
            max-width: 1420px; margin: 0 auto; padding: 0 34px 70px; }
.sc .lower { display: grid; grid-template-columns: 1fr 1.35fr; gap: 22px;
             max-width: 1420px; margin: 0 auto; padding: 0 34px 90px; }
.sc .res-grid { display: grid; grid-template-columns: 1fr 210px; gap: 22px; }
@media (max-width: 1100px) {
  .sc .grid, .sc .lower, .sc .res-grid { grid-template-columns: 1fr; }
}
.sc :focus-visible { outline: 2px solid ${C.mark}; outline-offset: 2px; }
`;

  const lines = result?.lines || [];
  const shown = showAll ? lines : lines.slice(0, 4);
  const footSize = 2;

  return (
    <div className="sc">
      <style>{css}</style>

      <Grain />
      <Splat variant="a" style={{ top: -26, left: -40, opacity: .16 }} scale={1.3} rotate={-8} />
      <Splat variant="c" style={{ top: 96, left: 118, opacity: .07 }} scale={.55} rotate={22} />
      <Splat variant="b" style={{ top: 210, right: -54, opacity: .11 }} scale={1.45} flip rotate={6} />
      <Splat variant="a" style={{ top: 640, right: 40, opacity: .05 }} scale={.7} rotate={-30} />
      <Splat variant="c" style={{ bottom: 90, left: -56, opacity: .1 }} scale={1.2} rotate={14} />
      <Splat variant="b" style={{ bottom: 260, right: 96, opacity: .045 }} scale={.6} rotate={-18} flip />

      {/* nav */}
      <nav style={{ display: "flex", alignItems: "center", gap: 16, padding: "20px 34px",
                    maxWidth: 1420, margin: "0 auto", position: "relative", zIndex: 1 }}>
        <span style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 23 }}>
          <Quill size={25} />
          Scansion
        </span>
        <hr style={{ flex: 1, border: "none", borderTop: `1px solid ${C.rule}`, margin: "0 16px" }} />
        <a className="nav-link" href="#how">How it works</a>
        <button className="btn" onClick={run}>Analyze poem</button>
      </nav>

      {/* hero */}
      <header style={{ textAlign: "center", padding: "34px 24px 44px", position: "relative", zIndex: 1 }}>
        <h1 style={{ fontSize: 58, fontWeight: 400, lineHeight: 1.08, letterSpacing: "-.02em", margin: 0 }}>
          Hear the poem.<br />
          See its <span style={{ fontStyle: "italic", color: C.mark }}>heartbeat.</span>
        </h1>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center",
                      gap: 12, margin: "22px 0 18px" }}>
          <hr style={{ width: 90, border: "none", borderTop: `1px solid ${C.rule}` }} />
          <span style={{ color: C.mark, fontSize: 13 }}>&#10087;</span>
          <hr style={{ width: 90, border: "none", borderTop: `1px solid ${C.rule}` }} />
        </div>
        <p style={{ fontSize: 17.5, color: C.dim, lineHeight: 1.6, margin: 0 }}>
          Metre. Inversions. Caesura. Rhyme.<br />
          Everything a performer needs to know.
        </p>
      </header>

      {/* main */}
      <div className="grid" style={{ position: "relative", zIndex: 1 }}>

        {/* poem input */}
        <section className="panel" style={{ background: C.card, padding: "18px 20px 22px",
                                            display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", alignItems: "center", marginBottom: 12 }}>
            <span className="lab" style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Quill size={15} color={C.dim} /> Your poem
            </span>
            <button className="lab" onClick={() => setText("")}
                    style={{ marginLeft: "auto", background: "none", border: "none",
                             cursor: "pointer", textTransform: "none", letterSpacing: 0,
                             fontSize: 13.5, fontFamily: "Newsreader, serif" }}>
              Clear
            </button>
          </div>

          <div style={{ background: C.panel, border: `1px solid ${C.rule}`, borderRadius: 2,
                        padding: "16px 18px", flex: 1 }}>
            <textarea value={text} onChange={(e) => setText(e.target.value)} spellCheck={false} />
          </div>

          <button className="btn" onClick={run} disabled={busy}
                  style={{ marginTop: 18, width: "100%", fontSize: 15.5, padding: "13px" }}>
            {busy ? "Analyzing…" : "Analyze poem  \u2192"}
          </button>

          {offline && (
            <div className="lab" style={{ marginTop: 10, color: C.mark, textAlign: "center" }}>
              API offline · showing sample
            </div>
          )}

          <div style={{ marginTop: 26, paddingTop: 20, borderTop: `1px solid ${C.rule}`,
                        display: "flex", gap: 10 }}>
            <span style={{ fontSize: 34, color: C.rule, lineHeight: .8,
                           fontFamily: "Newsreader, serif" }}>&ldquo;</span>
            <div>
              <p style={{ fontStyle: "italic", fontSize: 15.5, lineHeight: 1.55, margin: 0 }}>
                Poetry is what gets lost in translation.
              </p>
              <div className="lab" style={{ marginTop: 8 }}>— Robert Frost</div>
            </div>
          </div>
        </section>

        {/* results */}
        <section className="panel" style={{ padding: "18px 22px 24px" }}>
          <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: 10,
                        marginBottom: 20 }}>
            <span className="lab" style={{ fontSize: 11.5 }}>Scansion results</span>
            <div style={{ marginLeft: "auto", display: "flex", gap: 4 }}>
              {[["scansion", "\u2261"], ["rhyme", "\u2295"], ["breath", "\u25D1"]].map(([k, icon]) => (
                <button key={k} className={`tab${tab === k ? " on" : ""}`} onClick={() => setTab(k)}>
                  <span style={{ fontSize: 11 }}>{icon}</span>
                  {k === "rhyme" ? "Rhyme scheme" : k[0].toUpperCase() + k.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div className="res-grid">
            <div>
              {tab === "scansion" && shown.map((ln, i) => {
                const feet = toFeet(ln.words, footSize);
                return (
                  <div key={i} style={{ display: "flex", gap: 16, alignItems: "flex-start",
                                        padding: "16px 0",
                                        borderBottom: i < shown.length - 1 ? `1px solid ${C.rule}` : "none" }}>
                    <span className="mono" style={{ fontSize: 12, color: C.faint, paddingTop: 20 }}>
                      {i + 1}
                    </span>
                    <div style={{ display: "flex", flexWrap: "wrap" }}>
                      {feet.map((f, fi) => (
                        <span key={fi} className="foot">
                          <span className="marks-row">
                            {f.syls.map((s, si) => (
                              <span key={si} className="mk">
                                {s.stress === "1" ? "\u2044" : "\u02D8"}
                              </span>
                            ))}
                          </span>
                          <span className="syl-row">
                            {f.syls.map((s, si) => (
                              <span key={si}
                                    className={`syl${s.demoted ? " quiet" : ""}${s.certain ? "" : " guess"}`}>
                                {s.text}
                              </span>
                            ))}
                          </span>
                          <span className="lab" style={{ marginTop: 7, fontSize: 9,
                                                         color: f.pattern === "01" ? C.faint : C.mark }}>
                            {FOOT_NAME[f.pattern] || "—"}
                          </span>
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}

              {tab === "rhyme" && (
                <div style={{ display: "flex", gap: 26, flexWrap: "wrap" }}>
                  <div style={{ minWidth: 200 }}>
                    {lines.map((ln, i) => {
                      const toks = ln.text.toLowerCase().match(/[a-z']+/g) || [];
                      return (
                        <div key={i} style={{ display: "flex", gap: 14, padding: "7px 0",
                                              borderBottom: `1px solid ${C.rule}` }}>
                          <span className="mono" style={{ fontSize: 12, color: C.faint, width: 18 }}>
                            {i + 1}
                          </span>
                          <span style={{ flex: 1, fontSize: 16 }}>{toks[toks.length - 1] || "—"}</span>
                          <span className="mono" style={{ fontSize: 14, color: C.gold }}>
                            {(result.rhyme_scheme || "")[i] || ""}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                  <div style={{ background: C.card, border: `1px solid ${C.rule}`, borderRadius: 2,
                                padding: "18px 20px", alignSelf: "flex-start", minWidth: 180 }}>
                    <div style={{ fontSize: 17, fontWeight: 500 }}>Rhyme scheme</div>
                    <div className="mono" style={{ fontSize: 15, marginTop: 8, letterSpacing: ".08em" }}>
                      {result.rhyme_scheme || "—"}
                    </div>
                    <div style={{ fontSize: 15, color: C.dim, marginTop: 16, lineHeight: 1.5 }}>
                      {(result.rhyme_scheme || "").startsWith("ABAB")
                        ? "Shakespearean (or Elizabethan) sonnet"
                        : "No standard form matched"}
                    </div>
                  </div>
                </div>
              )}

              {tab === "breath" && (
                <div>
                  {lines.map((ln, i) => (
                    <div key={i} style={{ display: "flex", gap: 14, alignItems: "flex-start",
                                          padding: "12px 0", borderBottom: `1px solid ${C.rule}` }}>
                      <span className="mono" style={{ fontSize: 11, color: C.faint,
                                                      border: `1px solid ${C.rule}`, borderRadius: "50%",
                                                      width: 22, height: 22, display: "inline-flex",
                                                      alignItems: "center", justifyContent: "center",
                                                      flexShrink: 0 }}>
                        {i + 1}
                      </span>
                      <div>
                        <div style={{ fontSize: 17, lineHeight: 1.5 }}>
                          {ln.text}
                          {ln.caesura && <span style={{ color: C.mark, marginLeft: 8 }}>&#8739;</span>}
                        </div>
                        {ln.notes?.length > 0 && (
                          <div className="lab" style={{ marginTop: 6, letterSpacing: ".05em",
                                                        textTransform: "none", fontSize: 13,
                                                        fontFamily: "Newsreader, serif", fontStyle: "italic" }}>
                            {ln.notes.join("  ·  ")}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {lines.length > 4 && tab === "scansion" && (
                <button className="btn ghost" style={{ marginTop: 18, fontSize: 13 }}
                        onClick={() => setShowAll(!showAll)}>
                  {showAll ? "Show fewer" : `Show all ${lines.length} lines  \u2304`}
                </button>
              )}
            </div>

            {/* key sidebar */}
            <aside style={{ background: C.card, border: `1px solid ${C.rule}`, borderRadius: 2,
                            padding: "18px 18px 20px", alignSelf: "flex-start" }}>
              <div className="lab" style={{ marginBottom: 12 }}>Key</div>
              {[["\u2044", "stressed"], ["\u02D8", "unstressed"], ["\u00D7", "spondee"],
                ["\u2502", "caesura"]].map(([sym, mean]) => (
                <div key={mean} style={{ display: "flex", gap: 13, padding: "4px 0", fontSize: 14 }}>
                  <span className="mono" style={{ color: C.mark, width: 12 }}>{sym}</span>
                  <span style={{ color: C.dim }}>{mean}</span>
                </div>
              ))}

              <hr style={{ border: "none", borderTop: `1px solid ${C.rule}`, margin: "16px 0" }} />

              <div className="lab" style={{ marginBottom: 8 }}>Metre</div>
              <div style={{ fontSize: 15.5, fontWeight: 500, textTransform: "capitalize" }}>
                {result?.dominant_meter || "—"}
              </div>
              {result && Object.keys(result.meter_counts || {}).length > 1 && (
                <div style={{ fontSize: 14, color: C.dim, marginTop: 3 }}>(with variations)</div>
              )}

              {result && shown.some((l) => l.substitutions?.length) && (
                <>
                  <hr style={{ border: "none", borderTop: `1px solid ${C.rule}`, margin: "16px 0" }} />
                  <div className="lab" style={{ marginBottom: 8 }}>Inversion highlights</div>
                  {shown.flatMap((l, li) =>
                    (l.substitutions || []).map((s, si) => (
                      <p key={`${li}-${si}`} style={{ fontSize: 14, lineHeight: 1.55,
                                                      color: C.dim, margin: "0 0 10px" }}>
                        Line <strong style={{ color: C.ink, fontWeight: 500 }}>{li + 1}</strong>,
                        foot <strong style={{ color: C.ink, fontWeight: 500 }}>{s.foot}</strong> is a{" "}
                        {s.kind.split(" (")[0]}.
                      </p>
                    ))
                  ).slice(0, 4)}
                </>
              )}
            </aside>
          </div>
        </section>
      </div>

      {/* footer note */}
      <div className="lower" id="how">
        <div className="panel" style={{ padding: "18px 22px" }}>
          <div className="lab" style={{ marginBottom: 12 }}>How it reads a line</div>
          <ol style={{ margin: 0, paddingLeft: 18, fontSize: 15, lineHeight: 1.9, color: C.dim }}>
            <li>Look up each word's syllables and stress in CMUdict</li>
            <li>Guess from spelling when a word isn't in the dictionary</li>
            <li>Demote function words — "the" and "of" carry no beat in a line</li>
            <li>Match the result against standard metrical templates</li>
            <li>Report every foot that departs from the winner</li>
          </ol>
        </div>
        <div className="panel" style={{ padding: "18px 22px" }}>
          <div className="lab" style={{ marginBottom: 12 }}>Why word stress isn't line stress</div>
          <p style={{ fontSize: 15, lineHeight: 1.75, color: C.dim, margin: 0 }}>
            The dictionary records words alone, so every monosyllable comes back
            stressed — including <em>the</em>, <em>of</em>, and <em>and</em>. Read
            naively, every line over-reports its beats. A demotion pass drops them,
            then puts one back wherever the result would leave three unstressed
            syllables in a row, which English resists. Greyed words below are the
            ones demoted.
          </p>
        </div>
      </div>
    </div>
  );
}

