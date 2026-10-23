import { useEffect, useState } from "react";

/**
 * Viewport width in CSS pixels. The mobile fleet layout needs one number only,
 * so it comes from `window.innerWidth` and a resize listener instead of a media
 * query the React tree cannot read. Static renders (tests, SSR) pass an
 * explicit width to the component; this hook is the container's default.
 */
export function useViewportWidth(fallback = 1_280): number {
  const [width, setWidth] = useState(() =>
    typeof window === "undefined" || typeof window.innerWidth !== "number" ? fallback : window.innerWidth,
  );

  useEffect(() => {
    if (typeof window === "undefined" || typeof window.addEventListener !== "function") return;
    const measure = () => setWidth(window.innerWidth);
    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, []);

  return width;
}
