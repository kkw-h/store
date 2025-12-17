import oss2
import os
from app.core.config import settings

def find_bucket():
    auth = oss2.Auth(settings.ALIYUN_OSS_ACCESS_KEY_ID, settings.ALIYUN_OSS_ACCESS_KEY_SECRET)
    service = oss2.Service(auth, settings.ALIYUN_OSS_ENDPOINT)
    
    print("Listing buckets...")
    try:
        buckets = [b.name for b in oss2.BucketIterator(service)]
        if buckets:
            print(f"Found buckets: {buckets}")
            return buckets[0]
        else:
            print("No buckets found.")
            return None
    except Exception as e:
        print(f"Error listing buckets: {e}")
        return None

if __name__ == "__main__":
    bucket = find_bucket()
    if bucket:
        print(f"Recommended bucket: {bucket}")
    else:
        print("Could not find any bucket. Please create one.")
