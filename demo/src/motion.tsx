// SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
// Motion that answers the visitor: the navigation underline follows the
// section being read, and charts draw in once when they scroll into view.
// Transform, opacity and clip-path only; reduced motion is handled in CSS.
import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";

export const SECTIONS: { id: string; label: string }[] = [
  { id: "overview", label: "Findings" },
  { id: "results", label: "Evidence" },
  { id: "sandbox", label: "Sandbox" },
  { id: "assumptions", label: "Assumptions" },
  { id: "method", label: "Method and limitations" },
];

export function SectionNav() {
  const [active, setActive] = useState<string | null>(null);
  const navRef = useRef<HTMLElement>(null);
  const barRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const seen = new Map<string, boolean>();
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) seen.set(e.target.id, e.isIntersecting);
        const first = SECTIONS.find((s) => seen.get(s.id));
        setActive(first ? first.id : null);
      },
      { rootMargin: "-30% 0px -60% 0px" },
    );
    const attach = () => SECTIONS.forEach((s) => { const el = document.getElementById(s.id); if (el) io.observe(el); });
    attach();
    // Sections mount after the results load; observe them when they appear.
    const mo = new MutationObserver(attach);
    mo.observe(document.getElementById("main") ?? document.body, { childList: true, subtree: true });
    return () => { io.disconnect(); mo.disconnect(); };
  }, []);

  useLayoutEffect(() => {
    const nav = navRef.current, bar = barRef.current;
    if (!nav || !bar) return;
    const link = active ? nav.querySelector<HTMLAnchorElement>(`a[href="#${active}"]`) : null;
    if (!link) { bar.style.opacity = "0"; return; }
    bar.style.opacity = "1";
    bar.style.transform = `translateX(${link.offsetLeft}px) scaleX(${link.offsetWidth / 100})`;
  }, [active]);

  return (
    <nav aria-label="Sections" ref={navRef} className="sections">
      {SECTIONS.map((s) => (
        <a key={s.id} href={`#${s.id}`} aria-current={active === s.id ? "location" : undefined}>{s.label}</a>
      ))}
      <span className="nav-bar" ref={barRef} aria-hidden="true" />
    </nav>
  );
}

/** Wraps a chart; its series draw in once when it first scrolls into view. */
export function Reveal({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<"idle" | "pending" | "done">("idle");
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === "undefined") return;
    const r = el.getBoundingClientRect();
    if (r.top < window.innerHeight && r.bottom > 0) return; // already visible: no wipe
    setState("pending");
    const io = new IntersectionObserver((es) => {
      if (es.some((e) => e.isIntersecting)) { setState("done"); io.disconnect(); }
    }, { threshold: 0.25 });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return <div ref={ref} className="reveal" data-reveal={state}>{children}</div>;
}
