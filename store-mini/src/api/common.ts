import type { FileOut } from './types';

const BASE_URL = 'http://localhost:8000/api/v1';

export const commonApi = {
  uploadFile: (filePath: string) => {
    return new Promise<FileOut>((resolve, reject) => {
      const token = uni.getStorageSync('token');
      
      uni.uploadFile({
        url: `${BASE_URL}/upload`,
        filePath: filePath,
        name: 'file',
        header: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
        success: (res) => {
          const statusCode = res.statusCode;
          if (statusCode >= 200 && statusCode < 300) {
            // uni.uploadFile returns data as string
            try {
              const data = JSON.parse(res.data);
              if (data.code === 200) {
                resolve(data.data);
              } else {
                uni.showToast({
                  title: data.msg || 'Upload failed',
                  icon: 'none'
                });
                reject(data);
              }
            } catch (e) {
              reject(e);
            }
          } else {
            uni.showToast({
              title: 'Upload failed',
              icon: 'none'
            });
            reject(res);
          }
        },
        fail: (err) => {
          uni.showToast({
            title: 'Network error',
            icon: 'none'
          });
          reject(err);
        }
      });
    });
  }
};
