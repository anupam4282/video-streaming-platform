import os
class Storage:
    def __init__(self):
        self.bucket=os.getenv("AWS_S3_BUCKET","").strip(); self.region=os.getenv("AWS_REGION","us-east-1"); self.uses_s3=bool(self.bucket)
        if self.uses_s3:
            import boto3
            self.client=boto3.client("s3",region_name=self.region,aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
        else:self.client=None
    def save(self,path,key):
        if not self.uses_s3:return key
        self.client.upload_file(path,self.bucket,key); return key
    def delete(self,key):
        if self.uses_s3:self.client.delete_object(Bucket=self.bucket,Key=key)
    def url(self,key):
        if not self.uses_s3:return key
        return self.client.generate_presigned_url("get_object",Params={"Bucket":self.bucket,"Key":key},ExpiresIn=3600)
