/**
 * 邮箱验证 API 服务
 */

// API 基础地址
// 开发时通过 Vite 代理访问后端，使用空字符串
// 生产时可通过环境变量配置
const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * 验证单个邮箱
 * @param {string} email - 邮箱地址
 * @param {string} level - 验证级别: syntax, dns, smtp, full
 * @param {number} timeout - 超时时间（秒）
 * @returns {Promise<Object>} 验证结果
 */
export async function validateEmail(email, level = 'full', timeout = 10) {
  const url = `${API_BASE}/api/v1/validate/${encodeURIComponent(email)}?level=${level}&timeout=${timeout}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`验证失败: ${response.status}`);
  }

  return response.json();
}

/**
 * 批量验证邮箱
 * @param {string[]} emails - 邮箱地址列表
 * @param {string} level - 验证级别
 * @param {number} timeout - 超时时间
 * @returns {Promise<Object>} 批量验证结果
 */
export async function validateBatch(emails, level = 'full', timeout = 10) {
  const url = `${API_BASE}/api/v1/validate/batch`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      emails,
      level,
      timeout,
    }),
  });

  if (!response.ok) {
    throw new Error(`批量验证失败: ${response.status}`);
  }

  return response.json();
}

/**
 * 快速验证
 * @param {string} email - 邮箱地址
 * @returns {Promise<Object>} 简化的验证结果
 */
export async function quickCheck(email) {
  const url = `${API_BASE}/api/v1/check/${encodeURIComponent(email)}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`验证失败: ${response.status}`);
  }

  return response.json();
}

/**
 * 健康检查
 * @returns {Promise<Object>} 服务状态
 */
export async function healthCheck() {
  const url = `${API_BASE}/api/v1/health`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`服务不可用: ${response.status}`);
  }

  return response.json();
}
