# pywgb
Wecom(A.K.A. WeChat Work) Group Bot python API.

## Homepage

> [ChowRex/pywgb: Wecom(A.K.A Wechat Work) Group Bot python API.](https://github.com/ChowRex/pywgb)

## How to use

1. Create a [Wecom Group Bot](https://qinglian.tencent.com/help/docs/2YhR-6/).
2. Copy the webhook URL or just the `key`. It should be like:

   - `Webhook`: *https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=UUID*
   - `Key`: *UUID*

3. Install this package: `pip install pywgb`
4. Refer code below:

   ```python
   from pywgb import TextWeComGroupBot, MarkdownWeComGroupBot
   
   KEY = "PASTE_YOUR_KEY_OR_WEBHOOKURL_HERE"
   
   # If you want to send Text message, use this.
   msg = "This is a test Text message."
   bot = TextWeComGroupBot(KEY)
   bot.send(msg)
   
   # If you want to send Markdown message, use this.
   msg = "# This is a test Markdown title message."
   bot = MarkdownWeComGroupBot(KEY)
   bot.send(msg)
   
   ```

## Official Docs

> Only Chinese version doc: [群机器人配置说明 - 文档 - 企业微信开发者中心](https://developer.work.weixin.qq.com/document/path/99110)

## Roadmap

- [x] v0.0.1: :tada: Initial project. Offering send Text and Markdown type message.
- [ ] v0.0.2: :framed_picture: Add `Picture` type message support.
- [ ] v0.0.3: :newspaper: Add `News` type message support.
- [ ] v0.0.4: :open_file_folder: Add `File` type message support.
- [ ] v0.0.5: :speaking_head: Add `Voice` type message support.
- [ ] v0.0.6: :spiral_notepad: Add `TextCard` type message support.
- [ ] v0.0.7: :card_file_box: Add `PictureCard` type message support.
- [ ] v0.1.0: :thumbsup: First FULL capacity stable version release.Fix bugs and so on.

