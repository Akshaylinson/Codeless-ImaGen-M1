import { apiFetch, clearToken, setToken } from '../utils/api.js';
import { $ } from '../utils/dom.js';
import { toast } from '../components/toast.js';

async function login() {
  const username = $('#username').value.trim();
  const password = $('#password').value;
  const status = $('#authStatus');
  try {
    const result = await apiFetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    setToken(result.access_token);
    status.textContent = `Logged in as ${result.username} (${result.role})`;
    await loadDashboard();
  } catch (error) {
    status.textContent = error.message;
    toast(error.message, 'error');
  }
}

async function loadDashboard() {
  try {
    const [metrics, history] = await Promise.all([
      apiFetch('/api/metrics'),
      apiFetch('/api/history'),
    ]);
    $('#metrics').innerHTML = `
      <div class="stat"><strong>${metrics.cpu_usage_percent}%</strong><span class="muted">CPU usage</span></div>
      <div class="stat"><strong>${metrics.ram_usage_mb} MB</strong><span class="muted">RAM usage</span></div>
      <div class="stat"><strong>${metrics.queue_size}</strong><span class="muted">Queue size</span></div>
      <div class="stat"><strong>${metrics.active_jobs}</strong><span class="muted">Active jobs</span></div>
    `;
    $('#recentJobs').innerHTML = history.jobs.slice(0, 8).map((job) => `
      <tr>
        <td>#${job.id}</td>
        <td>${job.status}</td>
        <td>${job.instruction}</td>
        <td>${job.progress}%</td>
      </tr>
    `).join('') || '<tr><td colspan="4" class="muted">No jobs yet.</td></tr>';
  } catch (error) {
    $('#authStatus').textContent = error.message;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  $('#loginBtn').addEventListener('click', login);
  loadDashboard();
});

