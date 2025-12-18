<template>
  <div class="app-container">
    <!-- 搜索栏 -->
    <div class="filter-container">
      <el-input
        v-model="listQuery.phone"
        placeholder="手机号"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter="handleFilter"
        clearable
        @clear="handleFilter"
      />
      <el-button class="filter-item" type="primary" icon="Search" @click="handleFilter">
        搜索
      </el-button>
    </div>

    <!-- 数据表格 -->
    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column label="ID" prop="id" align="center" width="80" />
      
      <el-table-column label="头像" align="center" width="100">
        <template #default="{ row }">
          <el-avatar :size="50" :src="row.avatar_url" shape="square">
            <img src="https://cube.elemecdn.com/e/fd/0fc7d20532fdaf769a25683617711png.png"/>
          </el-avatar>
        </template>
      </el-table-column>

      <el-table-column label="昵称" prop="nickname" align="center" min-width="120">
        <template #default="{ row }">
          {{ row.nickname || '未设置昵称' }}
        </template>
      </el-table-column>

      <el-table-column label="手机号" prop="phone" align="center" width="150">
        <template #default="{ row }">
          {{ row.phone || '--' }}
        </template>
      </el-table-column>

      <el-table-column label="注册时间" align="center" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="listQuery.page"
        v-model:page-size="listQuery.size"
        :page-sizes="[10, 20, 30, 50]"
        :total="total"
        background
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getUserList } from '@/api/user'
import dayjs from 'dayjs'

const list = ref([])
const total = ref(0)
const listLoading = ref(true)
const listQuery = reactive({
  page: 1,
  size: 10,
  phone: undefined
})

const formatTime = (time) => {
  if (!time) return '--'
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const getList = async () => {
  listLoading.value = true
  try {
    const res = await getUserList(listQuery)
    list.value = res.list
    total.value = res.total
  } catch (error) {
    console.error(error)
  } finally {
    listLoading.value = false
  }
}

const handleFilter = () => {
  listQuery.page = 1
  getList()
}

const handleSizeChange = (val) => {
  listQuery.size = val
  getList()
}

const handleCurrentChange = (val) => {
  listQuery.page = val
  getList()
}

onMounted(() => {
  getList()
})
</script>

<style scoped>
.filter-container {
  padding-bottom: 10px;
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
