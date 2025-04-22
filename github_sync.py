#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GitHub同步工具
用于将采集的新闻数据同步到GitHub仓库
"""

import os
import json
import base64
import requests
import logging
import datetime
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("github_sync.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class GitHubSync:
    """GitHub同步工具类"""
    
    def __init__(self):
        """初始化GitHub同步工具"""
        self.token = os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPO')
        
        if not self.token or not self.repo:
            logger.error('GitHub配置不完整，请检查.env文件')
            raise ValueError('GitHub配置不完整')
            
        self.api_url = f'https://api.github.com/repos/{self.repo}/contents'
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        logger.info(f'GitHub同步工具初始化完成，仓库: {self.repo}')
    
    def upload_file(self, local_path, repo_path):
        """上传文件到GitHub
        
        Args:
            local_path: 本地文件路径
            repo_path: 仓库中的路径
            
        Returns:
            bool: 是否上传成功
        """
        try:
            # 读取文件内容
            with open(local_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查文件是否已存在
            file_exists = False
            file_sha = None
            
            try:
                response = requests.get(f'{self.api_url}/{repo_path}', headers=self.headers)
                if response.status_code == 200:
                    file_exists = True
                    file_sha = response.json()['sha']
            except Exception as e:
                logger.debug(f'检查文件存在时出错: {str(e)}')
            
            # 准备请求数据
            data = {
                'message': f'更新文件: {repo_path} - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'content': base64.b64encode(content.encode('utf-8')).decode('utf-8')
            }
            
            if file_exists:
                data['sha'] = file_sha
                logger.info(f'更新文件: {repo_path}')
            else:
                logger.info(f'创建文件: {repo_path}')
            
            # 发送请求
            response = requests.put(f'{self.api_url}/{repo_path}', headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                logger.info(f'成功上传文件: {repo_path}')
                return True
            else:
                logger.error(f'上传文件失败: {repo_path}, 状态码: {response.status_code}, 响应: {response.text}')
                return False
                
        except Exception as e:
            logger.error(f'上传文件异常: {local_path} -> {repo_path}, 错误: {str(e)}')
            return False
    
    def sync_directory(self, local_dir, repo_dir=''):
        """同步整个目录到GitHub
        
        Args:
            local_dir: 本地目录路径
            repo_dir: 仓库中的目录路径
            
        Returns:
            int: 成功同步的文件数量
        """
        if not os.path.isdir(local_dir):
            logger.error(f'本地目录不存在: {local_dir}')
            return 0
            
        success_count = 0
        
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                # 只同步JSON和CSV文件
                if not (file.endswith('.json') or file.endswith('.csv')):
                    continue
                    
                local_path = os.path.join(root, file)
                
                # 计算相对路径
                rel_path = os.path.relpath(local_path, local_dir)
                if repo_dir:
                    repo_path = f'{repo_dir}/{rel_path}'.replace('\\', '/')
                else:
                    repo_path = rel_path.replace('\\', '/')
                
                # 上传文件
                if self.upload_file(local_path, repo_path):
                    success_count += 1
        
        logger.info(f'成功同步 {success_count} 个文件到GitHub')
        return success_count

def main():
    """主函数"""
    try:
        # 初始化同步工具
        syncer = GitHubSync()
        
        # 同步数据目录
        data_dir = 'data'
        if os.path.isdir(data_dir):
            syncer.sync_directory(data_dir)
        else:
            logger.error(f'数据目录不存在: {data_dir}')
            
    except Exception as e:
        logger.error(f'同步过程中发生错误: {str(e)}')

if __name__ == '__main__':
    main()
