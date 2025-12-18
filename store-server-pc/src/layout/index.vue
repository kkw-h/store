<template>
  <div class="app-wrapper">
    <Sidebar />
    <div class="main-container">
      <Header />
      <div class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.app-wrapper {
  display: flex;
  width: 100%;
  height: 100vh;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: $bg-color-page;
}

.app-main {
  flex: 1;
  padding: $spacing-md;
  overflow-y: auto;
  position: relative;
  
  /* Improve scrollbar in main area */
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #dcdfe6;
    border-radius: 4px;
    
    &:hover {
      background: #c0c4cc;
    }
  }
}
</style>
