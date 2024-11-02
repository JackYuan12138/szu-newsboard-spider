# szu-newsboard-spider

本项目通过 python 爬虫爬取深大公文通，可将爬虫挂在服务器上，启用邮件服务将爬取内容发送到私人邮箱，使得我们不会再错过重要的公文通信息


本项目复刻自 [szu-newsboard-spider](https://github.com/yarkable/szu-newsboard-spider)

感谢原作者的无私奉献，本项目在其基础上重新实现了公文通内容的获取，并在一些细节上进行了优化，原作者的教程依然适用，故保留
[使用教程](https://szukevin.site/2019/11/22/%E8%AE%A9python%E6%8B%AF%E6%95%91%E4%B8%8D%E7%9C%8B%E5%85%AC%E6%96%87%E9%80%9A%E7%9A%84%E6%88%91/)


新增配置参数`board_id`以及`board_password`用于登录公文通


以下为效果图（为微信内QQ邮件的预览效果）：
![board](https://cloudflare.cdnjson.com/images/2024/11/02/_20241102185502fff7c87f888c8cce.png)

