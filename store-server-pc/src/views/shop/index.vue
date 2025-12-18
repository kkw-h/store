<template>
  <div class="app-container">
    <el-card class="box-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>店铺基础设置</span>
        </div>
      </template>
      
      <el-form 
        ref="formRef"
        :model="form" 
        :rules="rules"
        label-width="120px"
        style="max-width: 600px"
      >
        <el-form-item label="店铺名称" prop="store_name">
          <el-input v-model="form.store_name" placeholder="请输入店铺名称" maxlength="50" show-word-limit />
        </el-form-item>

        <el-form-item label="营业状态" prop="is_open">
          <el-switch
            v-model="form.is_open"
            active-text="营业中"
            inactive-text="休息中"
            :active-value="1"
            :inactive-value="0"
          />
        </el-form-item>

        <el-form-item label="营业时间" required>
          <el-col :span="11">
            <el-form-item prop="open_time">
              <el-time-select
                v-model="form.open_time"
                start="00:00"
                step="00:30"
                end="23:30"
                placeholder="开始时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="2" class="text-center">
            <span class="text-gray-500">-</span>
          </el-col>
          <el-col :span="11">
            <el-form-item prop="close_time">
              <el-time-select
                v-model="form.close_time"
                start="00:00"
                step="00:30"
                end="23:30"
                placeholder="结束时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-form-item>

        <el-form-item label="起送金额" prop="min_order_amount">
          <el-input-number 
            v-model="form.min_order_amount" 
            :precision="2" 
            :step="1" 
            :min="0"
            style="width: 100%"
          >
            <template #prefix>￥</template>
          </el-input-number>
        </el-form-item>

        <el-form-item label="基础运费" prop="delivery_fee">
          <el-input-number 
            v-model="form.delivery_fee" 
            :precision="2" 
            :step="1" 
            :min="0"
            style="width: 100%"
          >
            <template #prefix>￥</template>
          </el-input-number>
        </el-form-item>

        <el-form-item label="联系电话" prop="store_phone">
          <el-input v-model="form.store_phone" placeholder="请输入店铺联系电话" />
        </el-form-item>

        <el-form-item label="店铺地址" prop="store_address">
          <el-input 
            v-model="form.store_address" 
            type="textarea" 
            rows="3" 
            placeholder="请输入详细地址"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">保存设置</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getShopConfig, updateShopConfig } from '@/api/shop'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  store_name: '',
  is_open: 1,
  open_time: '',
  close_time: '',
  min_order_amount: 0,
  delivery_fee: 0,
  store_phone: '',
  store_address: ''
})

const rules = {
  store_name: [
    { required: true, message: '请输入店铺名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  open_time: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  close_time: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ],
  min_order_amount: [
    { required: true, message: '请输入起送金额', trigger: 'blur' }
  ],
  delivery_fee: [
    { required: true, message: '请输入基础运费', trigger: 'blur' }
  ]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getShopConfig()
    Object.assign(form, res)
    // 转换布尔值为数字 (API 返回的是 boolean, form 需要 int)
    form.is_open = res.is_open ? 1 : 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await updateShopConfig(form)
        ElMessage.success('设置保存成功')
        fetchData()
      } catch (error) {
        console.error(error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const resetForm = () => {
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.text-center {
  text-align: center;
}
</style>
