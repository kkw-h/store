<template>
  <view class="container">
    <!-- User Info Header -->
    <view class="user-header">
      <button 
        class="avatar-btn" 
        open-type="chooseAvatar" 
        @chooseavatar="onChooseAvatar"
      >
        <image class="avatar" :src="userStore.userInfo?.avatar || defaultAvatar" mode="aspectFill"></image>
      </button>
      <view class="info">
        <text class="nickname" @click="openNicknameEdit">{{ userStore.userInfo?.nickname || '点击设置昵称' }}</text>
        <text class="phone">{{ userStore.userInfo?.phone || '点击登录' }}</text>
      </view>
    </view>
    
    <!-- Order Status Menu -->
    <view class="order-menu">
      <view class="menu-header">
        <text class="title">我的订单</text>
        <text class="more" @click="goToOrders(0)">查看全部 ></text>
      </view>
      <view class="status-grid">
        <view class="status-item" @click="goToOrders(1)">
          <text class="icon">📦</text>
          <text class="label">待接单</text>
        </view>
        <view class="status-item" @click="goToOrders(2)">
          <text class="icon">🚚</text>
          <text class="label">配送/自提</text>
        </view>
        <view class="status-item" @click="goToOrders(3)">
          <text class="icon">✅</text>
          <text class="label">已完成</text>
        </view>
      </view>
    </view>
    
    <!-- Function List -->
    <view class="func-list">
      <view class="func-item">
        <text>📍 收货地址管理</text>
        <text class="arrow">></text>
      </view>
      <view class="func-item">
        <text>📞 联系客服</text>
        <text class="arrow">></text>
      </view>
      <view class="func-item">
        <text>⚙️ 设置</text>
        <text class="arrow">></text>
      </view>
      <view class="func-item" v-if="userStore.isLoggedIn" @click="handleLogout">
        <text>🚪 退出登录</text>
        <text class="arrow">></text>
      </view>
    </view>

    <!-- Nickname Edit Dialog -->
    <view class="modal-mask" v-if="showNicknameDialog" @click="showNicknameDialog = false">
      <view class="modal-content" @click.stop>
        <view class="modal-title">修改昵称</view>
        <input 
          type="nickname" 
          class="nickname-input" 
          placeholder="请输入昵称" 
          v-model="tempNickname"
          @change="onNicknameChange" 
        />
        <view class="modal-btns">
          <button class="btn cancel" @click="showNicknameDialog = false">取消</button>
          <button class="btn confirm" type="primary" @click="saveNickname">确定</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { commonApi } from '@/api/common';

const userStore = useUserStore();
const defaultAvatar = 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0';

const showNicknameDialog = ref(false);
const tempNickname = ref('');

const onChooseAvatar = async (e: any) => {
  const { avatarUrl } = e.detail;
  if (!avatarUrl) return;
  
  uni.showLoading({ title: '上传中...' });
  try {
    const fileRes = await commonApi.uploadFile(avatarUrl);
    await userStore.updateUserInfo({ avatar: fileRes.url });
    uni.showToast({ title: '头像更新成功', icon: 'success' });
  } catch (error) {
    console.error('Update avatar failed:', error);
    uni.showToast({ title: '头像更新失败', icon: 'none' });
  } finally {
    uni.hideLoading();
  }
};

const openNicknameEdit = () => {
  if (!userStore.isLoggedIn) {
    userStore.login();
    return;
  }
  tempNickname.value = userStore.userInfo?.nickname || '';
  showNicknameDialog.value = true;
};

const onNicknameChange = (e: any) => {
  tempNickname.value = e.detail.value;
};

const saveNickname = async () => {
  if (!tempNickname.value.trim()) {
    uni.showToast({ title: '昵称不能为空', icon: 'none' });
    return;
  }
  
  uni.showLoading({ title: '保存中...' });
  try {
    await userStore.updateUserInfo({ nickname: tempNickname.value });
    showNicknameDialog.value = false;
    uni.showToast({ title: '昵称更新成功', icon: 'success' });
  } catch (error) {
    console.error('Update nickname failed:', error);
    uni.showToast({ title: '更新失败', icon: 'none' });
  } finally {
    uni.hideLoading();
  }
};

const goToOrders = (status: number) => {
  console.log('Go to orders status:', status);
  // uni.navigateTo({ url: `/pages/order/list?status=${status}` });
};

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout();
      }
    }
  });
};
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background-color: #f8f8f8;
}

.user-header {
  background-color: #3cc51f;
  padding: 40rpx 30rpx 80rpx;
  display: flex;
  align-items: center;
  
  .avatar-btn {
    padding: 0;
    margin: 0;
    background: none;
    line-height: normal;
    margin-right: 30rpx;
    
    &::after {
      border: none;
    }
  }

  .avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    border: 4rpx solid rgba(255,255,255,0.3);
    background: #fff;
    display: block;
  }
  
  .info {
    color: #fff;
    
    .nickname {
      font-size: 36rpx;
      font-weight: bold;
      display: block;
      margin-bottom: 10rpx;
    }
    
    .phone {
      font-size: 28rpx;
      opacity: 0.8;
    }
  }
}

.order-menu {
  background: #fff;
  margin: -40rpx 30rpx 30rpx;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05);
  
  .menu-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;
    
    .title {
      font-size: 32rpx;
      font-weight: bold;
      color: #333;
    }
    
    .more {
      font-size: 24rpx;
      color: #999;
    }
  }
  
  .status-grid {
    display: flex;
    justify-content: space-around;
    
    .status-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      
      .icon {
        font-size: 48rpx;
        margin-bottom: 10rpx;
      }
      
      .label {
        font-size: 26rpx;
        color: #666;
      }
    }
  }
}

.func-list {
  background: #fff;
  margin: 0 30rpx;
  border-radius: 16rpx;
  
  .func-item {
    padding: 30rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #f5f5f5;
    font-size: 30rpx;
    color: #333;
    
    &:last-child {
      border-bottom: none;
    }
    
    .arrow {
      color: #ccc;
    }
  }
}

.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  width: 80%;
  background: #fff;
  border-radius: 16rpx;
  padding: 40rpx;
  
  .modal-title {
    font-size: 32rpx;
    font-weight: bold;
    text-align: center;
    margin-bottom: 30rpx;
  }
  
  .nickname-input {
    background: #f5f5f5;
    height: 80rpx;
    border-radius: 8rpx;
    padding: 0 20rpx;
    margin-bottom: 40rpx;
    font-size: 28rpx;
  }
  
  .modal-btns {
    display: flex;
    gap: 20rpx;
    
    .btn {
      flex: 1;
      font-size: 28rpx;
      
      &.confirm {
        background: #3cc51f;
        color: #fff;
      }
    }
  }
}
</style>
