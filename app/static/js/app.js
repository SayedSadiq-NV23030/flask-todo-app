document.addEventListener('DOMContentLoaded', () => {
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
  const orderSelect = document.getElementById('order-select');
  const priorityFilter = document.getElementById('priority-filter');
  const dueFilter = document.getElementById('due-filter');
  const filtersEl = document.getElementById('filters');

  let tasks = [];

  function buildQuery() {
    const params = new URLSearchParams();
    const q = ((searchInput && searchInput.value) || '').trim();
    const status = (filtersEl && filtersEl.querySelector('.filter.active') && filtersEl.querySelector('.filter.active').getAttribute('data-filter')) || 'all';
    const sort = (sortSelect && sortSelect.value) || 'created_at';
    const order = (orderSelect && orderSelect.value) || 'desc';
    const priority = (priorityFilter && priorityFilter.value) || '';
    const due = (dueFilter && dueFilter.value) || '';

    if (q) params.set('q', q);
    if (status && status !== 'all') params.set('status', status);
    if (priority) params.set('priority', priority);
    if (due) params.set('due', due);
    params.set('sort', sort);
    params.set('order', order);

    return params.toString();
  }

  function formatDateLabel(isoDate) {
    if (!isoDate) return '';
    return isoDate;
  }

  function priorityLabel(priority) {
    if (Number(priority) === 1) return 'High';
    if (Number(priority) === 3) return 'Low';
    return 'Medium';
  }

  function createdLabel(createdAt) {
    if (!createdAt) return '';
    const date = new Date(createdAt);
    if (Number.isNaN(date.getTime())) return '';
    return `Created: ${date.toLocaleDateString()}`;
  }

  async function fetchTasks() {
    const query = buildQuery();
    const res = await fetch(`/api/tasks${query ? `?${query}` : ''}`);
    if (!res.ok) {
      throw new Error('Failed to fetch tasks');
    }
    const data = await res.json();
    tasks = data.tasks || [];
    render();
  }

  function render() {
    listEl.innerHTML = '';
    if (!tasks.length) {
      if (emptyEl) emptyEl.style.display = 'block';
      return;
    }

    if (emptyEl) emptyEl.style.display = 'none';
    tasks.forEach((t) => {
      const li = document.createElement('li');
      li.className = 'task-card fade-in';
      li.innerHTML = `
        <div class="task-main">
          <button
            class="btn-icon checkbox ${t.status === 'completed' ? 'is-checked' : 'is-unchecked'}"
            data-id="${t.id}"
            aria-pressed="${t.status === 'completed' ? 'true' : 'false'}"
            aria-label="${t.status === 'completed' ? 'Mark task as active' : 'Mark task as completed'}"
            title="${t.status === 'completed' ? 'Mark as active' : 'Mark as completed'}"
          >
            <span class="checkbox-mark" aria-hidden="true">${t.status === 'completed' ? '✓' : ''}</span>
          </button>
          <div class="task-content">
            <div class="task-title">${escapeHtml(t.title)}</div>
            <div class="task-meta">
              ${t.description ? escapeHtml(t.description) + ' • ' : ''}Priority: ${priorityLabel(t.priority)}${t.due_date ? ' • Due: ' + escapeHtml(formatDateLabel(t.due_date)) : ''}${t.created_at ? ' • ' + escapeHtml(createdLabel(t.created_at)) : ''}
            </div>
            <div class="task-toggle-hint">${t.status === 'completed' ? 'Completed. Tap to uncheck.' : 'Tap circle to mark as done.'}</div>
          </div>
        </div>
        <div class="task-actions">
          <button class="btn btn-ghost delete" data-id="${t.id}">Delete</button>
        </div>
      `;

      li.querySelector('.delete').addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        deleteTask(id);
      });

      li.querySelector('.checkbox').addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        toggleDone(id);
      });

      listEl.appendChild(li);
      setTimeout(() => {
        li.classList.remove('fade-in');
      }, 250);
    });
  }

  async function addTask(title, description, priority, dueDate) {
    const payload = {
      title,
      description,
      priority,
      due_date: dueDate,
      status: 'active',
    };
    const res = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      throw new Error('Failed to add task');
    }
    await fetchTasks();
  }

  async function deleteTask(id) {
    const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
    if (!res.ok) {
      throw new Error('Failed to delete task');
    }
    await fetchTasks();
  }

  async function toggleDone(id) {
    const task = tasks.find((x) => x.id === id);
    if (!task) return;
    const next = task.status === 'completed' ? 'active' : 'completed';
    const res = await fetch(`/api/tasks/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: next }),
    });
    if (!res.ok) {
      throw new Error('Failed to update task');
    }
    await fetchTasks();
  }

  async function clearAllTasks() {
    if (!confirm('Clear all tasks?')) return;
    const ids = tasks.map((t) => t.id);
    await Promise.all(ids.map((id) => fetch(`/api/tasks/${id}`, { method: 'DELETE' })));
    await fetchTasks();
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const v = input.value && input.value.trim();
    if (!v) return;

    try {
      await addTask(v, descInput && descInput.value, priorityInput && priorityInput.value, dueInput && dueInput.value);
      input.value = '';
      if (descInput) descInput.value = '';
      if (dueInput) dueInput.value = '';
      input.focus();
    } catch (err) {
      console.error(err);
    }
  });

  clearAllBtn.addEventListener('click', async () => {
    try {
      await clearAllTasks();
    } catch (err) {
      console.error(err);
    }
  });

  if (searchInput) {
    searchInput.addEventListener('input', async () => {
      await fetchTasks();
    });
  }
  if (sortSelect) {
    sortSelect.addEventListener('change', async () => {
      await fetchTasks();
    });
  }
  if (orderSelect) {
    orderSelect.addEventListener('change', async () => {
      await fetchTasks();
    });
  }
  if (priorityFilter) {
    priorityFilter.addEventListener('change', async () => {
      await fetchTasks();
    });
  }
  if (dueFilter) {
    dueFilter.addEventListener('change', async () => {
      await fetchTasks();
    });
  }
  if (filtersEl) {
    filtersEl.addEventListener('click', async (e) => {
      if (!e.target.classList.contains('filter')) return;
      filtersEl.querySelectorAll('.filter').forEach((b) => b.classList.remove('active'));
      e.target.classList.add('active');
      await fetchTasks();
    });
  }

  function escapeHtml(str) {
    return String(str || '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  }

  // Theme handling
  function setTheme(t) { if (t === 'dark') document.documentElement.setAttribute('data-theme', 'dark'); else document.documentElement.removeAttribute('data-theme'); try { localStorage.setItem('site-theme', t); } catch (e) {} }
  try { const saved = localStorage.getItem('site-theme') || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'); setTheme(saved); } catch(e) {}
  themeToggle && themeToggle.addEventListener('click', () => { const cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'; setTheme(cur === 'dark' ? 'light' : 'dark'); });

  fetchTasks().catch((err) => {
    console.error(err);
  });
});
