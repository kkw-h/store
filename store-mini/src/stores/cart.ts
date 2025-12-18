import { defineStore } from 'pinia';
import { cartApi } from '@/api/cart';
import type { CartItem } from '@/api/types';

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [] as CartItem[],
    totalAmount: '0.00',
    selectedCount: 0,
  }),
  getters: {
    totalCount: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
    // totalPrice is now calculated by backend usually, but we have totalAmount from list response
    totalPrice: (state) => state.totalAmount,
  },
  actions: {
    async fetchList() {
      try {
        const res = await cartApi.list();
        this.items = res.list;
        this.totalAmount = res.total_amount;
        this.selectedCount = res.selected_count;
      } catch (error) {
        console.error('Failed to fetch cart list', error);
      }
    },
    async addItem(productId: number, count: number = 1) {
      try {
        await cartApi.add({ product_id: productId, quantity: count });
        await this.fetchList();
        uni.showToast({ title: '已加入购物车', icon: 'success' });
      } catch (error) {
        console.error('Failed to add item', error);
      }
    },
    async updateItem(cartId: number, quantity: number, selected?: boolean) {
      try {
        await cartApi.update({ id: cartId, quantity, selected });
        await this.fetchList();
      } catch (error) {
        console.error('Failed to update item', error);
      }
    },
    async deleteItem(cartIds: number[]) {
      try {
        await cartApi.delete(cartIds);
        await this.fetchList();
      } catch (error) {
        console.error('Failed to delete item', error);
      }
    },
  },
});
