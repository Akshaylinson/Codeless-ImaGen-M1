export function createUploadZone({ onFileSelected }) {
  const wrapper = document.createElement('label');
  wrapper.className = 'panel';
  wrapper.style.display = 'grid';
  wrapper.style.gap = '12px';
  wrapper.style.padding = '24px';
  wrapper.style.cursor = 'pointer';
  wrapper.innerHTML = `
    <strong>Upload image</strong>
    <span class="muted">PNG, JPEG, or WEBP up to 20 MB</span>
    <input type="file" accept="image/png,image/jpeg,image/webp" hidden />
  `;
  const input = wrapper.querySelector('input');
  input.addEventListener('change', () => {
    const file = input.files && input.files[0];
    if (file) onFileSelected(file);
  });
  return wrapper;
}

