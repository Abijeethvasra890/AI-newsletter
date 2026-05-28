AI_RSS_FEEDS = [
    # Global tier-1 tech/AI
    "https://feeds.feedburner.com/TheHackersNews",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.wired.com/feed/tag/artificial-intelligence/rss",
    "https://www.technologyreview.com/feed/",
    "https://blog.openai.com/rss/",
    "https://www.anthropic.com/rss.xml",
    "https://deepmind.google/blog/rss/",
    "https://ai.googleblog.com/feeds/posts/default",
    "https://huggingface.co/blog/feed.xml",

    # Research
    "https://export.arxiv.org/rss/cs.AI",
    "https://export.arxiv.org/rss/cs.LG",
    "https://export.arxiv.org/rss/cs.CL",

    # Developer signal
    "https://hnrss.org/frontpage?q=AI",
    "https://hnrss.org/frontpage?q=LLM",
    "https://news.google.com/rss/search?q=AI+open+source",

    # Regional signals (keep perspective diversity)
    "https://analyticsindiamag.com/feed/",
    "https://news.google.com/rss/search?q=AI+Europe",
    "https://news.google.com/rss/search?q=AI+startup+funding",
]

MAX_ARTICLES_PER_FEED = 8
COLLECTOR_TIMEOUT = 10