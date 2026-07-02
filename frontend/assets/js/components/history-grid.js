import { escapeHtml, formatDate } from '../utils/dom.js';

export function renderHistoryGrid(container, jobs) {
  if (!container) return;
  if (!jobs.length) {
    container.innerHTML = '<div class="panel card"><h3>No jobs yet</h3><p class="muted">Upload an image and start editing.</p></div>';
    return;
  }
  container.innerHTML = jobs.map((job) => `
    <article class="thumb">
      <div class="meta">
        <strong>#${job.id}</strong>
        <div class="muted">${escapeHtml(job.status)} · ${job.progress}%</div>
        <div class="muted">${escapeHtml(job.instruction)}</div>
        <div class="muted">${formatDate(job.created_at)}</div>
      </div>
    </article>
  `).join('');
}

