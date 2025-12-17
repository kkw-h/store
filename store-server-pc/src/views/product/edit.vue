<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑商品' : '发布商品' }}</span>
        </div>
      </template>
      
      <el-form
        ref="postFormRef"
        :model="postForm"
        :rules="rules"
        label-width="120px"
        class="product-form"
      >
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="postForm.name" placeholder="请输入商品名称" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="商品分类" prop="category_id">
          <el-select v-model="postForm.category_id" placeholder="请选择分类">
            <el-option
              v-for="item in categoryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="商品图片" prop="thumb_url">
          <el-upload
            class="avatar-uploader"
            action="#"
            :http-request="handleUpload"
            :show-file-list="false"
            :before-upload="beforeUpload"
          >
            <img v-if="previewUrl" :src="previewUrl" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="el-upload__tip">建议尺寸 800x800，大小不超过 2MB</div>
        </el-form-item>

        <el-form-item label="商品价格" prop="price">
          <el-input-number v-model="postForm.price" :precision="2" :step="0.1" :min="0" />
          <span class="unit">元</span>
        </el-form-item>

        <el-form-item label="划线价" prop="original_price">
          <el-input-number v-model="postForm.original_price" :precision="2" :step="0.1" :min="0" />
          <span class="unit">元</span>
        </el-form-item>

        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="postForm.stock" :min="0" :precision="0" />
        </el-form-item>

        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="postForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入商品描述"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="上架状态" prop="status">
          <el-switch
            v-model="postForm.status"
            :active-value="1"
            :inactive-value="0"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submitForm">
            {{ isEdit ? '保存修改' : '立即发布' }}
          </el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProductDetail, saveProduct, getCategoryList } from '@/api/product'
import { uploadFile } from '@/api/common'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const postFormRef = ref(null)
const loading = ref(false)
const categoryOptions = ref([])
const previewUrl = ref('')

const isEdit = computed(() => !!route.params.id)

const postForm = reactive({
  id: undefined,
  name: '',
  category_id: undefined,
  thumb_url: '',
  price: 0,
  original_price: undefined,
  stock: 0,
  description: '',
  status: 1,
  specs: null
})

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择商品分类', trigger: 'change' }],
  thumb_url: [{ required: true, message: '请上传商品图片', trigger: 'change' }],
  price: [{ required: true, message: '请输入商品价格', trigger: 'blur' }],
  stock: [{ required: true, message: '请输入库存', trigger: 'blur' }]
}

const fetchCategories = async () => {
  try {
    const res = await getCategoryList()
    categoryOptions.value = res
  } catch (error) {
    console.error(error)
  }
}

const fetchData = async (id) => {
  try {
    const res = await getProductDetail(id)
    Object.assign(postForm, res)
    // 后端 thumb_url 可能是 url (如果未转换) 或转换后的 url
    // 后端 thumb_path 是 path
    // 我们需要: postForm.thumb_url = path; previewUrl = url
    if (res.thumb_path) {
      postForm.thumb_url = res.thumb_path
      previewUrl.value = res.thumb_url
    } else {
      // 兼容旧数据或无 path 字段的情况
      postForm.thumb_url = res.thumb_url
      previewUrl.value = res.thumb_url
    }
  } catch (error) {
    console.error(error)
  }
}

const handleUpload = async (options) => {
  try {
    const res = await uploadFile(options.file)
    // res: { path: "...", url: "..." }
    postForm.thumb_url = res.path
    previewUrl.value = res.url
  } catch (error) {
    ElMessage.error('上传失败')
    console.error(error)
  }
}

const beforeUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG) {
    ElMessage.error('上传头像图片只能是 JPG/PNG 格式!')
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
  }
  return isJPG && isLt2M
}

const submitForm = () => {
  postFormRef.value?.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const { id, ...data } = postForm
        // Ensure numbers are numbers
        data.price = Number(data.price)
        if (data.original_price) data.original_price = Number(data.original_price)
        data.stock = Number(data.stock)

        await saveProduct(data, id)
        ElMessage.success(isEdit.value ? '修改成功' : '发布成功')
        router.push('/product/list')
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchCategories()
  if (isEdit.value) {
    fetchData(route.params.id)
  }
})
</script>

<style scoped>
.product-form {
  max-width: 800px;
  margin-top: 20px;
}
.unit {
  margin-left: 10px;
  color: #666;
}
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}
.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 148px;
  height: 148px;
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
}
.avatar {
  width: 148px;
  height: 148px;
  display: block;
}
</style>
