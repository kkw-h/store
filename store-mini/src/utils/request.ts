// src/utils/request.ts

const BASE_URL = 'http://localhost:8000/api/v1'; // TODO: Change to real environment variable

interface RequestOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: any;
  header?: any;
}

interface ResponseData<T = any> {
  code: number;
  msg: string;
  data: T;
}

export const request = <T = any>(options: RequestOptions): Promise<T> => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token');
    
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header,
      },
      success: (res: any) => {
        const { statusCode, data } = res;
        
        if (statusCode >= 200 && statusCode < 300) {
            const result = data as ResponseData<T>;
            if (result.code === 200) {
                 resolve(result.data);
            } else {
                uni.showToast({
                    title: result.msg || 'Request failed',
                    icon: 'none'
                });
                reject(result);
            }
        } else if (statusCode === 401) {
            // Token expired or invalid
            uni.removeStorageSync('token');
            uni.showToast({
                title: 'Session expired, please login again',
                icon: 'none'
            });
            // Navigate to user page or login page
            // uni.switchTab({ url: '/pages/user/user' });
            reject(res);
        } else {
          uni.showToast({
            title: `Error: ${statusCode}`,
            icon: 'none',
          });
          reject(res);
        }
      },
      fail: (err) => {
        uni.showToast({
          title: 'Network error',
          icon: 'none',
        });
        reject(err);
      },
    });
  });
};
