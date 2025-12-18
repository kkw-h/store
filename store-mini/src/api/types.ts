export interface Category {
  id: number;
  name: string;
  sort_order: number;
  is_visible: boolean;
}

export interface Product {
  id: number;
  category_id: number;
  name: string;
  description?: string;
  thumb_url?: string;
  price: string;
  original_price?: string;
  stock: number;
  status: number;
  sales_count: number;
  specs?: any;
}

export interface ProductListParams {
  category_id?: number;
  keyword?: string;
  page?: number;
  size?: number;
}

export interface ProductListResponse {
  list: Product[];
  total: number;
  page: number;
  size: number;
}

export interface CartItem {
  id: number;
  product_id: number;
  product_name: string;
  product_image?: string;
  price: string;
  quantity: number;
  selected: boolean;
  stock: number;
}

export interface CartListResponse {
  list: CartItem[];
  total_amount: string;
  selected_count: number;
}

export interface AddToCartParams {
  product_id: number;
  quantity?: number;
}

export interface UpdateCartParams {
  quantity?: number;
  selected?: boolean;
}

export interface LoginParams {
  code: string;
}

export interface UserInfo {
  id: number;
  username?: string;
  nickname?: string;
  avatar?: string;
  phone?: string;
}

export interface LoginResponse {
  token: string;
  userInfo: UserInfo;
}

export interface UserUpdateParams {
  nickname?: string;
  avatar?: string;
}

export interface FileOut {
  path: string;
  url: string;
}
