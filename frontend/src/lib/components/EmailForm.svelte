<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  let email = '';
  let level = 'full';
  let loading = false;

  const levels = [
    { value: 'syntax', label: '语法验证', desc: '仅检查格式' },
    { value: 'dns', label: 'DNS验证', desc: '检查域名和MX记录' },
    { value: 'smtp', label: 'SMTP验证', desc: '连接邮件服务器' },
    { value: 'full', label: '完整验证', desc: '全面检测（推荐）' },
  ];

  function handleSubmit() {
    if (!email.trim()) return;
    dispatch('validate', { email: email.trim(), level });
  }

  export function setLoading(value) {
    loading = value;
  }

  export function clear() {
    email = '';
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="email-form">
  <div class="input-group">
    <input
      type="email"
      bind:value={email}
      placeholder="输入邮箱地址，如 example@gmail.com"
      disabled={loading}
      class="email-input"
    />
    <button type="submit" disabled={loading || !email.trim()} class="submit-btn">
      {#if loading}
        <span class="spinner"></span>
        验证中...
      {:else}
        验证邮箱
      {/if}
    </button>
  </div>

  <div class="level-selector">
    <span class="level-label">验证级别：</span>
    <div class="level-options">
      {#each levels as { value, label, desc }}
        <label class="level-option" class:selected={level === value}>
          <input type="radio" bind:group={level} {value} disabled={loading} />
          <span class="option-content">
            <span class="option-label">{label}</span>
            <span class="option-desc">{desc}</span>
          </span>
        </label>
      {/each}
    </div>
  </div>
</form>

<style>
  .email-form {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }

  .input-group {
    display: flex;
    gap: 0.75rem;
  }

  .email-input {
    flex: 1;
    padding: 0.875rem 1rem;
    font-size: 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .email-input:focus {
    outline: none;
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  }

  .email-input:disabled {
    background: #f9fafb;
  }

  .submit-btn {
    padding: 0.875rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    color: white;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
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

  .level-selector {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
  }

  .level-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
  }

  .level-options {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  .level-option {
    display: flex;
    align-items: center;
    padding: 0.5rem 0.75rem;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .level-option:hover {
    border-color: #c7d2fe;
    background: #f5f3ff;
  }

  .level-option.selected {
    border-color: #6366f1;
    background: #eef2ff;
  }

  .level-option input {
    display: none;
  }

  .option-content {
    display: flex;
    flex-direction: column;
  }

  .option-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
  }

  .option-desc {
    font-size: 0.75rem;
    color: #6b7280;
  }

  @media (max-width: 640px) {
    .input-group {
      flex-direction: column;
    }

    .level-options {
      flex-direction: column;
    }
  }
</style>
