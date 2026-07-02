export function createPagination({ page = 1, pageSize = 12, total = 0, onChange }) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const wrapper = document.createElement('div');
  wrapper.className = 'nav';
  for (let index = 1; index <= totalPages; index += 1) {
    const button = document.createElement('button');
    button.className = 'ghost';
    button.textContent = String(index);
    if (index === page) button.style.borderColor = 'rgba(126,230,201,0.5)';
    button.addEventListener('click', () => onChange(index));
    wrapper.appendChild(button);
  }
  return wrapper;
}

