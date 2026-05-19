<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import {
  createDbConnection,
  deleteDbConnection,
  listDbConnections,
  updateDbConnection,
} from "../api/dbConnections";

const defaultForm = {
  user_id: "",
  name: "",
  db_type: "postgresql",
  host: "",
  port: null,
  database_name: "",
  username: "",
  password: "",
  ssl_mode: "prefer",
  readonly: true,
  status: "active",
};

const filters = reactive({
  keyword: "",
  db_type: "",
  status: "",
});

const pager = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

const form = reactive({ ...defaultForm });
const connections = ref([]);
const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");
const formError = ref("");
const panelOpen = ref(false);
const editingConnectionId = ref("");
const extraText = ref("{}");

const totalPages = computed(() => Math.max(1, Math.ceil(pager.total / pager.pageSize)));
const isEditing = computed(() => Boolean(editingConnectionId.value));

function resetForm() {
  Object.assign(form, defaultForm);
  extraText.value = "{}";
  editingConnectionId.value = "";
  formError.value = "";
}

function openCreatePanel() {
  resetForm();
  panelOpen.value = true;
}

function openEditPanel(connection) {
  Object.assign(form, {
    user_id: connection.user_id || "",
    name: connection.name || "",
    db_type: connection.db_type || "postgresql",
    host: connection.host || "",
    port: connection.port || null,
    database_name: connection.database_name || "",
    username: connection.username || "",
    password: "",
    ssl_mode: connection.ssl_mode || "prefer",
    readonly: Boolean(connection.readonly),
    status: connection.status || "active",
  });
  extraText.value = JSON.stringify(connection.extra || {}, null, 2);
  editingConnectionId.value = connection.connection_id;
  formError.value = "";
  panelOpen.value = true;
}

function closePanel() {
  panelOpen.value = false;
  resetForm();
}

function cleanPayload() {
  let extra = {};
  try {
    extra = extraText.value.trim() ? JSON.parse(extraText.value) : {};
  } catch {
    throw new Error("扩展配置必须是合法 JSON 对象");
  }
  if (!extra || Array.isArray(extra) || typeof extra !== "object") {
    throw new Error("扩展配置必须是 JSON 对象");
  }

  const payload = {
    user_id: form.user_id.trim() || null,
    name: form.name.trim(),
    db_type: form.db_type,
    host: form.host.trim(),
    port: form.port === "" || form.port === null ? null : Number(form.port),
    database_name: form.database_name.trim(),
    username: form.username.trim(),
    password: form.password,
    ssl_mode: form.ssl_mode,
    readonly: Boolean(form.readonly),
    status: form.status,
    extra,
  };

  if (!payload.name || !payload.host || !payload.database_name || !payload.username) {
    throw new Error("请填写连接名称、主机、数据库名和用户名");
  }
  if (!isEditing.value && !payload.password.trim()) {
    throw new Error("新增数据源时必须填写密码");
  }
  if (isEditing.value && !payload.password.trim()) {
    delete payload.password;
  }
  return payload;
}

async function loadConnections() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const payload = await listDbConnections({
      keyword: filters.keyword.trim(),
      db_type: filters.db_type,
      status: filters.status,
      page: pager.page,
      page_size: pager.pageSize,
    });
    connections.value = Array.isArray(payload.data) ? payload.data : [];
    pager.total = payload.total || 0;
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    loading.value = false;
  }
}

function applyFilters() {
  pager.page = 1;
  loadConnections();
}

function resetFilters() {
  filters.keyword = "";
  filters.db_type = "";
  filters.status = "";
  applyFilters();
}

async function saveConnection() {
  saving.value = true;
  formError.value = "";
  try {
    const payload = cleanPayload();
    if (isEditing.value) {
      await updateDbConnection(editingConnectionId.value, payload);
    } else {
      await createDbConnection(payload);
    }
    closePanel();
    await loadConnections();
  } catch (error) {
    formError.value = error.message;
  } finally {
    saving.value = false;
  }
}

async function removeConnection(connection) {
  const confirmed = window.confirm(`确认删除数据源「${connection.name}」吗？`);
  if (!confirmed) {
    return;
  }
  errorMessage.value = "";
  try {
    await deleteDbConnection(connection.connection_id);
    if (connections.value.length === 1 && pager.page > 1) {
      pager.page -= 1;
    }
    await loadConnections();
  } catch (error) {
    errorMessage.value = error.message;
  }
}

function changePage(nextPage) {
  const normalized = Math.min(Math.max(nextPage, 1), totalPages.value);
  if (normalized !== pager.page) {
    pager.page = normalized;
    loadConnections();
  }
}

function formatDate(value) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatTestState(connection) {
  if (!connection.last_tested_at) {
    return "未测试";
  }
  return connection.last_test_success ? "测试通过" : "测试失败";
}

onMounted(loadConnections);
</script>

<template>
  <section class="workspace-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Data Sources</p>
        <h1>数据源管理</h1>
      </div>
      <button class="primary-button" type="button" @click="openCreatePanel">新增数据源</button>
    </header>

    <section class="toolbar-panel connection-toolbar">
      <label>
        <span>搜索</span>
        <input v-model="filters.keyword" type="search" placeholder="连接名称" @keyup.enter="applyFilters" />
      </label>
      <label>
        <span>数据库类型</span>
        <select v-model="filters.db_type">
          <option value="">全部</option>
          <option value="postgresql">PostgreSQL</option>
          <option value="mysql">MySQL</option>
        </select>
      </label>
      <label>
        <span>状态</span>
        <select v-model="filters.status">
          <option value="">全部</option>
          <option value="active">启用</option>
          <option value="disabled">停用</option>
        </select>
      </label>
      <div class="toolbar-actions">
        <button class="ghost-button" type="button" @click="resetFilters">重置</button>
        <button class="dark-button" type="button" @click="applyFilters">查询</button>
      </div>
    </section>

    <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

    <section class="data-panel">
      <div class="table-meta">
        <span>共 {{ pager.total }} 条数据源</span>
        <span v-if="loading">正在加载...</span>
      </div>

      <div class="table-wrap connections-table">
        <table>
          <thead>
            <tr>
              <th>连接名称</th>
              <th>类型</th>
              <th>主机</th>
              <th>数据库</th>
              <th>用户</th>
              <th>访问</th>
              <th>状态</th>
              <th>连接测试</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!loading && connections.length === 0">
              <td colspan="10" class="empty-cell">暂无数据源</td>
            </tr>
            <tr v-for="connection in connections" :key="connection.connection_id">
              <td>
                <strong>{{ connection.name }}</strong>
                <small>{{ connection.connection_id }}</small>
              </td>
              <td>{{ connection.db_type }}</td>
              <td>{{ connection.host }}:{{ connection.port }}</td>
              <td>{{ connection.database_name }}</td>
              <td>{{ connection.username }}</td>
              <td>{{ connection.readonly ? "只读" : "读写" }}</td>
              <td>
                <span class="status-pill" :class="connection.status">
                  {{ connection.status === "active" ? "启用" : "停用" }}
                </span>
              </td>
              <td>{{ formatTestState(connection) }}</td>
              <td>{{ formatDate(connection.updated_at) }}</td>
              <td>
                <div class="row-actions">
                  <button class="link-button" type="button" @click="openEditPanel(connection)">编辑</button>
                  <button class="danger-link" type="button" @click="removeConnection(connection)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <footer class="pagination">
        <button class="ghost-button" type="button" :disabled="pager.page <= 1" @click="changePage(pager.page - 1)">
          上一页
        </button>
        <span>第 {{ pager.page }} / {{ totalPages }} 页</span>
        <button
          class="ghost-button"
          type="button"
          :disabled="pager.page >= totalPages"
          @click="changePage(pager.page + 1)"
        >
          下一页
        </button>
      </footer>
    </section>

    <div v-if="panelOpen" class="drawer-mask" @click.self="closePanel">
      <aside class="drawer-panel" aria-label="数据源表单">
        <header>
          <div>
            <p class="eyebrow">{{ isEditing ? "Edit Source" : "New Source" }}</p>
            <h2>{{ isEditing ? "编辑数据源" : "新增数据源" }}</h2>
          </div>
          <button class="ghost-button" type="button" @click="closePanel">关闭</button>
        </header>

        <form class="connection-form" @submit.prevent="saveConnection">
          <label>
            <span>连接名称</span>
            <input v-model="form.name" type="text" maxlength="100" placeholder="例如：生产只读库" />
          </label>
          <label>
            <span>用户标识</span>
            <input v-model="form.user_id" type="text" maxlength="100" placeholder="可选" />
          </label>
          <label>
            <span>数据库类型</span>
            <select v-model="form.db_type">
              <option value="postgresql">PostgreSQL</option>
              <option value="mysql">MySQL</option>
            </select>
          </label>
          <label>
            <span>主机</span>
            <input v-model="form.host" type="text" maxlength="255" placeholder="127.0.0.1" />
          </label>
          <label>
            <span>端口</span>
            <input v-model="form.port" type="number" min="1" max="65535" placeholder="默认端口" />
          </label>
          <label>
            <span>数据库名</span>
            <input v-model="form.database_name" type="text" maxlength="100" />
          </label>
          <label>
            <span>用户名</span>
            <input v-model="form.username" type="text" maxlength="100" />
          </label>
          <label>
            <span>密码</span>
            <input
              v-model="form.password"
              type="password"
              :placeholder="isEditing ? '不填写则保持原密码' : '请输入密码'"
            />
          </label>
          <label>
            <span>SSL 模式</span>
            <select v-model="form.ssl_mode">
              <option value="disable">disable</option>
              <option value="allow">allow</option>
              <option value="prefer">prefer</option>
              <option value="require">require</option>
              <option value="verify-ca">verify-ca</option>
              <option value="verify-full">verify-full</option>
            </select>
          </label>
          <label>
            <span>状态</span>
            <select v-model="form.status">
              <option value="active">启用</option>
              <option value="disabled">停用</option>
            </select>
          </label>
          <label class="switch-row">
            <input v-model="form.readonly" type="checkbox" />
            <span>只读连接</span>
          </label>
          <label class="form-wide">
            <span>扩展配置 JSON</span>
            <textarea v-model="extraText" rows="5" spellcheck="false"></textarea>
          </label>

          <p v-if="formError" class="error-banner">{{ formError }}</p>

          <footer class="form-actions">
            <button class="ghost-button" type="button" @click="closePanel">取消</button>
            <button class="primary-button" type="submit" :disabled="saving">
              {{ saving ? "保存中..." : "保存" }}
            </button>
          </footer>
        </form>
      </aside>
    </div>
  </section>
</template>
