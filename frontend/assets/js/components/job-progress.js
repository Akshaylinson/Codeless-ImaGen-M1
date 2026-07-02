export function setProgress(bar, value) {
  if (!bar) return;
  bar.style.width = `${Math.max(0, Math.min(100, value))}%`;
}

