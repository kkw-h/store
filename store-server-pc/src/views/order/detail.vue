<template>
  <div class="app-container">
    <div class="header-actions">
      <el-button icon="ArrowLeft" @click="router.back()">返回列表</el-button>
      <div class="order-status">
        当前状态：<span class="status-text">{{ order.status_text }}</span>
      </div>
    </div>

    <el-row :gutter="20" class="info-section">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>订单信息</span>
            </div>
          </template>
          <div class="info-item">
            <span class="label">订单号：</span>
            <span>{{ order.order_no }}</span>
          </div>
          <div class="info-item">
            <span class="label">下单时间：</span>
            <span>{{ formatTime(order.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="label">配送方式：</span>
            <el-tag size="small">{{ order.delivery_type === 'delivery' ? '配送' : '自提' }}</el-tag>
          </div>
          <div class="info-item" v-if="order.delivery_type === 'pickup'">
            <span class="label">核销码：</span>
            <span class="code">{{ order.pickup_code }}</span>
          </div>
          <div class="info-item">
            <span class="label">备注：</span>
            <span>{{ order.remark || '无' }}</span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>收货人信息</span>
            </div>
          </template>
          <div class="info-item">
            <span class="label">姓名：</span>
            <span>{{ order.address_snapshot?.name || '--' }}</span>
          </div>
          <div class="info-item">
            <span class="label">电话：</span>
            <span>{{ order.address_snapshot?.phone || '--' }}</span>
          </div>
          <div class="info-item" v-if="order.delivery_type === 'delivery'">
            <span class="label">地址：</span>
            <span>{{ order.address_snapshot?.address || '--' }}</span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>金额信息</span>
            </div>
          </template>
          <div class="info-item">
            <span class="label">商品总额：</span>
            <span>¥{{ order.total_amount }}</span>
          </div>
          <div class="info-item">
            <span class="label">运费：</span>
            <span>¥{{ order.delivery_fee }}</span>
          </div>
          <div class="info-item total-amount">
            <span class="label">实付金额：</span>
            <span class="amount">¥{{ order.final_amount }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="goods-section" shadow="never">
      <template #header>
        <span>商品清单</span>
      </template>
      <el-table :data="order.items" border style="width: 100%">
        <el-table-column label="商品图" width="100" align="center">
          <template #default="{ row }">
            <el-image
              style="width: 60px; height: 60px"
              :src="row.product_image"
              :preview-src-list="[row.product_image]"
              fit="cover"
              preview-teleported
            />
          </template>
        </el-table-column>
        <el-table-column label="商品名称" prop="product_name" />
        <el-table-column label="规格" prop="specs" />
        <el-table-column label="单价" prop="price" align="center">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column label="数量" prop="quantity" align="center" />
        <el-table-column label="小计" align="center">
          <template #default="{ row }">¥{{ (row.price * row.quantity).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="timeline-section" shadow="never">
      <template #header>
        <span>订单动态</span>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="(activity, index) in order.timeline"
          :key="index"
          :timestamp="formatTime(activity.created_at)"
          :type="index === 0 ? 'primary' : ''"
        >
          <h4>{{ activity.status }}</h4>
          <p>{{ activity.remark }}</p>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <div class="footer-actions">
      <!-- 待接单 (配送单) -->
      <template v-if="order.status === 1 && order.delivery_type === 'delivery'">
        <el-button type="success" @click="handleAudit('accept')">接单</el-button>
        <el-button type="danger" @click="handleReject">拒单</el-button>
      </template>

      <!-- 配送中 -->
      <template v-if="order.status === 3">
        <el-button type="success" @click="handleCompleteDelivery">确认送达</el-button>
      </template>

      <!-- 待自提 -->
      <template v-if="order.status === 2">
        <el-button type="primary" @click="handleVerify">确认核销</el-button>
      </template>
    </div>

    <!-- 拒单对话框 -->
    <el-dialog
      title="拒单确认"
      v-model="rejectDialogVisible"
      width="500px"
    >
      <div class="reject-warning">
        <el-icon color="#F56C6C"><Warning /></el-icon>
        <span>拒单后订单将自动关闭并退款给用户，此操作不可撤销。</span>
      </div>
      
      <el-form label-position="top">
        <el-form-item label="拒单原因">
          <el-input
            v-model="rejectReason"
            type="textarea"
            :rows="3"
            placeholder="请输入拒单原因（必填）"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="常用原因">
          <div class="reason-tags">
            <el-tag 
              v-for="tag in commonReasons" 
              :key="tag"
              class="reason-tag"
              type="info"
              effect="plain"
              @click="rejectReason = tag"
            >
              {{ tag }}
            </el-tag>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="rejectDialogVisible = false">取消</el-button>
          <el-button type="danger" :loading="rejecting" @click="confirmReject">
            确认拒单
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 确认送达对话框 -->
    <el-dialog
      title="送达确认"
      v-model="completeDialogVisible"
      width="400px"
    >
      <div class="complete-confirm">
        <el-icon class="confirm-icon" color="#67C23A"><SuccessFilled /></el-icon>
        <div class="confirm-text">
          <h3>确认已将商品送达给用户？</h3>
          <p>确认后订单状态将变更为“已完成”</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="completeDialogVisible = false">取消</el-button>
          <el-button type="success" :loading="completing" @click="confirmComplete">
            确认送达
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOrderDetail, auditOrder, completeDelivery, verifyPickup } from '@/api/order'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const order = ref({
  items: [],
  timeline: []
})

// 确认送达相关
const completeDialogVisible = ref(false)
const completing = ref(false)

// 拒单相关
const rejectDialogVisible = ref(false)
const rejecting = ref(false)
const rejectReason = ref('')
const commonReasons = ['商品缺货', '无法配送', '用户要求取消', '地址超出配送范围']

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const fetchData = async () => {
  try {
    const res = await getOrderDetail(route.params.id)
    order.value = res
  } catch (error) {
    console.error(error)
  }
}

const handleAudit = async (action) => {
  try {
    await auditOrder({ order_id: order.value.id, action })
    ElMessage.success('操作成功')
    fetchData()
  } catch (error) {
    console.error(error)
  }
}

const handleReject = () => {
  rejectReason.value = ''
  rejectDialogVisible.value = true
}

const confirmReject = async () => {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请输入拒单原因')
    return
  }

  rejecting.value = true
  try {
    await auditOrder({
      order_id: order.value.id,
      action: 'reject',
      reject_reason: rejectReason.value
    })
    ElMessage.success('已拒单')
    rejectDialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error(error)
  } finally {
    rejecting.value = false
  }
}

const handleCompleteDelivery = () => {
  completeDialogVisible.value = true
}

const confirmComplete = async () => {
  completing.value = true
  try {
    await completeDelivery({ order_id: order.value.id })
    ElMessage.success('操作成功')
    completeDialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error(error)
  } finally {
    completing.value = false
  }
}

const handleVerify = () => {
  ElMessageBox.confirm('确认核销该订单?', '核销确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      if (!order.value.pickup_code) {
        ElMessage.error('订单缺少核销码')
        return
      }
      await verifyPickup({ code: order.value.pickup_code })
      ElMessage.success('核销成功')
      fetchData()
    } catch (error) {
      console.error(error)
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.status-text {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
}

.info-section {
  margin-bottom: 20px;
}

.info-item {
  margin-bottom: 10px;
  font-size: 14px;
  display: flex;
}

.label {
  color: #909399;
  width: 80px;
  flex-shrink: 0;
}

.code {
  font-weight: bold;
  color: #F56C6C;
  font-size: 16px;
}

.total-amount {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px dashed #eee;
}

.amount {
  color: #F56C6C;
  font-size: 18px;
  font-weight: bold;
}

.goods-section {
  margin-bottom: 20px;
}

.timeline-section {
  margin-bottom: 20px;
}

.footer-actions {
  position: fixed;
  bottom: 0;
  right: 0;
  left: 220px; /* Sidebar width */
  padding: 20px;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  z-index: 99;
}

.reject-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background-color: #fef0f0;
  border-radius: 4px;
  color: #f56c6c;
  font-size: 14px;
  margin-bottom: 20px;
}

.reason-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.reason-tag {
  cursor: pointer;
  user-select: none;
  transition: all 0.3s;
}

.reason-tag:hover {
  color: #409EFF;
  border-color: #409EFF;
  background-color: #ecf5ff;
}

.complete-confirm {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px 0;
}

.confirm-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.confirm-text h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.confirm-text p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}
</style>
