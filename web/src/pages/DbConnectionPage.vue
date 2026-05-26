<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
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

const sensitiveKeyPattern =
  /(password|passwd|pwd|token|api[_-]?key|apikey|secret|credential|connection[_-]?string|dsn|uri)/i;

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

const formRef = ref(null);
const form = reactive({ ...defaultForm });
const connections = ref([]);
const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");
const formError = ref("");
const panelOpen = ref(false);
const editingConnectionId = ref("");
const extraText = ref("{}");
const extraDirty = ref(false);
const deletingConnectionId = ref("");

const isEditing = computed(() => Boolean(editingConnectionId.value));
const formRules = computed(() => ({
  name: [{ required: true, message: "请填写连接名称", trigger: "blur" }],
  host: [{ required: true, message: "请填写主机", trigger: "blur" }],
  database_name: [{ required: true, message: "请填写数据库名", trigger: "blur" }],
  username: [{ required: true, message: "请填写用户名", trigger: "blur" }],
  password: [
    {
      validator: (_rule, value, callback) => {
        if (!isEditing.value && !String(value || "").trim()) {
          callback(new Error("新增数据源时必须填写密码"));
          return;
        }
        callback();
      },
      trigger: "blur",
    },
  ],
}));

function resetForm() {
  Object.assign(form, defaultForm);
  extraText.value = "{}";
  extraDirty.value = false;
  editingConnectionId.value = "";
  formError.value = "";
  formRef.value?.clearValidate();
}

function maskSensitiveExtra(value) {
  if (Array.isArray(value)) {
    return value.map((item) => maskSensitiveExtra(item));
  }
  if (!value || typeof value !== "object") {
    return value;
  }
  return Object.fromEntries(
    Object.entries(value).map(([key, item]) => [
      key,
      sensitiveKeyPattern.test(key) ? "[已隐藏]" : maskSensitiveExtra(item),
    ])
  );
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
  extraText.value = JSON.stringify(maskSensitiveExtra(connection.extra || {}), null, 2);
  extraDirty.value = false;
  editingConnectionId.value = connection.connection_id;
  formError.value = "";
  panelOpen.value = true;
}

function closePanel() {
  panelOpen.value = false;
}

function parseExtra() {
  try {
    const extra = extraText.value.trim() ? JSON.parse(extraText.value) : {};
    if (!extra || Array.isArray(extra) || typeof extra !== "object") {
      throw new Error();
    }
    return extra;
  } catch {
    throw new Error("扩展配置必须是合法 JSON 对象");
  }
}

function cleanPayload() {
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
  };

  if (!isEditing.value || extraDirty.value) {
    payload.extra = parseExtra();
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
    ElMessage.error(error.message);
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
  formError.value = "";
  try {
    await formRef.value?.validate();
    const payload = cleanPayload();
    saving.value = true;
    if (isEditing.value) {
      await updateDbConnection(editingConnectionId.value, payload);
      ElMessage.success("数据源已更新");
    } else {
      await createDbConnection(payload);
      ElMessage.success("数据源已创建");
    }
    closePanel();
    await loadConnections();
  } catch (error) {
    const message = error?.message || "请检查表单必填项";
    formError.value = message;
    ElMessage.error(message);
  } finally {
    saving.value = false;
  }
}

async function removeConnection(connection) {
  try {
    await ElMessageBox.confirm(`确认删除数据源「${connection.name}」吗？`, "删除数据源", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
      confirmButtonClass: "el-button--danger",
    });
  } catch {
    return;
  }

  errorMessage.value = "";
  deletingConnectionId.value = connection.connection_id;
  try {
    await deleteDbConnection(connection.connection_id);
    ElMessage.success("数据源已删除");
    if (connections.value.length === 1 && pager.page > 1) {
      pager.page -= 1;
    }
    await loadConnections();
  } catch (error) {
    errorMessage.value = error.message;
    ElMessage.error(error.message);
  } finally {
    deletingConnectionId.value = "";
  }
}

function handlePageChange(nextPage) {
  pager.page = nextPage;
  loadConnections();
}

function handlePageSizeChange(nextSize) {
  pager.pageSize = nextSize;
  pager.page = 1;
  loadConnections();
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

function testStateType(connection) {
  if (!connection.last_tested_at) {
    return "info";
  }
  return connection.last_test_success ? "success" : "danger";
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
      <el-button type="primary" icon="Plus" @click="openCreatePanel">新增数据源</el-button>
    </header>

    <el-form class="toolbar-panel connection-toolbar" label-position="top" @submit.prevent>
      <el-form-item label="搜索">
        <el-input
          v-model="filters.keyword"
          clearable
          placeholder="连接名称"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="数据库类型">
        <el-select v-model="filters.db_type" clearable placeholder="全部">
          <el-option label="PostgreSQL" value="postgresql" />
          <el-option label="MySQL" value="mysql" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="filters.status" clearable placeholder="全部">
          <el-option label="启用" value="active" />
          <el-option label="停用" value="disabled" />
        </el-select>
      </el-form-item>
      <div class="toolbar-actions">
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" icon="Search" @click="applyFilters">查询</el-button>
      </div>
    </el-form>

    <el-alert
      v-if="errorMessage"
      class="page-alert"
      :title="errorMessage"
      type="error"
      show-icon
      :closable="false"
    />

    <section class="data-panel">
      <div class="table-meta">
        <span>共 {{ pager.total }} 条数据源</span>
        <el-tag v-if="loading" type="info" effect="plain">正在加载</el-tag>
      </div>

      <el-table
        v-loading="loading"
        class="connection-table"
        :data="connections"
        border
        empty-text="暂无数据源"
      >
        <el-table-column prop="name" label="连接名称" min-width="190" fixed>
          <template #default="{ row }">
            <strong class="table-title">{{ row.name }}</strong>
            <small>{{ row.connection_id }}</small>
          </template>
        </el-table-column>
        <el-table-column prop="db_type" label="类型" min-width="110" />
        <el-table-column label="主机" min-width="190" show-overflow-tooltip>
          <template #default="{ row }">{{ row.host }}:{{ row.port }}</template>
        </el-table-column>
        <el-table-column prop="database_name" label="数据库" min-width="150" show-overflow-tooltip />
        <el-table-column prop="username" label="用户" min-width="130" show-overflow-tooltip />
        <el-table-column label="访问" min-width="90">
          <template #default="{ row }">
            <el-tag :type="row.readonly ? 'info' : 'warning'" effect="light">
              {{ row.readonly ? "只读" : "读写" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'warning'" effect="light">
              {{ row.status === "active" ? "启用" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="连接测试" min-width="110">
          <template #default="{ row }">
            <el-tag :type="testStateType(row)" effect="plain">{{ formatTestState(row) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" min-width="160">
          <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="row-actions">
              <el-button link type="primary" @click="openEditPanel(row)">编辑</el-button>
              <el-button
                link
                type="danger"
                :loading="deletingConnectionId === row.connection_id"
                @click="removeConnection(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <footer class="pagination">
        <el-pagination
          v-model:current-page="pager.page"
          v-model:page-size="pager.pageSize"
          background
          layout="total, sizes, prev, pager, next"
          :page-sizes="[10, 20, 50, 100]"
          :total="pager.total"
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </footer>
    </section>

    <el-drawer
      v-model="panelOpen"
      class="connection-drawer"
      size="min(620px, 100vw)"
      :with-header="false"
      @closed="resetForm"
    >
      <template #default>
        <header class="drawer-header">
          <div>
            <p class="eyebrow">{{ isEditing ? "Edit Source" : "New Source" }}</p>
            <h2>{{ isEditing ? "编辑数据源" : "新增数据源" }}</h2>
          </div>
          <el-button icon="Close" circle @click="closePanel" />
        </header>

        <el-form
          ref="formRef"
          class="connection-form"
          :model="form"
          :rules="formRules"
          label-position="top"
          @submit.prevent="saveConnection"
        >
          <el-form-item label="连接名称" prop="name">
            <el-input v-model="form.name" maxlength="100" placeholder="例如：生产只读库" />
          </el-form-item>
          <el-form-item label="用户标识">
            <el-input v-model="form.user_id" maxlength="100" placeholder="可选" />
          </el-form-item>
          <el-form-item label="数据库类型" prop="db_type">
            <el-select v-model="form.db_type">
              <el-option label="PostgreSQL" value="postgresql" />
              <el-option label="MySQL" value="mysql" />
            </el-select>
          </el-form-item>
          <el-form-item label="主机" prop="host">
            <el-input v-model="form.host" maxlength="255" placeholder="127.0.0.1" />
          </el-form-item>
          <el-form-item label="端口">
            <el-input-number
              v-model="form.port"
              :min="1"
              :max="65535"
              controls-position="right"
              placeholder="默认端口"
            />
          </el-form-item>
          <el-form-item label="数据库名" prop="database_name">
            <el-input v-model="form.database_name" maxlength="100" />
          </el-form-item>
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" maxlength="100" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              :placeholder="isEditing ? '不填写则保持原密码' : '请输入密码'"
            />
          </el-form-item>
          <el-form-item label="SSL 模式">
            <el-select v-model="form.ssl_mode">
              <el-option label="disable" value="disable" />
              <el-option label="allow" value="allow" />
              <el-option label="prefer" value="prefer" />
              <el-option label="require" value="require" />
              <el-option label="verify-ca" value="verify-ca" />
              <el-option label="verify-full" value="verify-full" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="form.status">
              <el-option label="启用" value="active" />
              <el-option label="停用" value="disabled" />
            </el-select>
          </el-form-item>
          <el-form-item class="form-wide" label="访问模式">
            <el-switch
              v-model="form.readonly"
              active-text="只读连接"
              inactive-text="读写连接"
              inline-prompt
            />
          </el-form-item>
          <el-form-item class="form-wide" label="扩展配置 JSON">
            <el-input
              v-model="extraText"
              type="textarea"
              :rows="5"
              resize="vertical"
              spellcheck="false"
              @input="extraDirty = true"
            />
            <p v-if="isEditing" class="field-help">
              编辑时不修改扩展配置将保留原值；敏感键值不会明文回显。
            </p>
          </el-form-item>

          <el-alert
            v-if="formError"
            class="form-wide"
            :title="formError"
            type="error"
            show-icon
            :closable="false"
          />

          <footer class="form-actions">
            <el-button @click="closePanel">取消</el-button>
            <el-button type="primary" native-type="submit" :loading="saving">保存</el-button>
          </footer>
        </el-form>
      </template>
    </el-drawer>
  </section>
</template>
