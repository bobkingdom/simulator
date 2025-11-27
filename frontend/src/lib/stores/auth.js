/**
 * 用户认证状态管理
 */
import { writable } from 'svelte/store';

// 用户信息 store
export const user = writable(null);

// 是否已登录
export const isLoggedIn = writable(false);

/**
 * 处理 Google One Tap 登录成功
 * @param {Object} response - Google 登录响应
 */
export function handleGoogleLogin(response) {
  // 解码 JWT token 获取用户信息
  const payload = decodeJwtPayload(response.credential);

  user.set({
    id: payload.sub,
    email: payload.email,
    name: payload.name,
    picture: payload.picture,
    token: response.credential,
  });

  isLoggedIn.set(true);

  // 保存到 localStorage
  localStorage.setItem('user', JSON.stringify({
    id: payload.sub,
    email: payload.email,
    name: payload.name,
    picture: payload.picture,
  }));
}

/**
 * 登出
 */
export function logout() {
  user.set(null);
  isLoggedIn.set(false);
  localStorage.removeItem('user');
}

/**
 * 从 localStorage 恢复登录状态
 */
export function restoreSession() {
  const savedUser = localStorage.getItem('user');
  if (savedUser) {
    try {
      const userData = JSON.parse(savedUser);
      user.set(userData);
      isLoggedIn.set(true);
    } catch (e) {
      localStorage.removeItem('user');
    }
  }
}

/**
 * 解码 JWT payload
 */
function decodeJwtPayload(token) {
  const base64Url = token.split('.')[1];
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  const jsonPayload = decodeURIComponent(
    atob(base64)
      .split('')
      .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
      .join('')
  );
  return JSON.parse(jsonPayload);
}
