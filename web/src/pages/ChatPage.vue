<script setup>
import { computed, nextTick, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { chatWithAgent, listDbConnections } from "../api/agent";

const connections = ref([]);
const selectedConnectionId = ref("");
const messages = ref([]);
const inputMessage = ref("");
const loadingConnections = ref(false);
const sending = ref(false);
const errorMessage = ref("");
const chatBody = ref(null);
const sessionId = ref(createSessionId());

const selectedConnection = computed(() =>
  connections.value.find((item) => item.connection_id === selectedConnectionId.value)
);

const canSend = computed(
  () => Boolean(selectedConnectionId.value) && Boolean(inputMessage.value.trim()) && !sending.value
);

function createSessionId() {
  if (crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function formatConnection(connection) {
  const parts = [
    connection.name,
    connection.db_type,
    connection.database_name,
    connection.status,
  ].filter(Boolean);
  return parts.join(" / ");
}

function formatIntent(intent) {
  const intentMap = {
    data_query: "数据查询",
    metadata_query: "元数据查询",
    chat: "普通对话",
  };
  return intentMap[intent] || intent || "未知";
}

function normalizeRows(data) {
  return Array.isArray(data) ? data : [];
}

function tableColumns(data) {
  const columns = new Set();
  normalizeRows(data).forEach((row) => {
    if (row && typeof row === "object" && !Array.isArray(row)) {
      Object.keys(row).forEach((key) => columns.add(key));
    }
  });
  return Array.from(columns);
}

function displayValue(value) {
  if (value === null || value === undefined) {
    return "";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

async function scrollToBottom() {
  await nextTick();
  if (chatBody.value) {
    chatBody.value.scrollTop = chatBody.value.scrollHeight;
  }
}

async function loadConnections() {
  loadingConnections.value = true;
  errorMessage.value = "";
  try {
    const payload = await listDbConnections();
    connections.value = Array.isArray(payload.data) ? payload.data : [];
    if (!connections.value.some((item) => item.connection_id === selectedConnectionId.value)) {
      selectedConnectionId.value = connections.value[0]?.connection_id || "";
    }
  } catch (error) {
    errorMessage.value = error.message;
    ElMessage.error(error.message);
  } finally {
    loadingConnections.value = false;
  }
}

function newSession() {
  sessionId.value = createSessionId();
  messages.value = [];
  inputMessage.value = "";
  errorMessage.value = "";
}

async function sendMessage() {
  const text = inputMessage.value.trim();
  if (!canSend.value) {
    return;
  }

  errorMessage.value = "";
  inputMessage.value = "";
  messages.value.push({
    id: createSessionId(),
    role: "user",
    content: text,
  });
  await scrollToBottom();

  sending.value = true;
  try {
    const reply = await chatWithAgent({
      sessionId: sessionId.value,
      message: text,
      connectionId: selectedConnectionId.value,
    });
    messages.value.push({
      id: createSessionId(),
      role: "assistant",
      content: reply.answer || "",
      intent: reply.intent,
      sql: reply.sql,
      rowCount: reply.row_count,
      data: normalizeRows(reply.data),
    });
  } catch (error) {
    errorMessage.value = error.message;
    ElMessage.error(error.message);
    messages.value.push({
      id: createSessionId(),
      role: "assistant",
      content: `请求失败：${error.message}`,
      isError: true,
    });
  } finally {
    sending.value = false;
    await scrollToBottom();
  }
}

function handleEnter(event) {
  if (!event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

onMounted(loadConnections);
</script>

<template>
  <section class="workspace-page chat-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Database Agent</p>
        <h1>数据库智能问答</h1>
      </div>
      <div class="header-actions">
        <el-button icon="Refresh" :loading="loadingConnections" @click="loadConnections">
          刷新连接
        </el-button>
        <el-button type="primary" icon="Plus" @click="newSession">新建会话</el-button>
      </div>
    </header>

    <section class="toolbar-panel chat-toolbar">
      <span class="field-label">数据库连接</span>
      <el-select
        v-model="selectedConnectionId"
        class="connection-select"
        filterable
        placeholder="请选择数据库连接"
        :loading="loadingConnections"
        :disabled="loadingConnections || sending || connections.length === 0"
      >
        <el-option
          v-for="connection in connections"
          :key="connection.connection_id"
          :label="formatConnection(connection)"
          :value="connection.connection_id"
        />
      </el-select>
      <p v-if="selectedConnection" class="muted-line">
        当前连接：{{ selectedConnection.name }}，数据库：{{ selectedConnection.database_name }}
      </p>
      <p v-else-if="!loadingConnections" class="muted-line warning-text">
        暂无可用连接，请先创建数据库连接。
      </p>
    </section>

    <section ref="chatBody" class="chat-body" aria-live="polite">
      <el-empty
        v-if="messages.length === 0"
        class="empty-state"
        description="选择连接后开始提问，可以询问表结构、字段含义，或让 Agent 查询业务数据。"
      />

      <article
        v-for="message in messages"
        :key="message.id"
        class="message"
        :class="[message.role, { error: message.isError }]"
      >
        <div class="message-label">{{ message.role === "user" ? "你" : "Agent" }}</div>
        <div class="message-content">
          <p>{{ message.content }}</p>

          <div v-if="message.role === 'assistant' && !message.isError" class="reply-detail">
            <el-tag v-if="message.intent" type="info" effect="light">
              {{ formatIntent(message.intent) }}
            </el-tag>
            <el-tag v-if="Number.isInteger(message.rowCount)" type="success" effect="light">
              {{ message.rowCount }} 行
            </el-tag>
          </div>

          <pre v-if="message.sql" class="sql-block"><code>{{ message.sql }}</code></pre>

          <el-table
            v-if="message.data && message.data.length"
            class="result-table"
            :data="message.data"
            border
            size="small"
          >
            <el-table-column
              v-for="column in tableColumns(message.data)"
              :key="column"
              :prop="column"
              :label="column"
              min-width="140"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                    {{ displayValue(row[column]) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </article>
    </section>

    <el-alert
      v-if="errorMessage"
      class="page-alert"
      :title="errorMessage"
      type="error"
      show-icon
      :closable="false"
    />

    <el-form class="composer" @submit.prevent="sendMessage">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="2"
        resize="vertical"
        placeholder="输入你的数据库问题，Enter 发送，Shift + Enter 换行"
        :disabled="!selectedConnectionId || sending"
        @keydown.enter="handleEnter"
      />
      <el-button type="primary" native-type="submit" :loading="sending" :disabled="!canSend">
        发送
      </el-button>
    </el-form>
  </section>
</template>
