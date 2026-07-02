export function emptyState(title, description) {
  const wrapper = document.createElement('div');
  wrapper.className = 'panel';
  wrapper.innerHTML = `
    <div class="card">
      <h3>${title}</h3>
      <p class="muted">${description}</p>
    </div>
  `;
  return wrapper;
}

