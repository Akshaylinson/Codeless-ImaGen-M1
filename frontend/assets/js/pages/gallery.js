import { apiFetch } from '../utils/api.js';
import { $, escapeHtml } from '../utils/dom.js';

async function loadGallery() {
  const response = await apiFetch('/api/history');
  const query = $('#search').value.trim().toLowerCase();
  const jobs = response.jobs.filter((job) =>
    !query ||
    job.instruction.toLowerCase().includes(query) ||
    job.status.toLowerCase().includes(query)
  );
  $('#gallery').innerHTML = jobs.map((job) => `
    <article class="thumb">
      <div class="meta">
        <strong>#${job.id}</strong>
        <div class="muted">${escapeHtml(job.status)}</div>
        <div class="muted">${escapeHtml(job.instruction)}</div>
        <div class="muted">${job.output_path ? 'Result ready' : 'Processing'}</div>
      </div>
    </article>
  `).join('') || '<div class="panel card"><h3>No matches</h3></div>';
}

window.addEventListener('DOMContentLoaded', () => {
  $('#search').addEventListener('input', loadGallery);
  loadGallery();
});

