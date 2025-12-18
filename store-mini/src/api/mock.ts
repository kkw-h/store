// src/api/mock.ts

export const mockBanners = [
  { id: 1, image: 'https://via.placeholder.com/750x300/3cc51f/ffffff?text=Fresh+Fruit', url: '/pages/category/category' },
  { id: 2, image: 'https://via.placeholder.com/750x300/ff9900/ffffff?text=Daily+Deals', url: '/pages/category/category' },
];

export const mockCategories = [
  { id: 1, name: 'Fresh Fruit' },
  { id: 2, name: 'Vegetables' },
  { id: 3, name: 'Meat & Eggs' },
  { id: 4, name: 'Seafood' },
  { id: 5, name: 'Dairy' },
  { id: 6, name: 'Snacks' },
];

export const mockProducts = [
  {
    id: 101,
    category_id: 1,
    name: 'Red Apple',
    description: 'Sweet and crispy red apples',
    thumb_url: 'https://via.placeholder.com/200x200/ff0000/ffffff?text=Apple',
    price: 5.50,
    original_price: 8.00,
    stock: 100,
    tags: ['Hot', 'Sale'],
  },
  {
    id: 102,
    category_id: 1,
    name: 'Banana',
    description: 'Imported bananas',
    thumb_url: 'https://via.placeholder.com/200x200/ffff00/000000?text=Banana',
    price: 3.99,
    original_price: 4.50,
    stock: 50,
    tags: [],
  },
  {
    id: 201,
    category_id: 2,
    name: 'Carrot',
    description: 'Organic carrots',
    thumb_url: 'https://via.placeholder.com/200x200/ff9900/ffffff?text=Carrot',
    price: 2.00,
    original_price: 2.50,
    stock: 200,
    tags: ['Organic'],
  },
];
