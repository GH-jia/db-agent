<script setup>
import { computed, ref } from "vue";
import ChatPage from "./pages/ChatPage.vue";
import DbConnectionPage from "./pages/DbConnectionPage.vue";

const activePage = ref("chat");

const menuItems = [
  {
    key: "chat",
    label: "智能问答",
    description: "自然语言查询与元数据问答",
  },
  {
    key: "connections",
    label: "数据源管理",
    description: "维护 Agent 可使用的数据库连接",
  },
];

const activeMenu = computed(() => menuItems.find((item) => item.key === activePage.value));
</script>

<template>
  <main class="app-layout">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">DB</div>
        <div>
          <p>Database Agent</p>
          <span>数据查询工作台</span>
        </div>
      </div>

      <nav class="nav-menu" aria-label="主菜单">
        <button
          v-for="item in menuItems"
          :key="item.key"
          type="button"
          class="nav-item"
          :class="{ active: activePage === item.key }"
          @click="activePage = item.key"
        >
          <strong>{{ item.label }}</strong>
          <span>{{ item.description }}</span>
        </button>
      </nav>
    </aside>

    <section class="main-panel">
      <div class="mobile-topbar">
        <div>
          <p class="eyebrow">当前模块</p>
          <h1>{{ activeMenu?.label }}</h1>
        </div>
        <select v-model="activePage" aria-label="切换页面">
          <option v-for="item in menuItems" :key="item.key" :value="item.key">
            {{ item.label }}
          </option>
        </select>
      </div>

      <ChatPage v-if="activePage === 'chat'" />
      <DbConnectionPage v-else />
    </section>
  </main>
</template>
