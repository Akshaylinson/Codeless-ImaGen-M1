export function setLoading(element, loading, text = 'Loading...') {
  if (!element) return;
  element.dataset.loading = loading ? 'true' : 'false';
  element.textContent = loading ? text : element.dataset.defaultText || element.textContent;
}

