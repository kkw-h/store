<template>
  <view class="container">
    <!-- Left Sidebar -->
    <scroll-view scroll-y class="sidebar">
      <view
        v-for="item in categories"
        :key="item.id"
        class="menu-item"
        :class="{ active: currentCategoryId === item.id }"
        @click="selectCategory(item.id)"
      >
        {{ item.name }}
      </view>
    </scroll-view>

    <!-- Right Content -->
    <scroll-view scroll-y class="content">
      <view class="product-list">
        <view class="product-item" v-for="item in currentProducts" :key="item.id">
          <image class="thumb" :src="item.thumb_url" mode="aspectFill"></image>
          <view class="info">
            <text class="name">{{ item.name }}</text>
            <text class="desc">{{ item.description }}</text>
            <view class="bottom">
              <text class="price">¥{{ formatPrice(item.price) }}</text>
              <view class="add-btn" @click="addToCart(item)">+</view>
            </view>
          </view>
        </view>
        <view v-if="currentProducts.length === 0" class="empty-tip">
          该分类下暂无商品
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { categoryApi } from '@/api/category';
import { productApi } from '@/api/product';
import { useCartStore } from '@/stores/cart';
import type { Category, Product } from '@/api/types';

const categories = ref<Category[]>([]);
const currentProducts = ref<Product[]>([]);
const currentCategoryId = ref(0);
const cartStore = useCartStore();

onMounted(async () => {
  await fetchCategories();
});

const fetchCategories = async () => {
  try {
    const res = await categoryApi.list();
    categories.value = res;
    if (res.length > 0) {
      currentCategoryId.value = res[0].id;
      await fetchProducts();
    }
  } catch (error) {
    console.error('Failed to fetch categories', error);
  }
};

const fetchProducts = async () => {
  try {
    const res = await productApi.list({ 
        category_id: currentCategoryId.value,
        size: 100 // Fetch all for now or implement pagination later
    });
    currentProducts.value = res.list;
  } catch (error) {
    console.error('Failed to fetch products', error);
  }
};

const selectCategory = (id: number) => {
  currentCategoryId.value = id;
  fetchProducts();
};

const addToCart = (item: Product) => {
  cartStore.addItem(item.id, 1);
};

const formatPrice = (price: string | number) => {
    return Number(price).toFixed(2);
}
</script>

<style lang="scss">
.container {
  display: flex;
  height: 100vh;
  background-color: #f8f8f8;
}

.sidebar {
  width: 180rpx;
  height: 100%;
  background-color: #f0f0f0;
  
  .menu-item {
    height: 100rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28rpx;
    color: #666;
    position: relative;
    
    &.active {
      background-color: #fff;
      color: #3cc51f;
      font-weight: bold;
      
      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 30rpx;
        bottom: 30rpx;
        width: 6rpx;
        background-color: #3cc51f;
      }
    }
  }
}

.content {
  flex: 1;
  height: 100%;
  background-color: #fff;
  
  .product-list {
    padding: 20rpx;
  }
  
  .product-item {
    display: flex;
    padding: 20rpx 0;
    border-bottom: 1px solid #f5f5f5;
    
    .thumb {
      width: 160rpx;
      height: 160rpx;
      border-radius: 8rpx;
      margin-right: 20rpx;
      background: #eee;
    }
    
    .info {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      
      .name {
        font-size: 30rpx;
        color: #333;
        font-weight: bold;
      }
      
      .desc {
        font-size: 24rpx;
        color: #999;
        margin-top: 10rpx;
      }
      
      .bottom {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .price {
          font-size: 32rpx;
          color: #ff5000;
          font-weight: bold;
        }
        
        .add-btn {
          width: 50rpx;
          height: 50rpx;
          background: #3cc51f;
          color: #fff;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 36rpx;
        }
      }
    }
  }
  
  .empty-tip {
    text-align: center;
    color: #999;
    padding-top: 100rpx;
    font-size: 28rpx;
  }
}
</style>
