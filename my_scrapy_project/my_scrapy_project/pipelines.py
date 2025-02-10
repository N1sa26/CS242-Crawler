import json  # 确保使用的是 Python 的 json，而不是 Scrapy 内部的 json 解析模块

class JsonPipeline:
    def open_spider(self, spider):
        """ 打开 JSON 文件准备写入 """
        self.file = open("disaster_news.json", "w", encoding="utf-8")
        self.file.write("[\n")  # 开始 JSON 数组
        self.first_item = True  # 处理逗号问题

    def process_item(self, item, spider):
        """ 逐个存入 JSON 文件 """
        if not self.first_item:
            self.file.write(",\n")  # 逗号分隔 JSON 对象
        self.first_item = False
        json.dump(item, self.file, ensure_ascii=False, indent=4)
        return item

    def close_spider(self, spider):
        """ 关闭 JSON 文件 """
        self.file.write("\n]")  # 结束 JSON 数组
        self.file.close()
