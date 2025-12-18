<template>
  <div class="app-container">
    <el-card>
      <div class="filter-container">
        <el-tabs v-model="listQuery.status" type="card" @tab-change="handleTabChange">
          <el-tab-pane label="全部" :name="0" />
          <el-tab-pane label="待接单" :name="1" />
          <el-tab-pane label="待自提" :name="2" />
          <el-tab-pane label="配送中" :name="3" />
          <el-tab-pane label="已完成" :name="4" />
          <el-tab-pane label="已关闭" :name="-1" />
        </el-tabs>

        <div class="filter-actions">
          <el-button type="primary" :icon="Aim" @click="dialogVisible = true">
            扫码核销
          </el-button>
          <el-button icon="Refresh" @click="fetchList">
            刷新
          </el-button>
        </div>
      </div>

      <el-table
        v-loading="listLoading"
        :data="list"
        border
        fit
        highlight-current-row
        style="width: 100%;"
      >
        <el-table-column label="订单号" prop="order_no" min-width="180" align="center" />
        
        <el-table-column label="用户信息" min-width="180" align="center">
          <template #default="{ row }">
            <div v-if="row.user" class="user-info">
              <el-avatar :size="30" :src="row.user.avatar_url" v-if="row.user.avatar_url" />
              <div class="user-detail">
                <div class="nickname">{{ row.user.nickname || '微信用户' }}</div>
                <div class="phone">{{ row.user.phone || '--' }}</div>
              </div>
            </div>
            <span v-else>--</span>
          </template>
        </el-table-column>

        <el-table-column label="配送方式" align="center" width="100">
          <template #default="{ row }">
            <el-tag :type="row.delivery_type === 'delivery' ? 'primary' : 'success'">
              {{ row.delivery_type === 'delivery' ? '配送' : '自提' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="实付金额" prop="final_amount" align="center" width="120">
          <template #default="{ row }">
            ¥{{ row.final_amount }}
          </template>
        </el-table-column>

        <el-table-column label="状态" align="center" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTypeFilter(row.status)">
              {{ row.status_text }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="下单时间" prop="created_at" align="center" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" align="center" width="220" class-name="small-padding fixed-width">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleDetail(row)">
              详情
            </el-button>
            
            <!-- 待接单 (配送单) -->
            <template v-if="row.status === 1 && row.delivery_type === 'delivery'">
              <el-button type="success" link @click="handleAudit(row, 'accept')">
                接单
              </el-button>
              <el-button type="danger" link @click="handleReject(row)">
                拒单
              </el-button>
            </template>

            <!-- 配送中 -->
            <template v-if="row.status === 3">
              <el-button type="success" link @click="handleCompleteDelivery(row)">
                确认送达
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="listQuery.page"
          v-model:page-size="listQuery.size"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="fetchList"
          @current-change="fetchList"
        />
      </div>
    </el-card>

    <!-- 核销对话框 -->
    <el-dialog
      title="自提核销"
      v-model="dialogVisible"
      width="400px"
    >
      <el-input
        v-model="pickupCode"
        placeholder="请输入或扫描6位核销码"
        :prefix-icon="Aim"
        clearable
        @keyup.enter="handleVerify"
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="verifying" @click="handleVerify">
            确认核销
          </el-button>
        </span>
      </template>
    </el-dialog>

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
      
      <el-form :model="rejectForm" label-position="top">
        <el-form-item label="拒单原因">
          <el-input
            v-model="rejectForm.reason"
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
              @click="rejectForm.reason = tag"
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOrderList, auditOrder, completeDelivery, verifyPickup } from '@/api/order'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning, SuccessFilled, Aim, Refresh } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const router = useRouter()
const list = ref([])
const total = ref(0)
const listLoading = ref(true)
const dialogVisible = ref(false)
const pickupCode = ref('')
const verifying = ref(false)

// 确认送达相关
const completeDialogVisible = ref(false)
const completing = ref(false)
const completeId = ref(null)

// 拒单相关
const rejectDialogVisible = ref(false)
const rejecting = ref(false)
const rejectForm = reactive({
  orderId: null,
  reason: ''
})
const commonReasons = ['商品缺货', '无法配送', '用户要求取消', '地址超出配送范围']

const listQuery = reactive({
  page: 1,
  size: 10,
  status: 0
})

const statusTypeFilter = (status) => {
  const statusMap = {
    1: 'warning',
    2: 'warning',
    3: 'primary',
    4: 'success',
    '-1': 'info'
  }
  return statusMap[status] || ''
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const fetchList = async () => {
  listLoading.value = true
  try {
    const res = await getOrderList(listQuery)
    list.value = res.list
    total.value = res.total
  } catch (error) {
    console.error(error)
  } finally {
    listLoading.value = false
  }
}

const handleTabChange = (val) => {
  listQuery.status = val
  listQuery.page = 1
  fetchList()
}

const handleDetail = (row) => {
  router.push(`/order/detail/${row.id}`)
}

const handleAudit = async (row, action) => {
  try {
    await auditOrder({ order_id: row.id, action })
    ElMessage.success('操作成功')
    fetchList()
  } catch (error) {
    console.error(error)
  }
}

const handleReject = (row) => {
  rejectForm.orderId = row.id
  rejectForm.reason = ''
  rejectDialogVisible.value = true
}

const confirmReject = async () => {
  if (!rejectForm.reason.trim()) {
    ElMessage.warning('请输入拒单原因')
    return
  }

  rejecting.value = true
  try {
    await auditOrder({
      order_id: rejectForm.orderId,
      action: 'reject',
      reject_reason: rejectForm.reason
    })
    ElMessage.success('已拒单')
    rejectDialogVisible.value = false
    fetchList()
  } catch (error) {
    console.error(error)
  } finally {
    rejecting.value = false
  }
}

const handleCompleteDelivery = (row) => {
  completeId.value = row.id
  completeDialogVisible.value = true
}

const confirmComplete = async () => {
  completing.value = true
  try {
    await completeDelivery({ order_id: completeId.value })
    ElMessage.success('操作成功')
    completeDialogVisible.value = false
    fetchList()
  } catch (error) {
    console.error(error)
  } finally {
    completing.value = false
  }
}

const handleVerify = async () => {
  if (!pickupCode.value) {
    ElMessage.warning('请输入核销码')
    return
  }
  
  verifying.value = true
  try {
    const res = await verifyPickup({ code: pickupCode.value })
    if (res.success) {
      ElMessageBox.alert(
        `
        <div style="text-align: center;">
          <h3 style="color: #67C23A; margin: 0;">核销成功</h3>
          <p>订单号: ${res.order_info.order_no}</p>
          <p>金额: ¥${res.order_info.total_amount}</p>
        </div>
        `, 
        '提示', 
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '确定',
          callback: () => {
            dialogVisible.value = false
            pickupCode.value = ''
            fetchList()
          }
        }
      )
    }
  } catch (error) {
    console.error(error)
  } finally {
    verifying.value = false
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.filter-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.filter-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.user-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.user-detail {
  text-align: left;
  line-height: 1.4;
}

.nickname {
  font-size: 14px;
}

.phone {
  font-size: 12px;
  color: #909399;
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
