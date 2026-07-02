import { apiFetch } from '../utils/api.js';
import { $, formatDate } from '../utils/dom.js';
import { createUploadZone } from '../components/upload-zone.js';
import { setPreview } from '../components/image-preview.js';
import { setProgress } from '../components/job-progress.js';
import { renderComparison } from '../components/comparison-slider.js';
import { toast } from '../components/toast.js';

let selectedFile = null;
let selectedImageId = null;
let currentJobId = null;

function setStatus(text) {
  $('#jobStatus').textContent = text;
}

async function uploadCurrentFile(file) {
  const form = new FormData();
  form.append('file', file);
  const response = await apiFetch('/api/images/upload', { method: 'POST', body: form });
  selectedImageId = response.image_id;
  setStatus(`Uploaded image #${selectedImageId}`);
  return response.image_id;
}

async function startEditing() {
  const instruction = $('#instruction').value.trim();
  if (!selectedFile) {
    toast('Please select an image first', 'error');
    return;
  }
  if (!selectedImageId) {
    await uploadCurrentFile(selectedFile);
  }
  const response = await apiFetch('/api/edit/start', {
    method: 'POST',
    body: JSON.stringify({ image_id: selectedImageId, instruction }),
  });
  currentJobId = response.job_id;
  setStatus(`Job #${currentJobId} queued`);
  pollJob(currentJobId, selectedFile, instruction);
}

async function pollJob(jobId, beforeFile, instruction) {
  const beforeUrl = URL.createObjectURL(beforeFile);
  const timer = setInterval(async () => {
    try {
      const job = await apiFetch(`/api/jobs/${jobId}`);
      setProgress($('#progressBar'), job.progress);
      setStatus(`Job #${jobId} is ${job.status} (${job.progress}%)`);
      if (job.status === 'completed') {
        clearInterval(timer);
        const result = await apiFetch(`/api/jobs/${jobId}/result`);
        const blob = await result.blob();
        const afterUrl = URL.createObjectURL(blob);
        renderComparison($('#comparison'), beforeUrl, afterUrl);
        $('#downloadLink').href = afterUrl;
        $('#downloadLink').download = `job_${jobId}.png`;
        setStatus(`Completed at ${formatDate(new Date().toISOString())}`);
      }
      if (job.status === 'failed') {
        clearInterval(timer);
        toast(job.error_message || 'Job failed', 'error');
      }
    } catch (error) {
      clearInterval(timer);
      toast(error.message, 'error');
    }
  }, 1500);
}

window.addEventListener('DOMContentLoaded', () => {
  const uploadZoneHost = $('#uploadZone');
  uploadZoneHost.replaceWith(createUploadZone({
    onFileSelected: (file) => {
      selectedFile = file;
      setPreview($('#preview'), file);
      setStatus(`Selected ${file.name}`);
    },
  }));
  $('#generateBtn').addEventListener('click', startEditing);
  $('#downloadLink').removeAttribute('href');
});

