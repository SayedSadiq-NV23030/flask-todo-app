document.addEventListener('DOMContentLoaded', () => {
  const listEl = document.getElementById('task-list');
  const form = document.getElementById('add-form');
  const input = document.getElementById('todo-input');
  const descInput = document.getElementById('todo-desc');
  const tagsInput = document.getElementById('todo-tags');
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
  const tagFilter = document.getElementById('tag-filter');
  const filtersEl = document.getElementById('filters');
  const statTotal = document.getElementById('stat-total');
  const statCompleted = document.getElementById('stat-completed');
  const statOverdue = document.getElementById('stat-overdue');
  const statLast7 = document.getElementById('stat-last7');

  let tasks = [];

  function buildQuery() {
    const params = new URLSearchParams();
    const q = ((searchInput && searchInput.value) || '').trim();
    const status = (filtersEl && filtersEl.querySelector('.filter.active') && filtersEl.querySelector('.filter.active').getAttribute('data-filter')) || 'all';
    const sort = (sortSelect && sortSelect.value) || 'created_at';
    const order = (orderSelect && orderSelect.value) || 'desc';
    const priority = (priorityFilter && priorityFilter.value) || '';
    const due = (dueFilter && dueFilter.value) || '';
    const tag = (tagFilter && tagFilter.value) || '';

    if (q) params.set('q', q);
    if (status && status !== 'all') params.set('status', status);
    if (priority) params.set('priority', priority);
    if (due) params.set('due', due);
    if (tag) params.set('tag', tag);
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
      const subtasks = Array.isArray(t.subtasks) ? t.subtasks : [];
      const doneCount = subtasks.filter((s) => s.is_done).length;
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
            ${Array.isArray(t.tags) && t.tags.length ? `<div class="task-tags">${t.tags.map((tag) => `<span class="task-tag">${escapeHtml(tag)}</span>`).join('')}</div>` : ''}
            <div class="subtasks-wrap">
              <div class="subtasks-header">Checklist: ${doneCount}/${subtasks.length}</div>
              ${subtasks.length ? `<div class="subtasks-list">${subtasks.map((s) => `
                <div class="subtask-row">
                  <button class="subtask-toggle ${s.is_done ? 'done' : ''}" data-task-id="${t.id}" data-subtask-id="${s.id}">${s.is_done ? '✓' : ''}</button>
                  <span class="subtask-title ${s.is_done ? 'done' : ''}">${escapeHtml(s.title)}</span>
                  <button class="subtask-delete" data-task-id="${t.id}" data-subtask-id="${s.id}">x</button>
                </div>
              `).join('')}</div>` : '<div class="subtask-empty">No subtasks</div>'}
              <form class="subtask-form" data-task-id="${t.id}">
                <input class="subtask-input" maxlength="120" placeholder="Add subtask..." />
                <button type="submit" class="btn btn-ghost">Add</button>
              </form>
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

      li.querySelectorAll('.subtask-form').forEach((subtaskForm) => {
        subtaskForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const taskId = subtaskForm.getAttribute('data-task-id');
          const inputEl = subtaskForm.querySelector('.subtask-input');
          const title = ((inputEl && inputEl.value) || '').trim();
          if (!title) return;
          await addSubtask(taskId, title);
          if (inputEl) inputEl.value = '';
        });
      });

      li.querySelectorAll('.subtask-toggle').forEach((button) => {
        button.addEventListener('click', async (e) => {
          const taskId = e.target.getAttribute('data-task-id');
          const subtaskId = e.target.getAttribute('data-subtask-id');
          const task = tasks.find((x) => x.id === taskId);
          if (!task) return;
          const subtask = (task.subtasks || []).find((s) => s.id === subtaskId);
          if (!subtask) return;
          await toggleSubtask(taskId, subtaskId, !subtask.is_done);
        });
      });

      li.querySelectorAll('.subtask-delete').forEach((button) => {
        button.addEventListener('click', async (e) => {
          const taskId = e.target.getAttribute('data-task-id');
          const subtaskId = e.target.getAttribute('data-subtask-id');
          await deleteSubtask(taskId, subtaskId);
        });
      });

      listEl.appendChild(li);
      setTimeout(() => {
        li.classList.remove('fade-in');
      }, 250);
    });
  }

  async function addTask(title, description, tags, priority, dueDate) {
    const payload = {
      title,
      description,
      tags,
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
    await refreshAll();
  }

  async function deleteTask(id) {
    const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
    if (!res.ok) {
      throw new Error('Failed to delete task');
    }
    await refreshAll();
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
    await refreshAll();
  }

  async function clearAllTasks() {
    if (!confirm('Clear all tasks?')) return;
    const ids = tasks.map((t) => t.id);
    await Promise.all(ids.map((id) => fetch(`/api/tasks/${id}`, { method: 'DELETE' })));
    await refreshAll();
  }

  async function addSubtask(taskId, title) {
    const res = await fetch(`/api/tasks/${taskId}/subtasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    if (!res.ok) {
      throw new Error('Failed to add subtask');
    }
    await refreshAll();
  }

  async function toggleSubtask(taskId, subtaskId, isDone) {
    const res = await fetch(`/api/tasks/${taskId}/subtasks/${subtaskId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_done: isDone }),
    });
    if (!res.ok) {
      throw new Error('Failed to update subtask');
    }
    await refreshAll();
  }

  async function deleteSubtask(taskId, subtaskId) {
    const res = await fetch(`/api/tasks/${taskId}/subtasks/${subtaskId}`, {
      method: 'DELETE',
    });
    if (!res.ok) {
      throw new Error('Failed to delete subtask');
    }
    await refreshAll();
  }

  async function fetchTags() {
    const selected = (tagFilter && tagFilter.value) || '';
    const res = await fetch('/api/tags');
    if (!res.ok || !tagFilter) {
      return;
    }

    const data = await res.json();
    const tags = data.tags || [];
    tagFilter.innerHTML = '<option value="">Tag: All</option>';

    tags.forEach((tag) => {
      const option = document.createElement('option');
      option.value = tag;
      option.textContent = `Tag: ${tag}`;
      tagFilter.appendChild(option);
    });

    if (selected && tags.includes(selected)) {
      tagFilter.value = selected;
    }
  }

  async function fetchStats() {
    const res = await fetch('/api/stats');
    if (!res.ok) {
      return;
    }

    const stats = await res.json();
    if (statTotal) statTotal.textContent = String(stats.total_tasks || 0);
    if (statCompleted) statCompleted.textContent = String(stats.completed_tasks || 0);
    if (statOverdue) statOverdue.textContent = String(stats.overdue_tasks || 0);
    if (statLast7) statLast7.textContent = String(stats.completed_last_7_days || 0);
  }

  async function refreshAll() {
    await Promise.all([fetchTasks(), fetchTags(), fetchStats()]);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const v = input.value && input.value.trim();
    if (!v) return;

    try {
      await addTask(v, descInput && descInput.value, tagsInput && tagsInput.value, priorityInput && priorityInput.value, dueInput && dueInput.value);
      input.value = '';
      if (descInput) descInput.value = '';
      if (tagsInput) tagsInput.value = '';
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
      await refreshAll();
    });
  }
  if (sortSelect) {
    sortSelect.addEventListener('change', async () => {
      await refreshAll();
    });
  }
  if (orderSelect) {
    orderSelect.addEventListener('change', async () => {
      await refreshAll();
    });
  }
  if (priorityFilter) {
    priorityFilter.addEventListener('change', async () => {
      await refreshAll();
    });
  }
  if (dueFilter) {
    dueFilter.addEventListener('change', async () => {
      await refreshAll();
    });
  }
  if (tagFilter) {
    tagFilter.addEventListener('change', async () => {
      await refreshAll();
    });
  }
  if (filtersEl) {
    filtersEl.addEventListener('click', async (e) => {
      if (!e.target.classList.contains('filter')) return;
      filtersEl.querySelectorAll('.filter').forEach((b) => b.classList.remove('active'));
      e.target.classList.add('active');
      await refreshAll();
    });
  }

  function escapeHtml(str) {
    return String(str || '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  }

  // Theme handling
  function setTheme(t) { if (t === 'dark') document.documentElement.setAttribute('data-theme', 'dark'); else document.documentElement.removeAttribute('data-theme'); try { localStorage.setItem('site-theme', t); } catch (e) {} }
  try { const saved = localStorage.getItem('site-theme') || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'); setTheme(saved); } catch(e) {}
  themeToggle && themeToggle.addEventListener('click', () => { const cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'; setTheme(cur === 'dark' ? 'light' : 'dark'); });

  refreshAll().catch((err) => {
    console.error(err);
  });
});
