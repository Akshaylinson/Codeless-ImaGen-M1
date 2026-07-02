export function renderComparison(container, beforeUrl, afterUrl) {
  if (!container) return;
  container.innerHTML = `
    <div class="comparison">
      <img src="${beforeUrl}" alt="Before image">
      <div class="after-wrap">
        <img src="${afterUrl}" alt="After image">
      </div>
      <input type="range" min="0" max="100" value="50">
    </div>
  `;
  const range = container.querySelector('input[type="range"]');
  const afterWrap = container.querySelector('.after-wrap');
  range.addEventListener('input', () => {
    afterWrap.style.width = `${range.value}%`;
  });
}

