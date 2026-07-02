export function showModal(content) {
  const overlay = document.createElement('div');
  overlay.style.position = 'fixed';
  overlay.style.inset = '0';
  overlay.style.background = 'rgba(0,0,0,0.6)';
  overlay.style.display = 'grid';
  overlay.style.placeItems = 'center';
  overlay.style.zIndex = '10000';
  overlay.innerHTML = `<div class="panel card" style="max-width:720px;width:min(720px,calc(100% - 32px));">${content}</div>`;
  overlay.addEventListener('click', (event) => {
    if (event.target === overlay) overlay.remove();
  });
  document.body.appendChild(overlay);
  return overlay;
}

