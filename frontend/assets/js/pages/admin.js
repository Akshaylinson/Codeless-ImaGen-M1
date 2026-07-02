import { apiFetch } from '../services/api.js';
import { $ } from '../utils/dom.js';

async function loadAdmin() {
  const [metrics, history] = await Promise.all([
    apiFetch('/metrics'),
    apiFetch('/history'),
  ]);
  $('#adminMetrics').innerHTML = `
    <div class="stat"><strong>${metrics.cpu_usage_percent}%</strong><span class="muted">CPU usage</span></div>
    <div class="stat"><strong>${metrics.ram_usage_mb} MB</strong><span class="muted">RAM usage</span></div>
    <div class="stat"><strong>${metrics.disk_free_mb} MB</strong><span class="muted">Disk free</span></div>
    <div class="stat"><strong>${metrics.queue_size}</strong><span class="muted">Queue size</span></div>
  `;
  $('#adminJobs').innerHTML = history.jobs.map((job) => `
    <div class="panel card">
      <strong>Job #${job.id}</strong>
      <div class="muted">${job.status} · ${job.progress}%</div>
      <div class="muted">${job.instruction}</div>
      ${job.error_message ? `<div class="danger">${job.error_message}</div>` : ''}
    </div>
  `).join('') || '<div class="panel card"><h3>No jobs</h3></div>';
}

window.addEventListener('DOMContentLoaded', loadAdmin);
