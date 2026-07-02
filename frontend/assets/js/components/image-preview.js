export function setPreview(target, fileOrUrl) {
  if (!target) return;
  target.innerHTML = '';
  if (!fileOrUrl) {
    target.textContent = 'No image selected';
    return;
  }
  const img = document.createElement('img');
  img.src = typeof fileOrUrl === 'string' ? fileOrUrl : URL.createObjectURL(fileOrUrl);
  target.appendChild(img);
}

