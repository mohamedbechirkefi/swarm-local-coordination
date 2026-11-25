// SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
// Hand-written SVG charts (no chart library). Text uses currentColor so the page's
// theme tokens set its contrast; every chart has a text description and a legend in HTML.
import { useEffect, useState } from "react";

/** True on narrow screens, where line charts use a narrower drawing so text stays legible. */
function useNarrow(): boolean {
  const q = "(max-width: 36rem)";
  const [narrow, setNarrow] = useState(() => typeof window !== "undefined" && window.matchMedia?.(q).matches === true);
  useEffect(() => {
    const mq = window.matchMedia?.(q);
    if (!mq) return;
    const on = () => setNarrow(mq.matches);
    mq.addEventListener?.("change", on);
    return () => mq.removeEventListener?.("change", on);
  }, []);
  return narrow;
}

export type Pt = [number, number] | null;

export interface Series {
  id: string;
  label: string;
  color: string;
  dash?: string;
  points: Pt[];
}

interface LineProps {
  title: string;
  series: Series[];
  markers?: number[];
  markerLabel?: string;
  xLabel: string;
  yLabel: string;
  empty: string;
  xDomain?: [number, number];
  yDomain?: [number, number];
}

const H = 250, L = 46, R = 26, T = 12, B = 40;

function ticks(lo: number, hi: number, n: number): number[] {
  const span = hi - lo || 1;
  const raw = span / n;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const stepv = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= n) ?? raw;
  const out: number[] = [];
  const k0 = Math.ceil(lo / stepv - 1e-9), k1 = Math.floor(hi / stepv + 1e-9);
  for (let k = k0; k <= k1; k++) out.push(Number((k * stepv).toFixed(6)) + 0);
  return out;
}

function pathOf(points: Pt[], sx: (x: number) => number, sy: (y: number) => number): string {
  let d = "";
  let pen = false;
  for (const p of points) {
    if (p === null) {
      pen = false;
      continue;
    }
    d += `${pen ? "L" : "M"}${sx(p[0]).toFixed(1)},${sy(p[1]).toFixed(1)}`;
    pen = true;
  }
  return d;
}

export function LineChart({ title, series, markers = [], markerLabel, xLabel, yLabel, empty, xDomain, yDomain = [0, 1] }: LineProps) {
  const narrow = useNarrow();
  const W = narrow ? 340 : 600;
  const all = series.flatMap((s) => s.points.filter((p): p is [number, number] => p !== null));
  if (all.length === 0 && !xDomain) {
    return (
      <div className="chart-empty" role="img" aria-label={`${title}: ${empty}`}>
        <p>{empty}</p>
      </div>
    );
  }
  let x0 = xDomain ? xDomain[0] : Math.min(...all.map((p) => p[0]));
  let x1 = xDomain ? xDomain[1] : Math.max(...all.map((p) => p[0]));
  if (x1 - x0 < 10) x1 = x0 + 10;
  const [y0, y1] = yDomain;
  const sx = (x: number) => L + ((x - x0) / (x1 - x0)) * (W - L - R);
  const sy = (y: number) => T + (1 - (y - y0) / (y1 - y0)) * (H - T - B);
  return (
    <div className="chart">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={title} className="chart-svg">
        {ticks(y0, y1, 5).map((v) => (
          <g key={`y${v}`}>
            <line x1={L} x2={W - R} y1={sy(v)} y2={sy(v)} className="grid" />
            <text x={L - 6} y={sy(v) + 4} textAnchor="end" className="tick">{v}</text>
          </g>
        ))}
        {ticks(x0, x1, narrow ? 3 : 6).map((v) => (
          <text key={`x${v}`} x={sx(v)} y={H - B + 16} textAnchor="middle" className="tick">{v}</text>
        ))}
        <line x1={L} x2={W - R} y1={sy(y0)} y2={sy(y0)} className="axis" />
        <line x1={L} x2={L} y1={T} y2={sy(y0)} className="axis" />
        <text x={(L + W - R) / 2} y={H - 4} textAnchor="middle" className="tick">{xLabel}</text>
        <text x={12} y={(T + H - B) / 2} textAnchor="middle" className="tick" transform={`rotate(-90 12 ${(T + H - B) / 2})`}>{yLabel}</text>
        {markers.filter((m) => m >= x0 && m <= x1).map((m, i) => (
          <line key={`m${i}`} x1={sx(m)} x2={sx(m)} y1={T} y2={sy(y0)} className="marker" />
        ))}
        {series.map((s) => (
          <path key={s.id} d={pathOf(s.points, sx, sy)} fill="none" stroke={s.color} strokeWidth={2.2} strokeDasharray={s.dash} />
        ))}
      </svg>
      <ul className="legend">
        {series.map((s) => (
          <li key={s.id}>
            <svg width="28" height="10" aria-hidden="true"><line x1="0" x2="28" y1="5" y2="5" stroke={s.color} strokeWidth="2.5" strokeDasharray={s.dash} /></svg>
            {s.label}
          </li>
        ))}
        {markerLabel && (
          <li>
            <svg width="28" height="10" aria-hidden="true"><line x1="14" x2="14" y1="0" y2="10" className="marker" /></svg>
            {markerLabel}
          </li>
        )}
      </ul>
    </div>
  );
}

export interface ForestRow {
  key: string;
  label: string;
  estimate: number;
  lo: number;
  hi: number;
  text: string;
  hollow?: boolean;
  emphasis?: boolean;
}

interface ForestProps {
  title: string;
  rows: ForestRow[];
  domain: [number, number];
  sesoi: number;
  band?: { lo: number; hi: number; estimate: number };
  xLabel: string;
  labelWidth?: number;
}

export function ForestPlot({ title, rows, domain, sesoi, band, xLabel, labelWidth = 168 }: ForestProps) {
  const FW = 640, LW = labelWidth, RW = 168, RH = 22, top = 10, bottom = 40;
  const h = top + rows.length * RH + bottom;
  const [d0, d1] = domain;
  const sx = (v: number) => LW + ((v - d0) / (d1 - d0)) * (FW - LW - RW);
  const yEnd = top + rows.length * RH;
  return (
    <svg viewBox={`0 0 ${FW} ${h}`} role="img" aria-label={title} className="chart-svg forest">
      {band && <rect x={sx(band.lo)} width={Math.max(1, sx(band.hi) - sx(band.lo))} y={top} height={yEnd - top} className="band" />}
      {band && <line x1={sx(band.estimate)} x2={sx(band.estimate)} y1={top} y2={yEnd} className="band-line" />}
      <line x1={sx(0)} x2={sx(0)} y1={top} y2={yEnd} className="axis" />
      {[-sesoi, sesoi].map((v) => <line key={v} x1={sx(v)} x2={sx(v)} y1={top} y2={yEnd} className="sesoi" />)}
      {rows.map((r, i) => {
        const y = top + i * RH + RH / 2;
        return (
          <g key={r.key} className={r.emphasis ? "row emph" : "row"}>
            <text x={LW - 8} y={y + 4} textAnchor="end" className="tick">{r.label}</text>
            <line x1={sx(r.lo)} x2={sx(r.hi)} y1={y} y2={y} className="ci" />
            <circle cx={sx(r.estimate)} cy={y} r={4.5} className={r.hollow ? "pt hollow" : "pt"} />
            <text x={FW - RW + 10} y={y + 4} className="tick mono">{r.text}</text>
          </g>
        );
      })}
      {ticks(d0, d1, 6).map((v) => (
        <text key={v} x={sx(v)} y={yEnd + 16} textAnchor="middle" className="tick">{v}</text>
      ))}
      <text x={(LW + FW - RW) / 2} y={h - 4} textAnchor="middle" className="tick">{xLabel}</text>
    </svg>
  );
}
