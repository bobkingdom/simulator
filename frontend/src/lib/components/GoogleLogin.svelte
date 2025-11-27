<script>
  import { onMount } from 'svelte';
  import { user, isLoggedIn, handleGoogleLogin, logout, restoreSession } from '../stores/auth.js';

  // Google Client ID - 用户需要替换成自己的
  export let clientId = '';

  let googleLoaded = false;

  onMount(() => {
    // 恢复登录状态
    restoreSession();

    // 如果没有 clientId，不加载 Google SDK
    if (!clientId) {
      console.warn('Google Client ID 未配置');
      return;
    }

    // 加载 Google Identity Services SDK
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = initializeGoogle;
    document.head.appendChild(script);
  });

  function initializeGoogle() {
    if (!window.google || $isLoggedIn) return;

    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: handleCredentialResponse,
      auto_select: true,
      cancel_on_tap_outside: false,
    });

    // 显示 One Tap 弹窗
    window.google.accounts.id.prompt();

    googleLoaded = true;
  }

  function handleCredentialResponse(response) {
    handleGoogleLogin(response);
  }

  function handleLogout() {
    logout();
    // 重新显示登录弹窗
    if (googleLoaded && window.google) {
      window.google.accounts.id.prompt();
    }
  }
</script>

<div class="auth-container">
  {#if $isLoggedIn && $user}
    <div class="user-info">
      <img src={$user.picture} alt={$user.name} class="avatar" />
      <div class="user-details">
        <span class="user-name">{$user.name}</span>
        <span class="user-email">{$user.email}</span>
      </div>
      <button on:click={handleLogout} class="logout-btn">登出</button>
    </div>
  {:else if clientId}
    <div class="login-prompt">
      <span>使用 Google 账号登录</span>
      <div id="g_id_onload"
        data-client_id={clientId}
        data-context="signin"
        data-ux_mode="popup"
        data-callback="handleCredentialResponse"
        data-auto_prompt="false">
      </div>
      <div class="g_id_signin"
        data-type="standard"
        data-shape="rectangular"
        data-theme="outline"
        data-text="signin_with"
        data-size="large"
        data-logo_alignment="left">
      </div>
    </div>
  {:else}
    <div class="no-auth">
      <span class="guest-label">访客模式</span>
    </div>
  {/if}
</div>

<style>
  .auth-container {
    display: flex;
    align-items: center;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid #e5e7eb;
  }

  .user-details {
    display: flex;
    flex-direction: column;
  }

  .user-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
  }

  .user-email {
    font-size: 0.75rem;
    color: #6b7280;
  }

  .logout-btn {
    padding: 0.375rem 0.75rem;
    font-size: 0.8125rem;
    color: #6b7280;
    background: #f3f4f6;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s;
  }

  .logout-btn:hover {
    background: #e5e7eb;
    color: #374151;
  }

  .login-prompt {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 0.875rem;
    color: #6b7280;
  }

  .no-auth {
    display: flex;
    align-items: center;
  }

  .guest-label {
    padding: 0.375rem 0.75rem;
    font-size: 0.8125rem;
    color: #6b7280;
    background: #f3f4f6;
    border-radius: 6px;
  }
</style>
