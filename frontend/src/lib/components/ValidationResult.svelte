<script>
  export let result = null;

  function getRiskColor(risk) {
    const colors = {
      low: '#10b981',
      medium: '#f59e0b',
      high: '#ef4444',
      invalid: '#6b7280',
    };
    return colors[risk] || '#6b7280';
  }

  function getRiskLabel(risk) {
    const labels = {
      low: '低风险',
      medium: '中等风险',
      high: '高风险',
      invalid: '无效',
    };
    return labels[risk] || '未知';
  }

  function getScoreGrade(score) {
    if (score >= 80) return 'A';
    if (score >= 60) return 'B';
    if (score >= 40) return 'C';
    return 'D';
  }
</script>

{#if result}
  <div class="result-card">
    <!-- 头部概览 -->
    <div class="result-header">
      <div class="email-info">
        <span class="email-address">{result.email}</span>
        <span
          class="risk-badge"
          style="background-color: {getRiskColor(result.risk_level)}"
        >
          {getRiskLabel(result.risk_level)}
        </span>
      </div>
      <div class="score-circle" style="--score-color: {getRiskColor(result.risk_level)}">
        <span class="score-value">{result.score}</span>
        <span class="score-grade">{getScoreGrade(result.score)}</span>
      </div>
    </div>

    <!-- 验证状态 -->
    <div class="validation-status">
      <div class="status-item" class:valid={result.valid}>
        <span class="status-icon">{result.valid ? '✓' : '✗'}</span>
        <span class="status-text">{result.valid ? '邮箱有效' : '邮箱无效'}</span>
      </div>
      <p class="message">{result.message}</p>
    </div>

    <!-- 详细结果 -->
    <div class="details">
      <!-- 语法验证 -->
      <div class="detail-section">
        <h4 class="section-title">
          <span class="check-icon" class:valid={result.syntax?.valid}>
            {result.syntax?.valid ? '✓' : '✗'}
          </span>
          语法验证
        </h4>
        {#if result.syntax?.valid}
          <div class="detail-content">
            <div class="detail-row">
              <span class="detail-label">用户名</span>
              <span class="detail-value">{result.syntax.local_part}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">域名</span>
              <span class="detail-value">{result.syntax.domain}</span>
            </div>
          </div>
        {:else}
          <p class="error-text">{result.syntax?.error}</p>
        {/if}
      </div>

      <!-- DNS验证 -->
      {#if result.dns}
        <div class="detail-section">
          <h4 class="section-title">
            <span class="check-icon" class:valid={result.dns.has_mx}>
              {result.dns.has_mx ? '✓' : '✗'}
            </span>
            DNS验证
          </h4>
          <div class="detail-content">
            <div class="detail-row">
              <span class="detail-label">MX记录</span>
              <span class="detail-value">{result.dns.has_mx ? '存在' : '不存在'}</span>
            </div>
            {#if result.dns.mx_records?.length > 0}
              <div class="mx-records">
                <span class="detail-label">邮件服务器</span>
                <ul class="mx-list">
                  {#each result.dns.mx_records.slice(0, 3) as mx}
                    <li>{mx}</li>
                  {/each}
                  {#if result.dns.mx_records.length > 3}
                    <li class="more">+{result.dns.mx_records.length - 3} 更多</li>
                  {/if}
                </ul>
              </div>
            {/if}
            {#if result.dns.error}
              <p class="error-text">{result.dns.error}</p>
            {/if}
          </div>
        </div>
      {/if}

      <!-- SMTP验证 -->
      {#if result.smtp}
        <div class="detail-section">
          <h4 class="section-title">
            <span class="check-icon" class:valid={result.smtp.accepts_mail}>
              {result.smtp.accepts_mail ? '✓' : result.smtp.connectable ? '~' : '✗'}
            </span>
            SMTP验证
          </h4>
          <div class="detail-content">
            <div class="detail-row">
              <span class="detail-label">可连接</span>
              <span class="detail-value">{result.smtp.connectable ? '是' : '否'}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">接受邮件</span>
              <span class="detail-value">{result.smtp.accepts_mail ? '是' : '未确认'}</span>
            </div>
            {#if result.smtp.is_catch_all !== null}
              <div class="detail-row">
                <span class="detail-label">Catch-all</span>
                <span class="detail-value">{result.smtp.is_catch_all ? '是' : '否'}</span>
              </div>
            {/if}
            {#if result.smtp.error}
              <p class="warning-text">{result.smtp.error}</p>
            {/if}
          </div>
        </div>
      {/if}

      <!-- 深度分析 -->
      {#if result.deep_analysis}
        <div class="detail-section">
          <h4 class="section-title">
            <span class="check-icon valid">✓</span>
            深度分析
          </h4>
          <div class="detail-content">
            <div class="tags">
              {#if result.deep_analysis.is_disposable}
                <span class="tag danger">一次性邮箱</span>
              {/if}
              {#if result.deep_analysis.is_role_account}
                <span class="tag warning">角色账户</span>
              {/if}
              {#if result.deep_analysis.is_free_provider}
                <span class="tag info">
                  {result.deep_analysis.provider_name || '免费邮箱'}
                </span>
              {:else}
                <span class="tag success">企业邮箱</span>
              {/if}
            </div>
            {#if result.deep_analysis.suggestions?.length > 0}
              <ul class="suggestions">
                {#each result.deep_analysis.suggestions as suggestion}
                  <li>{suggestion}</li>
                {/each}
              </ul>
            {/if}
          </div>
        </div>
      {/if}
    </div>

    <!-- 验证时间 -->
    <div class="footer">
      <span class="time">验证耗时: {result.validation_time_ms}ms</span>
    </div>
  </div>
{/if}

<style>
  .result-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 1.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }

  .email-info {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .email-address {
    font-size: 1.125rem;
    font-weight: 600;
    word-break: break-all;
  }

  .risk-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 9999px;
    width: fit-content;
  }

  .score-circle {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 3px solid var(--score-color);
  }

  .score-value {
    font-size: 1.5rem;
    font-weight: 700;
  }

  .score-grade {
    font-size: 0.75rem;
    opacity: 0.9;
  }

  .validation-status {
    padding: 1rem 1.5rem;
    background: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
  }

  .status-item.valid {
    color: #10b981;
  }

  .status-item:not(.valid) {
    color: #ef4444;
  }

  .status-icon {
    font-size: 1.25rem;
  }

  .message {
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #6b7280;
  }

  .details {
    padding: 1rem 1.5rem;
  }

  .detail-section {
    padding: 1rem 0;
    border-bottom: 1px solid #e5e7eb;
  }

  .detail-section:last-child {
    border-bottom: none;
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0 0 0.75rem 0;
    font-size: 0.9375rem;
    font-weight: 600;
    color: #374151;
  }

  .check-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.25rem;
    height: 1.25rem;
    font-size: 0.75rem;
    border-radius: 50%;
    background: #fee2e2;
    color: #ef4444;
  }

  .check-icon.valid {
    background: #d1fae5;
    color: #10b981;
  }

  .detail-content {
    padding-left: 1.75rem;
  }

  .detail-row {
    display: flex;
    justify-content: space-between;
    padding: 0.25rem 0;
    font-size: 0.875rem;
  }

  .detail-label {
    color: #6b7280;
  }

  .detail-value {
    color: #374151;
    font-weight: 500;
  }

  .mx-records {
    margin-top: 0.5rem;
  }

  .mx-list {
    margin: 0.25rem 0 0 0;
    padding-left: 1rem;
    font-size: 0.8125rem;
    color: #6b7280;
  }

  .mx-list li {
    padding: 0.125rem 0;
  }

  .mx-list .more {
    color: #9ca3af;
    font-style: italic;
  }

  .error-text {
    margin: 0.5rem 0 0 0;
    font-size: 0.8125rem;
    color: #ef4444;
  }

  .warning-text {
    margin: 0.5rem 0 0 0;
    font-size: 0.8125rem;
    color: #f59e0b;
  }

  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .tag {
    padding: 0.25rem 0.625rem;
    font-size: 0.75rem;
    font-weight: 500;
    border-radius: 4px;
  }

  .tag.success {
    background: #d1fae5;
    color: #065f46;
  }

  .tag.warning {
    background: #fef3c7;
    color: #92400e;
  }

  .tag.danger {
    background: #fee2e2;
    color: #991b1b;
  }

  .tag.info {
    background: #dbeafe;
    color: #1e40af;
  }

  .suggestions {
    margin: 0.75rem 0 0 0;
    padding-left: 1rem;
    font-size: 0.8125rem;
    color: #6b7280;
  }

  .suggestions li {
    padding: 0.125rem 0;
  }

  .footer {
    padding: 0.75rem 1.5rem;
    background: #f9fafb;
    border-top: 1px solid #e5e7eb;
  }

  .time {
    font-size: 0.75rem;
    color: #9ca3af;
  }
</style>
