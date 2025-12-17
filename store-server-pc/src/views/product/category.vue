<template>
  <div class="app-container">
    <div class="filter-container">
      <el-button type="primary" icon="Plus" @click="handleCreate">
        新增分类
      </el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%; margin-top: 20px;"
    >
      <el-table-column label="ID" prop="id" align="center" width="80" />
      <el-table-column label="分类名称" prop="name" align="center" />
      <el-table-column label="排序" prop="sort_order" align="center" width="100" />
      <el-table-column label="状态" align="center" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_visible ? 'success' : 'info'">
            {{ row.is_visible ? '显示' : '隐藏' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="200" class-name="small-padding fixed-width">
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

    <el-dialog
      :title="textMap[dialogStatus]"
      v-model="dialogFormVisible"
      width="500px"
    >
      <el-form
        ref="dataFormRef"
        :rules="rules"
        :model="temp"
        label-position="right"
        label-width="100px"
        style="width: 400px; margin-left:30px;"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="temp.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="temp.sort_order" :min="0" :max="999" label="排序" />
          <div class="tips">数值越大越靠前</div>
        </el-form-item>
        <el-form-item label="是否显示" prop="is_visible">
          <el-switch v-model="temp.is_visible" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogFormVisible = false">
            取消
          </el-button>
          <el-button type="primary" @click="dialogStatus === 'create' ? createData() : updateData()">
            确认
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { getCategoryList, createCategory, updateCategory, deleteCategory } from '@/api/product'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const listLoading = ref(true)
const dialogFormVisible = ref(false)
const dialogStatus = ref('')
const textMap = {
  update: '编辑分类',
  create: '新增分类'
}

const temp = reactive({
  id: undefined,
  name: '',
  sort_order: 0,
  is_visible: true
})

const dataFormRef = ref(null)

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

const fetchList = async () => {
  listLoading.value = true
  try {
    const res = await getCategoryList()
    list.value = res
  } catch (error) {
    console.error(error)
  } finally {
    listLoading.value = false
  }
}

const resetTemp = () => {
  temp.id = undefined
  temp.name = ''
  temp.sort_order = 0
  temp.is_visible = true
}

const handleCreate = () => {
  resetTemp()
  dialogStatus.value = 'create'
  dialogFormVisible.value = true
  nextTick(() => {
    dataFormRef.value?.clearValidate()
  })
}

const createData = () => {
  dataFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        await createCategory(temp)
        dialogFormVisible.value = false
        ElMessage.success('创建成功')
        fetchList()
      } catch (error) {
        console.error(error)
      }
    }
  })
}

const handleUpdate = (row) => {
  temp.id = row.id
  temp.name = row.name
  temp.sort_order = row.sort_order
  temp.is_visible = row.is_visible
  dialogStatus.value = 'update'
  dialogFormVisible.value = true
  nextTick(() => {
    dataFormRef.value?.clearValidate()
  })
}

const updateData = () => {
  dataFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const { id, ...data } = temp
        await updateCategory(id, data)
        dialogFormVisible.value = false
        ElMessage.success('更新成功')
        fetchList()
      } catch (error) {
        console.error(error)
      }
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该分类?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteCategory(row.id)
      ElMessage.success('删除成功')
      fetchList()
    } catch (error) {
      console.error(error)
    }
  })
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.tips {
  font-size: 12px;
  color: #999;
  margin-left: 10px;
  display: inline-block;
}
</style>
