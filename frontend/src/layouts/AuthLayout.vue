<template>
  <div class="auth-layout">
    <div class="auth-left">
      <div class="brand-content">
        <h1 class="brand-title" @click="$router.push('/')">八股文刷题</h1>
        <p class="brand-slogan">高效备战技术面试，个性化推荐助你查漏补缺</p>
        <div class="brand-decoration">
          <div class="deco-line"></div>
          <div class="deco-line"></div>
          <div class="deco-line"></div>
        </div>
      </div>
    </div>
    <div class="auth-right">
      <div class="auth-form-container">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
}

.auth-left {
  width: 50%;
  background: var(--bg-page);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xxl);
}

.brand-content {
  text-align: center;
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  cursor: pointer;
  margin-bottom: var(--spacing-md);
}

.brand-slogan {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xxl);
}

.brand-decoration {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.deco-line {
  height: 1px;
  background: var(--border-default);
  border-radius: 1px;
}

.deco-line:nth-child(1) {
  width: 200px;
}

.deco-line:nth-child(2) {
  width: 140px;
}

.deco-line:nth-child(3) {
  width: 80px;
}

.auth-right {
  width: 50%;
  background: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xxl);
}

.auth-form-container {
  width: 100%;
  max-width: 400px;
}
</style>