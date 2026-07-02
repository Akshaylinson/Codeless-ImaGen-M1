export function toast(message, tone = 'info') {
  const node = document.createElement('div');
  node.className = `panel`;
  node.style.position = 'fixed';
  node.style.right = '18px';
  node.style.bottom = '18px';
  node.style.zIndex = '9999';
  node.style.padding = '14px 16px';
  node.style.maxWidth = '320px';
  node.style.borderColor = tone === 'error' ? 'rgba(255,107,138,0.5)' : 'rgba(126,230,201,0.28)';
  node.textContent = message;
  document.body.appendChild(node);
  setTimeout(() => node.remove(), 3000);
}

