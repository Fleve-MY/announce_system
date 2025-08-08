<template>
  <div class="content-container">
    <div class="header-with-button">
      <h1>同款检测日志</h1>
      <button @click="fetchLogs" :disabled="isLoading" class="btn-primary refresh-btn">
        <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
        刷新
      </button>
    </div>

    <div class="list-card">
      <div v-if="isLoading" class="loading-state">
        正在从飞书获取数据...
      </div>
      <div v-else-if="error" class="error-state">
        {{ error }}
      </div>
      <ul v-else-if="logs.length > 0" class="log-list">
        <li class="log-list-header">
          <div v-if="authStore.isAdmin" class="col-user sortable filter-wrapper">
            <span @click="toggleFilter('username')">
              运营人
              <i class="fas fa-filter filter-icon" :class="{ active: filters.username.length > 0 }"></i>
            </span>
            <div v-if="activeFilter === 'username'" class="filter-dropdown" @click.stop>
              <h3>筛选运营人</h3>
              <div class="filter-options">
                <label v-for="option in uniqueFilterOptions.username" :key="option">
                  <input type="checkbox" :value="option" v-model="filters.username">
                  {{ option }}
                </label>
              </div>
              <div class="filter-actions">
                <button @click="resetFilter('username')" class="btn-secondary">重置</button>
                <button @click="closeFilter" class="btn-primary">确认</button>
              </div>
            </div>
          </div>

          <span class="col-a">流水号</span>

          <div class="col-b sortable filter-wrapper">
            <span @click="toggleSort('b_col')">
              日期
              <i class="fas" :class="sortIconClass"></i>
            </span>
            <i class="fas fa-filter filter-icon separate-filter" :class="{ active: isDateFilterActive }" @click.stop="toggleFilter('b_col')"></i>
            <!-- 1. 修改日期筛选框的内部结构 -->
            <div v-if="activeFilter === 'b_col'" class="filter-dropdown date-range-filter" @click.stop>
              <h3>按日期范围筛选</h3>
              <div class="date-inputs">
                <label for="start-date">开始日期:</label>
                <input type="date" id="start-date" v-model="filters.b_col.start">
                <label for="end-date">结束日期:</label>
                <input type="date" id="end-date" v-model="filters.b_col.end">
              </div>
              <div class="filter-actions">
                <button @click="resetFilter('b_col')" class="btn-secondary">重置</button>
                <button @click="closeFilter" class="btn-primary">确认</button>
              </div>
            </div>
          </div>

          <div class="col-c sortable filter-wrapper">
            <span @click="toggleFilter('c_col')">
              店铺
              <i class="fas fa-filter filter-icon" :class="{ active: filters.c_col.length > 0 }"></i>
            </span>
            <div v-if="activeFilter === 'c_col'" class="filter-dropdown" @click.stop>
              <h3>筛选店铺</h3>
              <div class="filter-options">
                <label v-for="option in uniqueFilterOptions.c_col" :key="option">
                  <input type="checkbox" :value="option" v-model="filters.c_col">
                  {{ option }}
                </label>
              </div>
              <div class="filter-actions">
                <button @click="resetFilter('c_col')" class="btn-secondary">重置</button>
                <button @click="closeFilter" class="btn-primary">确认</button>
              </div>
            </div>
          </div>
          <span class="col-d">店铺编码</span>
          <span class="col-j">选品编码</span>
          <span class="col-f">关键字/类目</span>
          <span class="col-g">OSS路径</span>
          <span class="col-h">上传数量</span>
          <span class="col-i">上传状态</span>
          <span class="col-k">检测状态</span>
          <span class="col-l">检测结果文件名称</span>
        </li>
        <li v-for="(log, index) in paginatedLogs" :key="index" class="log-list-item">
          <span v-if="authStore.isAdmin" class="col-user">{{ log.username }}</span>
          <span class="col-a">{{ log.a_col }}</span>
          <span class="col-b">{{ log.b_col }}</span>
          <span class="col-c">{{ log.c_col }}</span>
          <span class="col-d">{{ log.d_col }}</span>
          <span class="col-j">{{ log.j_col }}</span>
          <span class="col-f">{{ log.f_col }}</span>
          <span class="col-g expandable" :class="{ expanded: isExpanded(index, 'g') }" @click="toggleExpand(index, 'g')">
            {{ log.g_col }}
          </span>
          <span class="col-h">{{ log.h_col }}</span>
          <span class="col-i">{{ log.i_col }}</span>
          <span class="col-k" :class="getStatusClass(log.k_col)">{{ log.k_col }}</span>
          <span class="col-l expandable" :class="{ expanded: isExpanded(index, 'l') }" @click="toggleExpand(index, 'l')">
            {{ log.l_col }}
          </span>
        </li>
      </ul>
      <div v-else class="empty-state">
        <span v-if="authStore.isAdmin">表格中目前没有有效的日志记录。</span>
        <span v-else>没有找到与您用户名匹配的日志记录。</span>
      </div>

      <div v-if="filteredAndSortedLogs.length > perPage" class="pagination">
        <button @click="changePage(page - 1)" :disabled="page === 1">上一页</button>
        <span>第 {{ page }} / {{ totalPages }} 页</span>
        <button @click="changePage(page + 1)" :disabled="page === totalPages">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import apiClient from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const logs = ref([]);
const isLoading = ref(false);
const error = ref(null);

const page = ref(1);
const perPage = ref(20);
const sortKey = ref('b_col');
const sortDirection = ref('desc');

// 筛选
const filters = ref({
  username: [],
  c_col: [],
  b_col: { start: '', end: '' },
});
const activeFilter = ref('');
const expandedCells = ref({});

const filterLabels = {
  username: '运营人',
  c_col: '店铺',
  b_col: '日期',
};

// 计算属性
const uniqueFilterOptions = computed(() => ({
  username: [...new Set(logs.value.map(log => log.username))].sort(),
  c_col: [...new Set(logs.value.map(log => log.c_col))].sort(),
}));

// 判断日期筛选是否生效
const isDateFilterActive = computed(() => {
  return filters.value.b_col.start || filters.value.b_col.end;
});

const filteredAndSortedLogs = computed(() => {
  let result = logs.value.filter(log => {
    // 日期筛选逻辑
    const logDate = log.b_col ? new Date(log.b_col.split(' ')[0]) : null;
    const startDate = filters.value.b_col.start ? new Date(filters.value.b_col.start) : null;
    const endDate = filters.value.b_col.end ? new Date(filters.value.b_col.end) : null;

    // 结束日期的时分秒设置为23:59:59，以包含当天的全部数据
    if (endDate) {
      endDate.setHours(23, 59, 59, 999);
    }

    const isDateMatch = !logDate || (
      (!startDate || logDate >= startDate) &&
      (!endDate || logDate <= endDate)
    );

    return (
      (filters.value.username.length === 0 || filters.value.username.includes(log.username)) &&
      (filters.value.c_col.length === 0 || filters.value.c_col.includes(log.c_col)) &&
      isDateMatch
    );
  });

  result.sort((a, b) => {
    const valA = a[sortKey.value];
    const valB = b[sortKey.value];
    let comparison = 0;
    if (sortKey.value === 'b_col') {
      if (!valA) return 1;
      if (!valB) return -1;
      const dateA = new Date(valA.replace(/-/g, '/'));
      const dateB = new Date(valB.replace(/-/g, '/'));
      comparison = dateA - dateB;
    } else {
      if (valA > valB) comparison = 1;
      else if (valA < valB) comparison = -1;
    }
    return sortDirection.value === 'asc' ? comparison : -comparison;
  });
  return result;
});

const totalPages = computed(() => Math.ceil(filteredAndSortedLogs.value.length / perPage.value));
const paginatedLogs = computed(() => {
  const start = (page.value - 1) * perPage.value;
  const end = start + perPage.value;
  return filteredAndSortedLogs.value.slice(start, end);
});
const sortIconClass = computed(() => {
  if (sortKey.value === 'b_col') {
    return sortDirection.value === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
  }
  return 'fa-sort';
});

// 读取数据
const fetchLogs = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/feishu-logs/');
    logs.value = response.data;
  } catch (err) {
    error.value = "获取数据失败，请稍后再试或联系管理员。";
  } finally {
    isLoading.value = false;
  }
};

const toggleFilter = (filterType) => {
  if (activeFilter.value === filterType) {
    activeFilter.value = '';
  } else {
    activeFilter.value = filterType;
  }
};
const closeFilter = () => {
  activeFilter.value = '';
  page.value = 1;
};
const resetFilter = (filterType) => {
  if (filterType === 'b_col') {
    filters.value.b_col = { start: '', end: '' };
  } else {
    filters.value[filterType] = [];
  }
  page.value = 1;
};

const isExpanded = (rowIndex, colKey) => {
  return !!expandedCells.value[`${rowIndex}-${colKey}`];
};
const toggleExpand = (rowIndex, colKey) => {
  const key = `${rowIndex}-${colKey}`;
  expandedCells.value[key] = !expandedCells.value[key];
};

const handleClickOutside = (event) => {
  if (activeFilter.value && !event.target.closest('.filter-wrapper')) {
    closeFilter();
  }
};

onMounted(() => {
  fetchLogs();
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});

const toggleSort = (key) => {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDirection.value = 'desc';
  }
  page.value = 1;
};
const changePage = (newPage) => {
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage;
  }
};
const getStatusClass = (status) => {
  if (status === '未完成') return 'status-unfinished';
  if (status && status.includes('已')) return 'status-finished';
  return '';
};
</script>
