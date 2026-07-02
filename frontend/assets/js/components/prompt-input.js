export function createPromptInput({ value = '', onChange }) {
  const wrap = document.createElement('div');
  wrap.className = 'field';
  wrap.innerHTML = `
    <label for="instruction">Instruction</label>
    <textarea id="instruction" placeholder="Remove the sunglasses.">${value}</textarea>
  `;
  const textarea = wrap.querySelector('textarea');
  textarea.addEventListener('input', () => onChange(textarea.value));
  return wrap;
}

