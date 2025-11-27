<script>
  import { createEventDispatcher } from 'svelte';
  import { validateBatch } from '../api/validator.js';

  const dispatch = createEventDispatcher();

  let emailsText = '';
  let level = 'full';
  let loading = false;
  let results = null;
  let error = null;

  $: emailList = emailsText
    .split(/[\n,;]/)
    .map(e => e.trim())
    .filter(e => e.length > 0);

  $: emailCount = emailList.length;

  async function handleSubmit() {
    if (emailCount === 0 || emailCount > 100) return;

    loading = true;
    error = null;

    try {
      results = await validateBatch(emailList, level, 10);
    } catch (e) {
      error = e.message;
      results = null;
    } finally {
      loading = false;
    }
  }

  function clearResults() {
    results = null;
    emailsText = '';
  }

  function getRiskColor(risk) {
    const colors = {
      low: '#10b981',
      medium: '#f59e0b',
      high: '#ef4444',
      invalid: '#6b7280',
    };
    return colors[risk] || '#6b7280';
  }

  function downloadCSV() {
    if (!results) return;

    const headers = ['邮箱', '有效', '评分', '风险等级', '说明'];
    const rows = results.results.map(r => [
      r.email,
      r.valid ? '是' : '否',
      r.score,
      r.risk_level,
      r.message,
    ]);

    const csv = [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n');

    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `email-validation-${Date.now()}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }
</script>

<div class="batch-validator">
  {#if !results}
    <form on:submit|preventDefault={handleSubmit} class="batch-form">
      <div class="form-header">
        <h3>批量验证</h3>
        <span class="email-count" class:warning={emailCount > 100}>
          {emailCount} / 100 个邮箱
        </span>
      </div>

      <textarea
        bind:value={emailsText}
        placeholder="输入邮箱地址，每行一个&#10;或用逗号、分号分隔&#10;&#10;例如：&#10;user1@example.com&#10;user2@gmail.com&#10;user3@company.com"
        rows="8"
        disabled={loading}
        class="email-textarea"
      ></textarea>

      <div class="form-actions">
        <select bind:value={level} disabled={loading} class="level-select">
          <option value="syntax">语法验证</option>
          <option value="dns">DNS验证</option>
          <option value="smtp">SMTP验证</option>
          <option value="full">完整验证</option>
        </select>

        <button
          type="submit"
          disabled={loading || emailCount === 0 || emailCount > 100}
          class="submit-btn"
        >
          {#if loading}
            <span class="spinner"></span>
            验证中...
          {:else}
            开始批量验证
          {/if}
        </button>
      </div>

      {#if error}
        <p class="error-message">{error}</p>
      {/if}
    </form>
  {:else}
    <div class="results-container">
      <div class="results-header">
        <h3>验证结果</h3>
        <div class="results-actions">
          <button on:click={downloadCSV} class="action-btn">
            📥 导出CSV
          </button>
          <button on:click={clearResults} class="action-btn secondary">
            🔄 重新验证
          </button>
        </div>
      </div>

      <div class="results-summary">
        <div class="summary-item">
          <span class="summary-value">{results.total}</span>
          <span class="summary-label">总数</span>
        </div>
        <div class="summary-item valid">
          <span class="summary-value">{results.valid_count}</span>
          <span class="summary-label">有效</span>
        </div>
        <div class="summary-item invalid">
          <span class="summary-value">{results.invalid_count}</span>
          <span class="summary-label">无效</span>
        </div>
      </div>

      <div class="results-list">
        {#each results.results as result}
          <div class="result-item" class:valid={result.valid}>
            <div class="result-main">
              <span class="result-email">{result.email}</span>
              <span class="result-score" style="color: {getRiskColor(result.risk_level)}">
                {result.score}分
              </span>
            </div>
            <div class="result-meta">
              <span class="result-status">{result.valid ? '✓ 有效' : '✗ 无效'}</span>
              <span class="result-risk">{result.risk_level}</span>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .batch-validator {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  .batch-form {
    padding: 1.5rem;
  }

  .form-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .form-header h3 {
    margin: 0;
    font-size: 1.125rem;
    color: #374151;
  }

  .email-count {
    font-size: 0.875rem;
    color: #6b7280;
  }

  .email-count.warning {
    color: #ef4444;
    font-weight: 600;
  }

  .email-textarea {
    width: 100%;
    padding: 0.875rem 1rem;
    font-size: 0.9375rem;
    font-family: inherit;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    resize: vertical;
    transition: border-color 0.2s;
  }

  .email-textarea:focus {
    outline: none;
    border-color: #6366f1;
  }

  .form-actions {
    display: flex;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .level-select {
    padding: 0.75rem 1rem;
    font-size: 0.9375rem;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    background: white;
    cursor: pointer;
  }

  .submit-btn {
    flex: 1;
    padding: 0.875rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    color: white;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .submit-btn:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  }

  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .spinner {
    width: 1rem;
    height: 1rem;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error-message {
    margin-top: 1rem;
    padding: 0.75rem 1rem;
    background: #fee2e2;
    color: #991b1b;
    border-radius: 8px;
    font-size: 0.875rem;
  }

  .results-container {
    padding: 1.5rem;
  }

  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .results-header h3 {
    margin: 0;
    font-size: 1.125rem;
    color: #374151;
  }

  .results-actions {
    display: flex;
    gap: 0.5rem;
  }

  .action-btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: #6366f1;
    background: #eef2ff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s;
  }

  .action-btn:hover {
    background: #e0e7ff;
  }

  .action-btn.secondary {
    color: #6b7280;
    background: #f3f4f6;
  }

  .action-btn.secondary:hover {
    background: #e5e7eb;
  }

  .results-summary {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .summary-item {
    flex: 1;
    padding: 1rem;
    background: #f9fafb;
    border-radius: 8px;
    text-align: center;
  }

  .summary-item.valid {
    background: #d1fae5;
  }

  .summary-item.invalid {
    background: #fee2e2;
  }

  .summary-value {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #374151;
  }

  .summary-item.valid .summary-value {
    color: #065f46;
  }

  .summary-item.invalid .summary-value {
    color: #991b1b;
  }

  .summary-label {
    font-size: 0.75rem;
    color: #6b7280;
  }

  .results-list {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
  }

  .result-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #e5e7eb;
  }

  .result-item:last-child {
    border-bottom: none;
  }

  .result-item.valid {
    background: #f0fdf4;
  }

  .result-item:not(.valid) {
    background: #fef2f2;
  }

  .result-main {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .result-email {
    font-size: 0.9375rem;
    color: #374151;
  }

  .result-score {
    font-weight: 600;
  }

  .result-meta {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.8125rem;
  }

  .result-status {
    color: #6b7280;
  }

  .result-risk {
    padding: 0.125rem 0.5rem;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
    color: #6b7280;
  }
</style>
