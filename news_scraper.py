#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自动化新闻采集工具主程序
支持从RSS源、Google News和直接网站抓取新闻内容
"""

import os
import json
import datetime
import feedparser
import newspaper
from newspaper import Article
import requests
from pygooglenews import GoogleNews
from dotenv import load_dotenv
import pandas as pd
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 创建数据目录
data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)

class NewsScraperAutomation:
    """自动化新闻采集工具类"""
    
    def __init__(self):
        """初始化新闻采集器"""
        self.news_sources = {}
        self.load_news_sources()
        self.gn = GoogleNews(lang='zh', country='CN')  # 可根据需要修改语言和国家
        
    def load_news_sources(self):
        """从配置文件加载新闻源"""
        # 从环境变量或配置文件加载新闻源
        sources_str = os.getenv('NEWS_SOURCES', 'cnn,bbc,theguardian')
        sources = sources_str.split(',')
        
        # 预定义的新闻源配置
        predefined_sources = {
            'cnn': {
                'link': 'http://edition.cnn.com/',
                'rss': 'http://rss.cnn.com/rss/edition.rss'
            },
            'bbc': {
                'link': 'http://www.bbc.com/',
                'rss': 'http://feeds.bbci.co.uk/news/rss.xml'
            },
            'theguardian': {
                'link': 'https://www.theguardian.com/international',
                'rss': 'https://www.theguardian.com/international/rss'
            },
            'xinhua': {
                'link': 'http://www.xinhuanet.com/',
                'rss': 'http://www.xinhuanet.com/english/rss/chinarss.xml'
            }
        }
        
        # 加载配置的新闻源
        for source in sources:
            source = source.strip()
            if source in predefined_sources:
                self.news_sources[source] = predefined_sources[source]
            else:
                logger.warning(f'未知的新闻源: {source}')
        
        logger.info(f'已加载 {len(self.news_sources)} 个新闻源')
    
    def scrape_from_rss(self, source_name, rss_url, limit=10):
        """从RSS源抓取新闻
        
        Args:
            source_name: 新闻源名称
            rss_url: RSS源URL
            limit: 最大抓取数量
            
        Returns:
            list: 抓取的新闻列表
        """
        logger.info(f'从 {source_name} RSS源抓取新闻')
        articles = []
        
        try:
            feed = feedparser.parse(rss_url)
            
            for i, entry in enumerate(feed.entries):
                if i >= limit:
                    break
                    
                article = {}
                article['title'] = entry.title
                article['link'] = entry.link
                
                # 提取发布日期
                if hasattr(entry, 'published'):
                    article['published'] = entry.published
                elif hasattr(entry, 'pubDate'):
                    article['published'] = entry.pubDate
                else:
                    article['published'] = datetime.datetime.now().isoformat()
                
                # 提取摘要
                if hasattr(entry, 'summary'):
                    article['summary'] = entry.summary
                else:
                    article['summary'] = ''
                    
                article['source'] = source_name
                
                # 使用newspaper库提取完整内容
                try:
                    news_article = Article(entry.link)
                    news_article.download()
                    news_article.parse()
                    
                    article['text'] = news_article.text
                    article['authors'] = news_article.authors
                    article['top_image'] = news_article.top_image
                    
                    # 如果newspaper能提取到发布日期，优先使用
                    if news_article.publish_date:
                        article['published'] = news_article.publish_date.isoformat()
                        
                except Exception as e:
                    logger.error(f'提取文章内容失败: {entry.link}, 错误: {str(e)}')
                    article['text'] = ''
                    article['authors'] = []
                    article['top_image'] = ''
                
                articles.append(article)
                logger.debug(f'已抓取文章: {article["title"]}')
                
        except Exception as e:
            logger.error(f'从 {source_name} 抓取失败: {str(e)}')
            
        logger.info(f'从 {source_name} 成功抓取 {len(articles)} 篇文章')
        return articles
    
    def scrape_from_google_news(self, query=None, topic=None, location=None, limit=10):
        """从Google News抓取新闻
        
        Args:
            query: 搜索关键词
            topic: 主题类别
            location: 地理位置
            limit: 最大抓取数量
            
        Returns:
            list: 抓取的新闻列表
        """
        articles = []
        
        try:
            if query:
                logger.info(f'从Google News搜索: {query}')
                results = self.gn.search(query)
            elif topic:
                logger.info(f'从Google News获取主题: {topic}')
                results = self.gn.topic_headlines(topic)
            elif location:
                logger.info(f'从Google News获取地区: {location}')
                results = self.gn.geo_headlines(location)
            else:
                logger.info('从Google News获取热门新闻')
                results = self.gn.top_news()
            
            for i, entry in enumerate(results['entries']):
                if i >= limit:
                    break
                    
                article = {}
                article['title'] = entry.title
                article['link'] = entry.link
                article['published'] = entry.published
                article['summary'] = entry.summary
                article['source'] = entry.source.title if hasattr(entry, 'source') else 'Google News'
                
                # 使用newspaper库提取完整内容
                try:
                    news_article = Article(entry.link)
                    news_article.download()
                    news_article.parse()
                    
                    article['text'] = news_article.text
                    article['authors'] = news_article.authors
                    article['top_image'] = news_article.top_image
                    
                    # 如果newspaper能提取到发布日期，优先使用
                    if news_article.publish_date:
                        article['published'] = news_article.publish_date.isoformat()
                        
                except Exception as e:
                    logger.error(f'提取文章内容失败: {entry.link}, 错误: {str(e)}')
                    article['text'] = ''
                    article['authors'] = []
                    article['top_image'] = ''
                
                articles.append(article)
                logger.debug(f'已抓取文章: {article["title"]}')
                
        except Exception as e:
            logger.error(f'从Google News抓取失败: {str(e)}')
            
        logger.info(f'从Google News成功抓取 {len(articles)} 篇文章')
        return articles
    
    def scrape_from_website(self, url, limit=5):
        """直接从网站抓取新闻
        
        Args:
            url: 网站URL
            limit: 最大抓取数量
            
        Returns:
            list: 抓取的新闻列表
        """
        logger.info(f'从网站抓取: {url}')
        articles = []
        
        try:
            # 使用newspaper库抓取网站
            news_site = newspaper.build(url, memoize_articles=False)
            
            for i, article_url in enumerate(news_site.article_urls()):
                if i >= limit:
                    break
                    
                try:
                    news_article = Article(article_url)
                    news_article.download()
                    news_article.parse()
                    
                    article = {}
                    article['title'] = news_article.title
                    article['link'] = article_url
                    article['text'] = news_article.text
                    article['authors'] = news_article.authors
                    article['top_image'] = news_article.top_image
                    
                    # 设置发布日期
                    if news_article.publish_date:
                        article['published'] = news_article.publish_date.isoformat()
                    else:
                        article['published'] = datetime.datetime.now().isoformat()
                        
                    article['source'] = url
                    article['summary'] = news_article.summary
                    
                    articles.append(article)
                    logger.debug(f'已抓取文章: {article["title"]}')
                    
                except Exception as e:
                    logger.error(f'提取文章内容失败: {article_url}, 错误: {str(e)}')
                    
            logger.info(f'从 {url} 成功抓取 {len(articles)} 篇文章')
            
        except Exception as e:
            logger.error(f'从 {url} 抓取失败: {str(e)}')
            
        return articles
    
    def save_articles(self, articles, source_name):
        """保存抓取的文章
        
        Args:
            articles: 文章列表
            source_name: 来源名称
        """
        if not articles:
            logger.warning(f'没有从 {source_name} 抓取到文章')
            return
            
        # 创建按日期和来源的目录
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        source_dir = os.path.join(data_dir, today, source_name)
        os.makedirs(source_dir, exist_ok=True)
        
        # 保存为JSON文件
        filename = os.path.join(source_dir, f'{source_name}_{int(time.time())}.json')
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
            
        logger.info(f'已保存 {len(articles)} 篇文章到 {filename}')
        
        # 同时保存为CSV格式方便查看
        try:
            # 提取主要字段
            df_data = []
            for article in articles:
                df_data.append({
                    'title': article.get('title', ''),
                    'published': article.get('published', ''),
                    'source': article.get('source', ''),
                    'link': article.get('link', ''),
                    'summary': article.get('summary', '')[:100] + '...' if article.get('summary', '') else ''
                })
                
            if df_data:
                df = pd.DataFrame(df_data)
                csv_filename = os.path.join(source_dir, f'{source_name}_{int(time.time())}.csv')
                df.to_csv(csv_filename, index=False, encoding='utf-8')
                logger.info(f'已保存CSV格式到 {csv_filename}')
        except Exception as e:
            logger.error(f'保存CSV失败: {str(e)}')
    
    def run(self):
        """运行新闻采集"""
        logger.info('开始新闻采集任务')
        
        # 从RSS源采集
        for source_name, source_info in self.news_sources.items():
            if 'rss' in source_info:
                articles = self.scrape_from_rss(source_name, source_info['rss'])
                self.save_articles(articles, source_name)
            else:
                logger.warning(f'{source_name} 没有配置RSS源')
                
        # 从Google News采集热门新闻
        articles = self.scrape_from_google_news()
        self.save_articles(articles, 'google_news_top')
        
        # 可以添加更多自定义采集任务
        # 例如，采集特定主题的新闻
        topics = ['business', 'technology', 'health']
        for topic in topics:
            articles = self.scrape_from_google_news(topic=topic)
            self.save_articles(articles, f'google_news_{topic}')
            
        logger.info('新闻采集任务完成')


if __name__ == '__main__':
    scraper = NewsScraperAutomation()
    scraper.run()
