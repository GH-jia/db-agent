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
    icon: "ChatDotRound",
  },
  {
    key: "connections",
    label: "数据源管理",
    description: "维护 Agent 可使用的数据库连接",
    icon: "DataAnalysis",
  },
];

const activeMenu = computed(() => menuItems.find((item) => item.key === activePage.value));
</script>

<template>
  <el-container class="app-layout">
    <el-aside class="sidebar" width="268px">
      <div class="brand">
        <div class="brand-mark">DB</div>
        <div>
          <p>Database Agent</p>
          <span>数据查询工作台</span>
        </div>
      </div>

      <el-menu class="nav-menu" :default-active="activePage" @select="activePage = $event">
        <el-menu-item
          v-for="item in menuItems"
          :key="item.key"
          :index="item.key"
        >
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <div class="nav-copy">
            <strong>{{ item.label }}</strong>
            <span>{{ item.description }}</span>
          </div>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-main class="main-panel">
      <div class="mobile-topbar">
        <div>
          <p class="eyebrow">当前模块</p>
          <h1>{{ activeMenu?.label }}</h1>
        </div>
        <el-select v-model="activePage" aria-label="切换页面" class="mobile-page-select">
          <el-option
            v-for="item in menuItems"
            :key="item.key"
            :label="item.label"
            :value="item.key"
          />
        </el-select>
      </div>

      <ChatPage v-if="activePage === 'chat'" />
      <DbConnectionPage v-else />
    </el-main>
  </el-container>
</template>
