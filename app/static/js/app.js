// Full client-side data model + SPA logic
document.addEventListener('DOMContentLoaded', () => {
  const KEY_TASKS = 'todo.tasks.v1';
  const listEl = document.getElementById('task-list');
  const form = document.getElementById('add-form');
  const input = document.getElementById('todo-input');
  const descInput = document.getElementById('todo-desc');
  const priorityInput = document.getElementById('todo-priority');
  const dueInput = document.getElementById('todo-due');
  const clearAllBtn = document.getElementById('clear-all');
  const themeToggle = document.getElementById('theme-toggle');
  const emptyEl = document.getElementById('empty-state');
  const searchInput = document.getElementById('search-input');
  const sortSelect = document.getElementById('sort-select');
  const filtersEl = document.getElementById('filters');

  function loadTasks() { try { return JSON.parse(localStorage.getItem(KEY_TASKS) || '[]'); } catch (e) { return []; } }
  function saveTasks(t) { localStorage.setItem(KEY_TASKS, JSON.stringify(t)); }
  function uid() { return 't_' + Math.random().toString(36).slice(2, 9); }

  let tasks = loadTasks();

  function applyFiltersAndSort() {
    const q = (searchInput && searchInput.value || '').toLowerCase().trim();
    const activeFilter = (filtersEl && filtersEl.querySelector('.filter.active') && filtersEl.querySelector('.filter.active').getAttribute('data-filter')) || 'all';
    const sortBy = (sortSelect && sortSelect.value) || 'created';

    let out = tasks.slice();
    // search
    if (q) out = out.filter(t => (t.title||'').toLowerCase().includes(q) || (t.description||'').toLowerCase().includes(q));
    // filter by status
    if (activeFilter === 'active') out = out.filter(t => !t.done);
    if (activeFilter === 'completed') out = out.filter(t => t.done);

    // sort
    out.sort((a,b) => {
      if (sortBy === 'due') { return (a.due_date || '').localeCompare(b.due_date || ''); }
      if (sortBy === 'priority') { return (a.priority||99) - (b.priority||99); }
      if (sortBy === 'title') { return (a.title||'').localeCompare(b.title||''); }
      // created
      return (b.createdAt || '').localeCompare(a.createdAt || '');
    });
    return out;
  }

  function render() {
    const visible = applyFiltersAndSort();
    listEl.innerHTML = '';
    if (!visible.length) { if (emptyEl) emptyEl.style.display = 'block'; return; }
    if (emptyEl) emptyEl.style.display = 'none';
    visible.forEach(t => {
      const li = document.createElement('li');
      li.className = 'task-card fade-in';
      li.innerHTML = `
        <div style="display:flex;gap:12px;align-items:center">
          <button class="btn-icon checkbox" data-id="${t.id}" aria-pressed="${t.done ? 'true' : 'false'}">${t.done ? '✓' : ''}</button>
          <div>
            <div class="task-title">${escapeHtml(t.title)}</div>
            <div class="task-meta">${t.description ? escapeHtml(t.description) + ' • ' : ''}${t.due_date ? 'Due: ' + escapeHtml(t.due_date) + ' • ' : ''}${t.createdAt || ''}</div>
          </div>
        </div>
        <div>
          <button class="btn btn-ghost delete" data-id="${t.id}">Delete</button>
        </div>
      `;

      // attach events
      li.querySelector('.delete').addEventListener('click', (e) => { const id = e.target.getAttribute('data-id'); deleteTask(id); });
      li.querySelector('.checkbox').addEventListener('click', (e) => { const id = e.target.getAttribute('data-id'); toggleDone(id); });
      listEl.appendChild(li);
      // small entrance animation
      setTimeout(() => { li.classList.remove('fade-in'); }, 250);
    });
  }

  function addTask(title, description, priority, due_date) { const t = { id: uid(), title: title.trim(), description: (description||'').trim(), priority: Number(priority)||2, due_date: due_date||'', createdAt: new Date().toISOString(), done: false }; tasks.unshift(t); saveTasks(tasks); render(); }
  function deleteTask(id) { tasks = tasks.filter(x => x.id !== id); saveTasks(tasks); render(); }
  function toggleDone(id) { tasks = tasks.map(x => x.id === id ? Object.assign({}, x, { done: !x.done }) : x); saveTasks(tasks); render(); }

  form.addEventListener('submit', (e) => { e.preventDefault(); const v = input.value && input.value.trim(); if (!v) return; addTask(v, descInput && descInput.value, priorityInput && priorityInput.value, dueInput && dueInput.value); input.value = ''; if(descInput) descInput.value=''; if(dueInput) dueInput.value=''; input.focus(); });
  clearAllBtn.addEventListener('click', () => { if (!confirm('Clear all tasks?')) return; tasks = []; saveTasks(tasks); render(); });

  // search / filter bindings
  if (searchInput) searchInput.addEventListener('input', () => render());
  if (sortSelect) sortSelect.addEventListener('change', () => render());
  if (filtersEl) filtersEl.addEventListener('click', (e) => { if (!e.target.classList.contains('filter')) return; filtersEl.querySelectorAll('.filter').forEach(b=>b.classList.remove('active')); e.target.classList.add('active'); render(); });

  function escapeHtml(str) { return String(str||'').replace(/[&<>\\\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

  // Theme handling
  function setTheme(t) { if (t === 'dark') document.documentElement.setAttribute('data-theme', 'dark'); else document.documentElement.removeAttribute('data-theme'); try { localStorage.setItem('site-theme', t); } catch (e) {} }
  try { const saved = localStorage.getItem('site-theme') || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'); setTheme(saved); } catch(e) {}
  themeToggle && themeToggle.addEventListener('click', () => { const cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'; setTheme(cur === 'dark' ? 'light' : 'dark'); });

  render();
});
