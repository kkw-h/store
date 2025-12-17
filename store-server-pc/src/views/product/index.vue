<template>
  <div class="app-container">
    <!-- 筛选栏 -->
    <div class="filter-container">
      <el-input
        v-model="listQuery.name"
        placeholder="商品名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter="handleFilter"
      />
      <el-select
        v-model="listQuery.category_id"
        placeholder="分类"
        clearable
        style="width: 150px; margin-left: 10px;"
        class="filter-item"
      >
        <el-option
          v-for="item in categoryOptions"
          :key="item.id"
          :label="item.name"
          :value="item.id"
        />
      </el-select>
      <el-select
        v-model="listQuery.status"
        placeholder="状态"
        clearable
        style="width: 120px; margin-left: 10px;"
        class="filter-item"
      >
        <el-option label="上架" :value="1" />
        <el-option label="下架" :value="0" />
      </el-select>
      <el-button class="filter-item" type="primary" icon="Search" @click="handleFilter" style="margin-left: 10px;">
        搜索
      </el-button>
      <el-button class="filter-item" type="primary" icon="Plus" @click="handleCreate" style="margin-left: 10px;">
        发布商品
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%; margin-top: 20px;"
    >
      <el-table-column label="ID" prop="id" align="center" width="80" />
      
      <el-table-column label="商品图" align="center" width="100">
        <template #default="{ row }">
          <el-image
            style="width: 60px; height: 60px"
            :src="row.thumb_url"
            :preview-src-list="[row.thumb_url]"
            fit="cover"
            preview-teleported
          >
             <template #error>
              <div class="image-slot">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </template>
      </el-table-column>

      <el-table-column label="商品名称" min-width="200">
        <template #default="{ row }">
          <div class="product-name">{{ row.name }}</div>
          <div class="product-desc">{{ row.description }}</div>
        </template>
      </el-table-column>

      <el-table-column label="价格" align="center" width="120">
        <template #default="{ row }">
          <div>¥{{ row.price }}</div>
          <div v-if="row.original_price" class="original-price">¥{{ row.original_price }}</div>
        </template>
      </el-table-column>

      <el-table-column label="库存" prop="stock" align="center" width="100" />
      <el-table-column label="销量" prop="sales_count" align="center" width="100" />

      <el-table-column label="状态" align="center" width="100">
        <template #default="{ row }">
          <el-switch
            v-model="row.status"
            :active-value="1"
            :inactive-value="0"
            @change="(val) => handleStatusChange(row, val)"
          />
        </template>
      </el-table-column>

      <el-table-column label="操作" align="center" width="150" class-name="small-padding fixed-width">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleUpdate(row)">
            编辑
          </el-button>
          <el-button type="danger" link @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="listQuery.page"
        v-model:page-size="listQuery.size"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleFilter"
        @current-change="fetchList"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProductList, updateProductStatus, deleteProduct, getCategoryList } from '@/api/product'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

const list = ref([])
const total = ref(0)
const listLoading = ref(true)
const categoryOptions = ref([])

const listQuery = reactive({
  page: 1,
  size: 10,
  name: undefined,
  category_id: undefined,
  status: undefined
})

const fetchCategories = async () => {
  try {
    const res = await getCategoryList()
    categoryOptions.value = res
  } catch (error) {
    console.error(error)
  }
}

const fetchList = async () => {
  listLoading.value = true
  try {
    const res = await getProductList(listQuery)
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
  fetchList()
}

const handleCreate = () => {
  router.push('/product/add')
}

const handleUpdate = (row) => {
  router.push(`/product/edit/${row.id}`)
}

const handleStatusChange = async (row, status) => {
  try {
    await updateProductStatus(row.id, status)
    ElMessage.success('状态更新成功')
  } catch (error) {
    row.status = status === 1 ? 0 : 1 // Revert on error
    console.error(error)
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该商品?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteProduct(row.id)
      ElMessage.success('删除成功')
      fetchList()
    } catch (error) {
      console.error(error)
    }
  })
}

onMounted(() => {
  fetchCategories()
  fetchList()
})
</script>

<style scoped>
.filter-container {
  padding-bottom: 20px;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
.product-name {
  font-weight: bold;
}
.product-desc {
  font-size: 12px;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.original-price {
  font-size: 12px;
  color: #999;
  text-decoration: line-through;
}
.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 20px;
}
</style>
