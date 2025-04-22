# 自动化新闻采集工具

这是一个基于Python的自动化新闻采集工具，支持从多个新闻源采集内容并自动同步到GitHub仓库。

## 功能特点

- 支持从RSS源自动采集新闻
- 支持从Google News采集热门新闻
- 支持从指定网站直接采集新闻内容
- 自动提取新闻标题、内容、发布日期和来源
- 定时自动运行采集任务
- 将采集结果保存为结构化数据（JSON和CSV格式）
- 自动同步到GitHub仓库

## 技术栈

- **newspaper3k**: 强大的文章提取和解析库
- **feedparser**: RSS源解析库
- **pygooglenews**: Google News非官方API封装
- **pandas**: 数据处理和CSV导出
- **schedule**: 定时任务调度
- **python-dotenv**: 环境变量管理

## 安装方法

```bash
git clone https://github.com/xianfeixu/news-scraper-automation.git
cd news-scraper-automation
pip install -r requirements.txt
```

## 配置说明

在使用前，请先创建`.env`文件并配置以下参数（可以复制`.env.example`并重命名）：

```
# 新闻源配置
NEWS_SOURCES=cnn,bbc,theguardian,xinhua

# GitHub配置
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your_username/your_repo

# 采集频率配置（小时）
SCRAPE_INTERVAL=6
```

## 使用方法

### 基本使用（单次采集）

```bash
python news_scraper.py
```

### 定时任务（持续采集）

```bash
python scheduler.py
```

### 手动同步到GitHub

```bash
python github_sync.py
```

## 数据输出

采集的新闻数据将保存在`data`目录下，按日期和来源分类存储：

```
data/
  └── 2025-04-22/
      ├── bbc/
      │   ├── bbc_1714503245.json
      │   └── bbc_1714503245.csv
      ├── cnn/
      │   ├── cnn_1714503247.json
      │   └── cnn_1714503247.csv
      └── google_news_top/
          ├── google_news_top_1714503250.json
          └── google_news_top_1714503250.csv
```

## 自定义新闻源

您可以通过修改`news_scraper.py`中的`predefined_sources`字典来添加更多新闻源：

```python
predefined_sources = {
    'new_source_name': {
        'link': 'https://example.com/',
        'rss': 'https://example.com/feed.xml'
    },
    # 更多新闻源...
}
```

## 贡献指南

欢迎提交问题和功能请求！如果您想贡献代码，请先fork本仓库，然后提交拉取请求。

## 许可证

MIT