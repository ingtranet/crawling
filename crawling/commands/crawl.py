from scrapy.commands.crawl import Command as CrawlCommand
from scrapy.exceptions import UsageError

class Command(CrawlCommand):
    def run(self, args, opts):
        if len(args) < 1:
            raise UsageError()
        elif len(args) > 1:
            raise UsageError("running 'scrapy crawl' with more than one spider is no longer supported")
        spname = args[0]

        self.crawler_process.crawl(spname, **opts.spargs)
        crawlers = [c for c in self.crawler_process.crawlers]
        self.crawler_process.start()

        if self.crawler_process.bootstrap_failed:
            self.exitcode = 1
        
        for c in crawlers:
            if c.stats.get_value('log_count/ERROR'):
                self.exitcode = 1 