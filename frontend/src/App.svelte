<script>
  import EmailForm from './lib/components/EmailForm.svelte';
  import ValidationResult from './lib/components/ValidationResult.svelte';
  import BatchValidator from './lib/components/BatchValidator.svelte';
  import GoogleLogin from './lib/components/GoogleLogin.svelte';
  import { validateEmail } from './lib/api/validator.js';

  // Google OAuth Client ID - 配置后启用登录功能
  const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

  let emailForm;
  let activeTab = 'single';
  let result = null;
  let loading = false;
  let error = null;

  async function handleValidate(event) {
    const { email, level } = event.detail;

    loading = true;
    error = null;
    result = null;

    if (emailForm) {
      emailForm.setLoading(true);
    }

    try {
      result = await validateEmail(email, level);
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
      if (emailForm) {
        emailForm.setLoading(false);
      }
    }
  }
</script>

<div class="app">
  <!-- 头部 -->
  <header class="header">
    <div class="header-content">
      <div class="logo">
        <span class="logo-icon">📧</span>
        <h1>邮箱验证器</h1>
      </div>
      <GoogleLogin clientId={GOOGLE_CLIENT_ID} />
    </div>
  </header>

  <!-- 主内容区 -->
  <main class="main">
    <div class="container">
      <!-- 介绍区域 -->
      <section class="intro">
        <h2>验证邮箱地址的有效性</h2>
        <p>不发送邮件，通过语法检查、DNS验证、SMTP连接等方式验证邮箱是否真实有效</p>
      </section>

      <!-- 标签切换 -->
      <div class="tabs">
        <button
          class="tab"
          class:active={activeTab === 'single'}
          on:click={() => activeTab = 'single'}
        >
          单个验证
        </button>
        <button
          class="tab"
          class:active={activeTab === 'batch'}
          on:click={() => activeTab = 'batch'}
        >
          批量验证
        </button>
      </div>

      <!-- 验证内容区 -->
      <div class="content">
        {#if activeTab === 'single'}
          <EmailForm bind:this={emailForm} on:validate={handleValidate} />

          {#if error}
            <div class="error-card">
              <span class="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          {/if}

          {#if result}
            <div class="result-wrapper">
              <ValidationResult {result} />
            </div>
          {/if}
        {:else}
          <BatchValidator />
        {/if}
      </div>

      <!-- 功能介绍 -->
      <section class="features">
        <h3>验证方式</h3>
        <div class="feature-grid">
          <div class="feature-card">
            <span class="feature-icon">📝</span>
            <h4>语法验证</h4>
            <p>检查邮箱格式是否符合 RFC 5322 标准</p>
          </div>
          <div class="feature-card">
            <span class="feature-icon">🌐</span>
            <h4>DNS验证</h4>
            <p>验证域名是否存在，检查MX记录配置</p>
          </div>
          <div class="feature-card">
            <span class="feature-icon">📡</span>
            <h4>SMTP验证</h4>
            <p>连接邮件服务器验证收件人是否存在</p>
          </div>
          <div class="feature-card">
            <span class="feature-icon">🔍</span>
            <h4>深度分析</h4>
            <p>检测一次性邮箱、角色账户等</p>
          </div>
        </div>
      </section>
    </div>
  </main>

  <!-- 页脚 -->
  <footer class="footer">
    <p>Email Validator API v1.0.0</p>
  </footer>
</div>

<style>
  :global(*) {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    min-height: 100vh;
  }

  .app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .header {
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .logo-icon {
    font-size: 1.75rem;
  }

  .logo h1 {
    font-size: 1.25rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .main {
    flex: 1;
    padding: 2rem;
  }

  .container {
    max-width: 800px;
    margin: 0 auto;
  }

  .intro {
    text-align: center;
    margin-bottom: 2rem;
  }

  .intro h2 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 0.5rem;
  }

  .intro p {
    font-size: 1rem;
    color: #6b7280;
  }

  .tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    background: white;
    padding: 0.375rem;
    border-radius: 10px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .tab {
    flex: 1;
    padding: 0.75rem 1.5rem;
    font-size: 0.9375rem;
    font-weight: 600;
    color: #6b7280;
    background: transparent;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .tab:hover {
    color: #374151;
    background: #f9fafb;
  }

  .tab.active {
    color: white;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  }

  .content {
    margin-bottom: 2rem;
  }

  .error-card {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
    padding: 1rem;
    background: #fee2e2;
    color: #991b1b;
    border-radius: 8px;
  }

  .result-wrapper {
    margin-top: 1.5rem;
  }

  .features {
    margin-top: 3rem;
  }

  .features h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 1rem;
    text-align: center;
  }

  .feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
  }

  .feature-card {
    background: white;
    padding: 1.25rem;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .feature-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .feature-icon {
    font-size: 2rem;
    display: block;
    margin-bottom: 0.75rem;
  }

  .feature-card h4 {
    font-size: 0.9375rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.375rem;
  }

  .feature-card p {
    font-size: 0.8125rem;
    color: #6b7280;
    line-height: 1.4;
  }

  .footer {
    background: white;
    padding: 1rem;
    text-align: center;
    border-top: 1px solid #e5e7eb;
  }

  .footer p {
    font-size: 0.8125rem;
    color: #9ca3af;
  }

  @media (max-width: 640px) {
    .header-content {
      padding: 1rem;
    }

    .main {
      padding: 1rem;
    }

    .intro h2 {
      font-size: 1.375rem;
    }

    .feature-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style>
