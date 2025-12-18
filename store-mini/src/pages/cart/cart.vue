<template>
  <view class="container">
    <view class="cart-list" v-if="cartStore.items.length > 0">
      <view class="cart-item" v-for="item in cartStore.items" :key="item.id">
        <image class="thumb" :src="item.product_image" mode="aspectFill"></image>
        <view class="info">
          <text class="name">{{ item.product_name }}</text>
          <view class="price-row">
            <text class="price">¥{{ formatPrice(item.price) }}</text>
            <view class="stepper">
              <view class="btn minus" @click="updateCount(item.id, item.quantity - 1)">-</view>
              <text class="count">{{ item.quantity }}</text>
              <view class="btn plus" @click="updateCount(item.id, item.quantity + 1)">+</view>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <view class="empty-state" v-else>
      <text class="empty-text">购物车是空的</text>
      <button class="go-shop-btn" @click="goShopping">去逛逛</button>
    </view>
    
    <!-- Bottom Bar -->
    <view class="bottom-bar" v-if="cartStore.items.length > 0">
      <view class="total-info">
        <text>合计：</text>
        <text class="total-price">¥{{ cartStore.totalPrice }}</text>
      </view>
      <view class="checkout-btn" @click="checkout">
        去结算 ({{ cartStore.totalCount }})
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app';
import { useCartStore } from '@/stores/cart';

const cartStore = useCartStore();

onShow(() => {
  cartStore.fetchList();
});

const updateCount = (id: number, count: number) => {
  if (count <= 0) {
    uni.showModal({
      title: '提示',
      content: '确定要删除该商品吗？',
      success: (res) => {
        if (res.confirm) {
          cartStore.deleteItem([id]);
        }
      }
    });
  } else {
    cartStore.updateItem(id, count);
  }
};

const goShopping = () => {
  uni.switchTab({ url: '/pages/category/category' });
};

const checkout = () => {
  uni.showToast({ title: '去结算功能开发中', icon: 'none' });
  // uni.navigateTo({ url: '/pages/order/create' });
};

const formatPrice = (price: string | number) => {
    return Number(price).toFixed(2);
}
</script>

<style lang="scss">
.container {
  padding-bottom: 120rpx;
  background-color: #f8f8f8;
  min-height: 100vh;
}

.cart-list {
  padding: 20rpx;
}

.cart-item {
  display: flex;
  background: #fff;
  padding: 20rpx;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
  align-items: center;
  
  .thumb {
    width: 140rpx;
    height: 140rpx;
    border-radius: 8rpx;
    margin-right: 20rpx;
    background: #eee;
  }
  
  .info {
    flex: 1;
    height: 140rpx;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    
    .name {
      font-size: 28rpx;
      color: #333;
      font-weight: 500;
    }
    
    .price-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .price {
        font-size: 32rpx;
        color: #ff5000;
        font-weight: bold;
      }
      
      .stepper {
        display: flex;
        align-items: center;
        border: 1px solid #ddd;
        border-radius: 4rpx;
        
        .btn {
          width: 50rpx;
          height: 50rpx;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 30rpx;
          color: #666;
          background: #f8f8f8;
          
          &.minus {
            border-right: 1px solid #ddd;
          }
          
          &.plus {
            border-left: 1px solid #ddd;
          }
        }
        
        .count {
          width: 60rpx;
          text-align: center;
          font-size: 28rpx;
          color: #333;
        }
      }
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-top: 200rpx;
  
  .empty-text {
    font-size: 28rpx;
    color: #999;
    margin-bottom: 30rpx;
  }
  
  .go-shop-btn {
    font-size: 28rpx;
    color: #3cc51f;
    border: 1px solid #3cc51f;
    background: #fff;
    padding: 10rpx 40rpx;
    border-radius: 30rpx;
  }
}

.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  /* #ifdef H5 */
  bottom: 50px; /* TabBar height */
  /* #endif */
  height: 100rpx;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30rpx;
  box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
  z-index: 100;
  
  .total-info {
    font-size: 28rpx;
    color: #333;
    
    .total-price {
      font-size: 36rpx;
      color: #ff5000;
      font-weight: bold;
      margin-left: 10rpx;
    }
  }
  
  .checkout-btn {
    background: #3cc51f;
    color: #fff;
    font-size: 30rpx;
    padding: 16rpx 40rpx;
    border-radius: 40rpx;
  }
}
</style>
