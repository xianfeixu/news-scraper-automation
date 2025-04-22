#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
定时任务调度器
用于定期执行新闻采集任务并同步到GitHub
"""

import os
import time
import schedule
import logging
import datetime
import subprocess
from dotenv import load_dotenv
from news_scraper import NewsScraperAutomation

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 获取采集频率配置（小时）
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '6'))

def sync_to_github():
    """将采集结果同步到GitHub"""
    try:
        # 获取GitHub配置
        github_token = os.getenv('GITHUB_TOKEN')
        github_repo = os.getenv('GITHUB_REPO')
        
        if not github_token or not github_repo:
            logger.warning('GitHub配置不完整，跳过同步')
            return
            
        logger.info('开始同步数据到GitHub')
        
        # 获取当前时间作为提交信息
        commit_message = f'自动更新: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        
        # 执行Git命令
        commands = [
            'git add data/*',
            f'git commit -m "{commit_message}"',
            'git push origin main'
        ]
        
        for cmd in commands:
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if process.returncode != 0 and 'nothing to commit' not in process.stderr:
                logger.error(f'Git命令失败: {cmd}
{process.stderr}')
                return
                
        logger.info('成功同步数据到GitHub')
        
    except Exception as e:
        logger.error(f'同步到GitHub失败: {str(e)}')

def run_scraper_job():
    """运行采集任务并同步到GitHub"""
    try:
        logger.info('开始定时采集任务')
        
        # 运行采集器
        scraper = NewsScraperAutomation()
        scraper.run()
        
        # 同步到GitHub
        sync_to_github()
        
        logger.info('定时采集任务完成')
        
    except Exception as e:
        logger.error(f'定时任务执行失败: {str(e)}')

def main():
    """主函数"""
    logger.info(f'启动定时任务调度器，采集频率: {SCRAPE_INTERVAL}小时')
    
    # 立即运行一次
    run_scraper_job()
    
    # 设置定时任务
    schedule.every(SCRAPE_INTERVAL).hours.do(run_scraper_job)
    
    # 运行调度器
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    main()
