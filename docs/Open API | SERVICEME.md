## 概述[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%A6%82%E8%BF%B0 "概述的直接链接")

SERVICEME Open API 调用基本流程：

**第一步，采用身份认证章节提供的接口进行身份认证，获取 access token**

​认证分为两类，一类是用户认证，另一类是客户端认证。

*   用户认证：基于个人账号身份进行认证的方式。
*   客户端认证：用SERVICEME颁发的客户端code与secret进行认证的方式。

**第二步，携带access token调用对应的API**

## 身份认证方式[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BA%AB%E4%BB%BD%E8%AE%A4%E8%AF%81%E6%96%B9%E5%BC%8F "身份认证方式的直接链接")

### 用户AAD认证[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E7%94%A8%E6%88%B7aad%E8%AE%A4%E8%AF%81 "用户AAD认证的直接链接")

该方式属于**用户认证**的一种，需要使用到AAD的access token作为身份认证的依据。

*   **AAD access token 获取方式：**
    
    > AAD 与 React 集成文档：[前往->](https://learn.microsoft.com/en-us/azure/active-directory-b2c/configure-authentication-sample-react-spa-app)
    > 
    > AAD 与 .Net 集成文档：[前往->](https://learn.microsoft.com/en-us/azure/active-directory-b2c/configure-authentication-sample-web-app?tabs=visual-studio)
    > 
    > AAD 与 Java 集成文档：[前往->](https://learn.microsoft.com/en-us/java/api/overview/azure/activedirectory?view=azure-java-stable)
    
*   **接口地址：**`/openapi/auth/user/aad`
    
*   **请求方式：**`post`
    
*   **请求body：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| token | 是 | string | 用户AAD access token（对接方自己提供） |

*   **接口请求示例：**

```
curl --location 'https://localhost/openapi/auth/user/aad' \--header 'Content-Type: application/json' \--data '{    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IlhSdmtvOFA3QTNVYVdTblU3Yk05blQwTWpoQSJ9.eyJhdWQiOiIzZTEwNjVhYS1jZWYxLTRiYTgtOWRiOS1kMWQ1Y2UzMGYyZDgiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vNDRjMjRmNDItZDQ5Yi00MT......"}'
```

*   **响应body：**

| 参数名称 | 参数二级 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| data |  | object | 响应数据 |
|  | access\_token | string | SERVICEME系统 access token |
|  | expires\_in | number | 过期时间，单位分钟 |
| success |  | boolean | 是否成功 |
| msg |  | string | 当success为false时，该处有值，会有部分错误提示 |

*   **响应示例：**

```
{    "data": {        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0V4dGVybmFsIjpmYWxzZSwidXNlcklkIjoiNDAzMDUwMjEwMTEyODgzOTE2OCIsImFjY291bnQiOiJlY210cmlhbEBzZXJ2aWNlbWUub25taWNyb3NvZ......",        "expires_in": 1440    },    "success": true,    "msg": ""}
```

### 客户端与用户账户认证[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%AE%A2%E6%88%B7%E7%AB%AF%E4%B8%8E%E7%94%A8%E6%88%B7%E8%B4%A6%E6%88%B7%E8%AE%A4%E8%AF%81 "客户端与用户账户认证的直接链接")

这种认证方式采用客户端认证和用户账户认证相结合的方式。通过用户账户进行身份认证，同时需要使用客户端凭证(client id和secret)来确保接口调用的安全性。调用此接口时需要进行签名验证。

*   **如何获取client和secret?**

系统管理员通过客户端管理界面进行凭据创建`{domain}#/super-admin/client-management`，创建后即可获取client id和secret。

*   **接口地址：**`/openapi/auth/client_with_account`
    
*   **请求方式：**`post`
    
*   **请求body：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| client | 是 | string | 客户端Id |
| account | 是 | string | 用户账户（对应用户管理中的UserName） |
| timestamp | 是 | number | 时间戳（13位数字，精度到毫秒，如 1711537596897 ） |
| nonce | 是 | string | 6位随机数（数字或字母的组合均可） |
| signature | 是 | string | 签名，五分钟内有效（签名格式：用冒号拼接后再MD5 `client:{client}secret:{secret}account:{account}timestamp:{timestamp}nonce:{nonce}` 得到的MD5 32位长度的值转小写） |

*   **javascript 签名示例：**
    
    > 请新建一个 html 文件粘贴以下内容后使用浏览器打开
    
    > ```
    > <html>  <head>    <style>      .box {         width: 100%;         height: 100%;         padding: 50px 50px;       }       .row {            display: flex;            height: 50px;            width: 100%;          }          .col1 {            flex: 1;       }       .col2 {         flex: 3;       }     </style>   </head>   <body>      <div class="box">      <div class="row">           <div class="col1">client:</div>           <div class="col2" id="client"></div>         </div>         <div class="row">           <div class="col1">secret:</div>           <div class="col2" id="secret"></div>         </div>        <div class="row">        <div class="col1">account:</div>        <div class="col2" id="account"></div>      </div>      <div class="row">         <div class="col1">timestamp:</div>         <div class="col2" id="timestamp"></div>       </div>       <div class="row">         <div class="col1">nonce:</div>         <div class="col2" id="nonce"></div>       </div>       <div class="row">         <div class="col1">signature:</div>         <div class="col2" id="signature"></div>       </div>     </div>     <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.0.0/crypto-js.min.js"></script>     <script>       const client = "openapi"       const secret = "DzYwyICrKbUCEseYthCK0PfSfX7NPEuV"       const account = "test@serviceme.com"       const timestamp = +new Date()       const nonce = "123abc"       const message = `client:${client}secret:${secret}account:${account}timestamp:${timestamp}nonce:${nonce}` // 签名明文       const md5Hash = CryptoJS.MD5(message).toString().toLowerCase(); // MD5 32位转小写          console.log(`签名明文：${message}`)       console.log(`签名结果：${md5Hash}`)         document.getElementById('client').innerText = client;       document.getElementById('secret').innerText = secret;       document.getElementById('account').innerText = account;       document.getElementById('timestamp').innerText = timestamp;       document.getElementById('nonce').innerText = nonce;       document.getElementById('signature').innerText = md5Hash;     </script>   </body>   </html>
    > ```
    
*   **接口请求示例：**
    

```
curl --location 'https://localhost/openapi/auth/client_with_account' \--header 'Content-Type: application/json' \--data '{    "client": "openapi",    "account": "test@serviceme.com",    "timestamp": 1711537596456,    "nonce": "123abc",    "signature": "182be0c5cdcd5072bb1864cdee4d3d6e"}'
```

*   **响应body**

| 参数名称 | 参数二级 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| data |  | object | 响应数据 |
|  | access\_token | string | SERVICEME系统 access token |
|  | expires\_in | number | 过期时间，单位分钟 |
| success |  | boolean | 是否成功 |
| msg |  | string | 当success为false时，该处有值，会有部分错误提示 |

*   **接口响应示例：**

```
{    "data": {        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0V4dGVybmFsIjpmYWxzZSwidXNlcklkIjoiNDAzMDUwMjEwMTEyODgzOTE2OCIsImFjY291bnQiOiJlY210cmlhbEBzZXJ2ub25ta......",        "expires_in": 1440    },    "success": true,    "msg": ""}
```

## 聊天[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%81%8A%E5%A4%A9 "聊天的直接链接")

### 向Agent发送消息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%90%91agent%E5%8F%91%E9%80%81%E6%B6%88%E6%81%AF "向Agent发送消息的直接链接")

*   **接口地址：**`/openapi/chat/expert`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **请求body：**

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| expertCode | 是 | string | SERVICEME系统中的Agent code（见SERVICEME系统） |
| content | 是 | string | 提问内容 |
| sessionId | 否 | string | 会话id，代表一个聊天上下文，传null表示开启新会话，新会话的id会在接口响应中返回，从第二次问答开始需要携带上一次返回的session id继续 |
| stream | 否 | boolean | 是否开启流式（true：开；false：关）,默认不会开启 |
| includeThought | 否 | boolean | 是否需要在返回内容里包含想法（true：包含；false：不包含） |
| language | 否 | object | 本次聊天的语种 |
| language.chatLanguage | 否 | string | 希望AI以什么语种回复，为空则由AI自行决定 |
| language.systemLanguage | 否 | string | 会话的基础语种，影响插件名称、提示信息等，但不影响AI的回复。为空时使用en-US，如果传了chatLanguage会被chatLanguage覆盖 |

> \*\*问答code如何获得？\*\*请见下图：
> 
> ![img](https://docs.serviceme.com/assets/images/%E4%B8%93%E5%AE%B6code%E8%8E%B7%E5%8F%96-7fd11bd05d78c8dbee9fc0dc8354e4dc.png)

*   **请求示例：**

```
curl --location 'https://localhost/vee/openapi/chat/expert' \--header 'Authorization: openapi {access_token}' \--header 'Content-Type: application/json' \--data '{    "expertCode": "CHATES",    "content": "加班申请",    "sessionId": null,    "stream": false,    "includeThought": true,    "language": { "chatLanguage" : null, "systemLanguage" :  "zh-CN"}}'
```

*   **响应body：**

| 参数 | 参数二级 | 参数三级 | 参数四级 | 类型 | 参数解释 |
| --- | --- | --- | --- | --- | --- |
| data |  |  |  | object | 响应数据 |
|  | chatRecordId |  |  | string | 会话记录id |
|  | sessionId |  |  | string | 会话id |
|  | content |  |  | string | 文本类型的回答信息 |
|  | medias |  |  | object | 媒体类型的回答信息数组（图片和文件等） |
|  |  | type |  | string | image：图片；file：文件 |
|  |  | name |  | string | 名称 |
|  | suggestionQuestions |  |  | array string | 建议问题 |
|  | thoughts |  |  | array | 想法 |
|  |  | thought |  | string | 想法内容 |
|  |  | pluginName |  | string | 插件名称 |
|  |  | elapsedTime |  | object | 插件耗时信息 |
|  |  |  | model | float | 模型耗时 |
|  |  |  | action | float | 动作耗时 |
|  |  |  | total | float | 总耗时 |
|  |  | state |  | string | 状态（success：成功） |
|  | finish\_reason |  |  | string | 是否结束回答，当值为stop时表示结束，回答过程中值为null |
| success |  |  |  | boolean | 是否成功 |
| msg |  |  |  | string | 当success为false时，该处有值，会有部分错误提示 |

*   **非流式响应示例：**

```
{    "data": {        "chatRecordId": "4299234148041625600",        "sessionId": "4292755814873047040",        "content": "团队负责人发布工作任务，明确完成节点和验收标准等，员工与上级达成一致后方可加班。加班完毕后由员工在工时系统填写加班工时，在系统提交加班流程，备注内容需清楚列明加班任务，在工作地记录完整的上下班打卡记录，团队负责人/上级验收加班成果后，批准加班申请流程。HR确认打卡记录后，核算调休假额度。",        "medias": [			{        		"type": "image",                "name": null,                "url":"http://localhost:3978/openapi/chat/media/image/FE680A9CCFB1B56E80737FB28562DC33F4A37DEF52A65F046464788B83E0BE77"            },            {        		"type": "file",                "name": "答案参考文件.pdf",                "url":"https://localhost/#/share/preview?fileId=4268457334348447744&objectType=2&previewType=file&mode=login"            },        ],        "suggestionQuestions": [],        "thoughts": [            {                "thought": "为了回答这个问题，我需要查询知识库中的相关信息。",                "pluginName": "Search Knowledgebase",                "elapsedTime": {                    "model": 3612.4722,                    "action": 689.5891,                    "total": 4302.0613                },                "state": "success"            }        ],        "finish_reason": "stop"    },    "success": true,    "msg": ""}
```

*   **流式响应示例：**

```
data: {"data":{"chatRecordId":"4299228743576059904","sessionId":"4292755079242457089","content":"","medias":[],"suggestionQuestions":[],"thoughts":[{"thought":"为了回答这个问题，我需要查询知识库中的相关信息。","pluginName":"Search Knowledgebase","elapsedTime":{"model": 3612.4722,"action": 689.5891,"total": 4302.0613},"state": "success"}],"finish_reason":null},"success":true,"msg":""}data: {"data":{"chatRecordId":"4299228743576059904","sessionId":"4292755079242457089","content":"团队负责人发布工作任务，明确完成节点和验收标准等，员工与上级达成一致后方可加班。加班完毕后由员工在工时系统填写加班工时，在系统提交加班流程，备注内容需清楚列明加班任务，在工作地记录完整的上下班打卡记录，团队负责人/上级验收加班成果后，批准加班申请流程。HR确认打卡记录后，核算调休假额度。","medias":[],"suggestionQuestions":[],"thoughts":[],"finish_reason":null},"success":true,"msg":""}data: {"data":{"chatRecordId":"4299228743576059904","sessionId":"4292755079242457089","content":"","medias":[{"type":"image","name":null,"url":"http://localhost:3978/openapi/chat/media/image/FE680A9CCFB1B56E80737FB28562DC33F4A37DEF52A65F046464788B83E0BE77"}],"suggestionQuestions":[],"thoughts":[],"finish_reason":null},"success":true,"msg":""}data: {"data":{"chatRecordId":"4299228743576059904","sessionId":"4292755079242457089","content":"","medias":[{"type":"file","name":"答案参考文件.pdf","url":"https://localhost/#/share/preview?fileId=4268457334348447744&objectType=2&previewType=file&mode=login"}],"suggestionQuestions":[],"thoughts":[],"finish_reason":"stop"},"success":true,"msg":""}
```

### 获取对话的参考资料[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%8E%B7%E5%8F%96%E5%AF%B9%E8%AF%9D%E7%9A%84%E5%8F%82%E8%80%83%E8%B5%84%E6%96%99 "获取对话的参考资料的直接链接")

*   **接口地址：**`/openapi/chat/record/{chatRecordId}/reference`
    
*   **请求方式：**`get`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **请求url传参：**

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| chatRecordId | 是 | string | 从问答接口返回的chatRecordId字段里取值 |

*   **请求示例：**

```
curl --location 'http://localhost/openapi/chat/record/4299234148041625600/reference' \--header 'Authorization: openapi {access_token}'
```

*   **响应body：**

| 参数名称 | 参数二级 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| data |  | object array | 响应数据 |
|  | title | string | 标题 |
|  | content | string | 该会话记录引用的片段内容 |
|  | score | float | 相关程度（0到1，越接近1表示越相关） |
|  | url | string | 链接（暂时只有文件类型的引用有链接） |
|  | type | string | 类型枚举：document(文档)、image(图片)、QnA、other |
| success |  | boolean | 是否成功 |
| msg |  | string | 当success为false时，该处有值，会有部分错误提示 |

*   **响应示例：**

```
{    "data": [        {            "title": "公司行政制度.pdf",            "content": "片段一 ......",            "score": 0.95,            "url": "https://localhost/#/share/preview?fileId=4268457334348447744&objectType=2&previewType=file&mode=login",            "type": "document"        },        {            "title": "公司行政制度.pdf",            "content": "片段二 ......",            "score": 0.81,            "url": "https://localhost/#/share/preview?fileId=4268457334348447744&objectType=2&previewType=file&mode=login",            "type": "document"        },        {            "title": "公司行政制度.pdf",            "content": "片段三 ......",            "score": 0.76,            "url": "https://localhost/#/share/preview?fileId=4268457334348447744&objectType=2&previewType=file&mode=login",            "type": "document"        }    ],    "success": true,    "msg": ""}
```

## Bot接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#bot%E6%8E%A5%E5%8F%A3 "Bot接口的直接链接")

### 创建 Bot接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%88%9B%E5%BB%BA-bot%E6%8E%A5%E5%8F%A3 "创建 Bot接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF "基本信息的直接链接")

*   请求方式：POST
*   接口地址：`/openapi`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0 "请求参数的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String | Bot编码，唯一，最大长度 50 |
| cover | String | 封面图片路径（可选） |
| names | Array(TranslationInfo) | 名称多语言，必填；每个元素包含：`languageCode`、`content` |
| welcomes | Array(TranslationInfo) | 欢迎语多语言；每个元素包含：`languageCode`、`content`（长度受系统限制） |
| descriptions | Array(TranslationInfo) | 描述多语言；元素同上 |
| historyRecordNumber | Number | 历史消息条数上限 |
| feedback | Boolean | 是否开启反馈 |
| recoreChat | Boolean | 是否记录对话 |
| useSuggestedQuestions | Boolean | 是否启用推荐问题 |
| useKnowledgeBase | Boolean | 是否启用知识库 |
| sort | Number | 排序序号 |
| chatModelId | Number(Int64) | 对话模型 ID |
| chatPrompt | String | 对话系统提示词 |
| temperature | Number | 温度系数（0~2） |
| topP | Number | TopP（0~1） |
| tools | Array(BotPluginToolVO) | 机器人工具列表（每项至少包含 `id`\=插件ID） |
| knowledgeInfo | Object(BotKnowledgeVO) | 知识库配置，如 `workspaces`: Array(Int64) 工作区 ID 列表 |
| dataSources | Array(String) | 数据源标识集合 |

请求参数示例（Body）：

```
{  "code": "qa-bot",  "cover": "/images/bots/qa.png",  "names": [    { "languageCode": "zh-CN", "content": "问答机器人" },    { "languageCode": "en-US", "content": "Q&A Bot" }  ],  "welcomes": [    { "languageCode": "zh-CN", "content": "您好！我可以帮您解答问题。" },    { "languageCode": "en-US", "content": "Hi! I can help answer your questions." }  ],  "descriptions": [    { "languageCode": "zh-CN", "content": "用于通用问答的机器人" },    { "languageCode": "en-US", "content": "A bot for general Q&A" }  ],  "historyRecordNumber": 10,  "feedback": true,  "recoreChat": true,  "useSuggestedQuestions": false,  "useKnowledgeBase": true,  "sort": 1,  "chatModelId": 4493000000000000001,  "chatPrompt": "你是一个专业助手，请用简体中文回答用户问题。",  "temperature": 0.7,  "topP": 0.95,  "tools": [    { "id": 4488000000000001001 },    { "id": 4488000000000001002 }  ],  "knowledgeInfo": {    "workspaces": [4493061452348784640, 4493061452348784641]  },  "dataSources": ["kb", "faq"]}
```

cURL 示例：

```
curl -X POST "https://<host>/openapi" ^  -H "Content-Type: application/json" ^  -H "Authorization: Bearer <token>" ^  -d "{ \"code\": \"qa-bot\", \"names\": [ { \"languageCode\": \"zh-CN\", \"content\": \"问答机器人\" } ], \"welcomes\": [ { \"languageCode\": \"zh-CN\", \"content\": \"您好！\" } ], \"descriptions\": [ { \"languageCode\": \"zh-CN\", \"content\": \"用于通用问答的机器人\" } ], \"historyRecordNumber\": 10, \"feedback\": true, \"recoreChat\": true, \"useSuggestedQuestions\": false, \"useKnowledgeBase\": true, \"sort\": 1, \"chatModelId\": 4493000000000000001, \"chatPrompt\": \"你是一个专业助手。\", \"temperature\": 0.7, \"topP\": 0.95, \"tools\": [ { \"id\": 4488000000000001001 } ], \"knowledgeInfo\": { \"workspaces\": [4493061452348784640] }, \"dataSources\": [\"kb\"] }"
```

注：

*   `code` 必须全局唯一；重复将返回错误。

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| data | String | 新建机器人 ID |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息 |

返回示例：

```
{ "data": "4493061452348784640", "success": true, "msg": "" }## 文件空间### 单文件上传- **接口地址：**```v1/openapi/workspace/file/upload```- **请求方式：**```post```- **请求header：**| 参数名称      | 必填 | 类型   | 参数解释                                                       || ------------- | ---- | ------ | -------------------------------------------------------------- || Authorization | 是   | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |- **Content Type：**```form-data```- **请求body：**| 参数名称       | 必填 | 类型   | 参数解释                                 || -------------- | ---- | ------ | ---------------------------------------- || workspace      | 是   | string | 文件空间                                 || file           | 是   | file   | 文件（单个）                             || eponymousCover | 否   | bool   | 如果存在同名文件是否要覆盖（默认不覆盖） |- **请求示例：**```shellcurl --location 'http://localhost/v1/openapi/workspace/file/upload' \--header 'Authorization: openapi {access_token}' \--form 'workspace="测试空间"' \--form 'file=@"/C:/test.doc"' \--form 'eponymousCover="false"'
```

*   **响应body：**

| 参数名称 | 参数二级 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| data |  | object | 响应数据 |
|  | fileId | string | 文件id |
|  | fileName | string | 文件名称 |
|  | uploader | string | 上传人 |
| success |  | boolean | 是否成功 |
| msg |  | string | 当success为false时，该处有值，会有部分错误提示 |

*   **响应示例：**

```
{    "data": {        "fileId": "4345229404125790208",        "fileName": "test.doc",        "uploader": "test@serviceme.com"    },    "success": true,    "msg": ""}
```

## 文件空间[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4 "文件空间的直接链接")

### 多文件上传[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%A4%9A%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0 "多文件上传的直接链接")

#### 提交文件[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%8F%90%E4%BA%A4%E6%96%87%E4%BB%B6 "提交文件的直接链接")

*   **接口地址：**`v1/openapi/workspace/file/upload/batchSubmit`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`form-data`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| workspace | 是 | string | 文件空间 |
| files | 是 | file | 文件（多个） |
| eponymousCover | 否 | bool | 如果存在同名文件是否要覆盖（默认不覆盖） |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/workspace/file/upload/batchSubmit' \--header 'Authorization: openapi {access_token}' \--form 'workspace="测试空间"' \--form 'files=@"/C:/test1.doc"' \--form 'files=@"/C:/test2.docx"' \--form 'eponymousCover="false"'
```

*   **响应body：**

| 参数名称 | 参数二级 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| data |  | object | 响应数据 |
|  | stateId | string | 上传的状态id，可以使用这个状态id不断轮询获得最新的上传结果 |
| success |  | boolean | 是否成功 |
| msg |  | string | 当success为false时，该处有值，会有部分错误提示 |

*   **响应示例：**

```
{    "data": {        "stateId": "4345229404125790208"    },    "success": true,    "msg": ""}
```

#### 查询上传结果[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%9F%A5%E8%AF%A2%E4%B8%8A%E4%BC%A0%E7%BB%93%E6%9E%9C "查询上传结果的直接链接")

*   **接口地址：**`v1/openapi/workspace/file/upload/batchSubmit/{stateId}`
    
*   **请求方式：**`get`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **请求url传参：**

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| stateId | 是 | string | 多文件提交上传接口返回给你的那个stateId字段值 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/workspace/file/upload/batchSubmit/4345227891722682368' \--header 'Authorization: openapi {access_token}'
```

*   **响应body：**

| 参数名称 | 参数二级 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| data |  | object array | 响应数据 |
|  | fileId | string | 文件Id |
|  | fileName | string | 文件名 |
|  | state | string | 状态枚举：underway（排队处理中）、success（成功）、fail（失败） |
|  | uploader | string | 上传人 |
|  | errorMsg | string | 当状态为 fail 时，这里会存放导致失败的原因 |
|  | finishTime | string | 文件处理完成的时间 |
| success |  | boolean | 是否成功 |
| msg |  | string | 当success为false时，该处有值，会有部分错误提示 |

*   **响应示例：**

```
{    "data": [        {            "fileId": "4345227925730099200",            "fileName": "test1.doc",            "state": "success",            "uploader": "test@serviceme.com",            "errorMsg": "",            "finishTime": "2024-08-17T05:04:30.0128596Z"        },        {            "fileId": "4345227924266287104",            "fileName": "test2.docx",            "state": "success",            "uploader": "test@serviceme.com",            "errorMsg": "",            "finishTime": "2024-08-17T05:04:29.7952274Z"        }    ],    "success": true,    "msg": ""}
```

### QnA 创建[​](https://docs.serviceme.com/docs/technical-guide/open-api#qna-%E5%88%9B%E5%BB%BA "QnA 创建的直接链接")

*   **接口地址：**`v1/openapi/workspace/qna/create`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **请求body：**

| 参数名称 | 参数二级 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- | --- |
| workspace |  | 是 | string | 文件空间 |
| questions |  | 是 | string array | 问题数组，可多个 |
| answer |  | 是 | string | 答案 |
| metadatas |  | 否 | object array | 元数据 |
|  | typeCode | 是 | string | 元数据类型 |
|  | content | 是 | string | 内容 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/workspace/qna/create' \--header 'Content-Type: application/json' \--header 'Authorization: openapi {access_token}' \--data '{    "questions": [        "测试问题"    ],    "answer": "测试答案",    "workspace": "测试空间",    "metadatas": [        {            "typeCode": "Document type",            "content": "测试元数据"        }    ]}'
```

*   **响应body：**

| 参数名称 | 类型 | 参数解释 |
| --- | --- | --- |
| success | boolean | 是否成功 |
| msg | string | 当success为false时，该处有值，会有部分错误提示 |

*   **响应示例：**

```
{    "success": true,    "msg": ""}
```

### 查询文件[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%9F%A5%E8%AF%A2%E6%96%87%E4%BB%B6 "查询文件的直接链接")

*   **接口地址：**`v1/openapi/workspace/file`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **请求body：**

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| workspace | 是 | string | 文件空间 |
| pageIndex | 否 | number | 页码，默认第一页 |
| pageSize | 否 | number | 获取数量，默认10条 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/workspace/file' \--header 'Content-Type: application/json' \--header 'Authorization: ••••••' \--data '{    "workspace": "测试空间",    "pageIndex": 1,    "pageSize": 10}'
```

*   **响应body：**
    
    | 参数名称 | 参数二级 | 参数三级 | 类型 | 参数解释 |
    | --- | --- | --- | --- | --- |
    | data |  |  | object array | 响应数据 |
    |  | id |  | string | 文件id |
    |  | name |  | string | 文件名 |
    |  | size |  | number | 文件大小，单位字节 |
    |  | description |  | string | 描述 |
    |  | fullPath |  | string | 文件路径 |
    |  | tags |  | object array | 文件标签信息 |
    |  |  | id | string | 标签id |
    |  |  | value | string | 标签内容 |
    |  | chunkingState |  | string | 文件索引状态：waiting(等候处理中)、success(成功)、fail(失败)、underway(进行中) |
    |  | previewState |  | string | 文件预览状态：waiting(等候处理中)、success(成功)、fail(失败)、underway(进行中) |
    |  | fileCanPreview |  | boolean | 文件是否可预览，true：可以；false：不可以 |
    |  | previewUrl |  | string | 文件预览地址 |
    |  | createdByRealName |  | string | 文件创建者名称 |
    |  | createdByAccount |  | string | 文件创建者账号 |
    |  | created |  | datetime | 文件创建时间 |
    |  | modifiedByRealName |  | string | 文件编辑者名称 |
    |  | modifiedByAccount |  | string | 文件编辑者账号 |
    |  | modified |  | datetime | 文件编辑时间 |
    | success |  |  | boolean | 是否成功 |
    | msg |  |  | string | 当success为false时，该处有值，会有部分错误提示 |
    
*   **响应示例：**
    

```
{    "data": [        {            "id": "4339013367831199744",            "name": "test.docx",            "size": 15113,            "description": null,            "fullPath": "/",            "tags": [],            "chunkingState": "success",            "previewState": "success",            "fileCanPreview": true,            "previewUrl": "http://localhost.com/#/share/preview?fileId=4339013367831199744&objectType=2&previewType=file&mode=login",            "createdByRealName": "test",            "createdByAccount": "test",            "created": "2024-07-31T01:30:02.88",            "modifiedByRealName": "test",            "modifiedByAccount": "test",            "modified": "2024-07-31T01:30:02.88"        }    ],    "pageSize": 10,    "pageIndex": 1,    "totalCount": 1,    "success": true,    "msg": ""}
```

### 查询文件片段[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%9F%A5%E8%AF%A2%E6%96%87%E4%BB%B6%E7%89%87%E6%AE%B5 "查询文件片段的直接链接")

*   **接口地址：**`v1/openapi/workspace/file/chunk`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **请求body：**

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| fileId | 是 | string | 文件id |
| imageFormat | 否 | string | 图片格式，markdown或html，默认使用markdown输出 |
| pageIndex | 否 | number | 页码，默认第一页 |
| pageSize | 否 | number | 获取数量，默认10条 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/workspace/file/chunk' \--header 'Content-Type: application/json' \--header 'Authorization: ••••••' \--data '{    "fileId": "4344174161665458176",    "imageFormat": "html",    "pageIndex": 1,    "pageSize": 10}'
```

*   **响应body：**
    
    | 参数名称 | 参数二级 | 参数三级 | 类型 | 参数解释 |
    | --- | --- | --- | --- | --- |
    | data |  |  | object array | 响应数据 |
    |  | id |  | string | 片段id |
    |  | content |  | string | 片段内容 |
    | success |  |  | boolean | 是否成功 |
    | msg |  |  | string | 当success为false时，该处有值，会有部分错误提示 |
    
*   **响应示例：**
    

```
{    "data": [        {            "id": "4339013367831199744",            "content": "test"        }    ],    "pageSize": 10,    "pageIndex": 1,    "totalCount": 1,    "success": true,    "msg": ""}
```

### 下载文件为 Markdown 文件接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E4%B8%8B%E8%BD%BD%E6%96%87%E4%BB%B6%E4%B8%BA-markdown-%E6%96%87%E4%BB%B6%E6%8E%A5%E5%8F%A3 "下载文件为 Markdown 文件接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-1 "基本信息的直接链接")

*   请求方式：POST
*   接口地址：`/v1/openapi/workspace/file/downloadDocument2MD`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-1 "请求参数的直接链接")

| 参数名 | 类型 | 位置 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| id | Number(Int64) | Body | 是 | 需要转换为 Markdown 的文件 ID |

请求体示例（JSON）：

```
{  "id": 4493061452348784640}
```

cURL 示例：

```
curl -X POST "https://<host>/v1/openapi/DownloadDocument2MD" ^  -H "Authorization: <token>" ^  -H "Content-Type: application/json" ^  --data-raw "{\"id\":4493061452348784640}"
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-1 "返回值的直接链接")

*   类型：文件流（FileContentResult），作为附件下载
*   文件名：原文件名去掉扩展名后改为 `.md`
*   Content-Type：`application/octet-stream`

返回示例（HTTP 响应头关键字段）：

```
HTTP/1.1 200 OKContent-Type: application/octet-streamContent-Disposition: attachment; filename="示例文档.md"
```

### RAG[​](https://docs.serviceme.com/docs/technical-guide/open-api#rag "RAG的直接链接")

*   **接口地址：**`/v1/openapi/rag`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **请求body：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `query` | `string` | 否 | 无 | 需要检索的问题或内容。和Keywords参数不能都为`null`。 |
| `keywords` | `string` | 否 | 无 | 关键词，多个关键词用 `|` 分隔。和Query参数不能都为`null`。为`null`时会根据需要提取关键字，不为空时直接使用传入的关键字。 |
| `workspaces` | `array` | 否 | 无 | 本次 RAG 将要检索的文件空间名称或Id。如果传了这个值，则会只从这几个空间里检索。 |
| `ragObject` | `RagObject` | 是 | `0` | RAG 对象类型，枚举值（详见 **RagObject 枚举**）。 目前尚不支持QNA查询 |
| `topk` | `number` | 是 | 无 | 返回结果的数量。 |
| `minSimilarity` | `double` | 否 | `0.8` | 最低相似度，范围为 `[0, 1]`。 |
| `metadataProvider` | `array` | 否 | 无 | 要使用的元数据。 目前只支持传\["default"\] |
| `metadataSearchType` | `number` | 否 | `0` | 搜索时使用元数据的方式，必须先启用metadataProvider才生效。0： 过滤模式，1：权重排序模式 |
| `ragMode` | `SearchMode` | 是 | `0` | RAG 模式，枚举值（详见 **SearchMode 枚举**）。 |
| `weights` | `object` | 否 | 无 | 各路索引的RRF权重，仅在 `RagMode` 为 `Hybrid` 时有效。若为 `null` 则使用默认权重。 |
| `reranker` | `string` | 否 | 无 | 如果为 `null` 则不使用 `reranker`。 |

* * *

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/rag' \--header 'Authorization: ••••••' \--header 'Content-Type: application/json' \--data '{      "query": "什么是人工智能？",      "keywords": "AI|机器学习",      "workspaces": ["workspace1", "workspace2"],      "ragObject": 0,      "topk": 3,      "minSimilarity": 0.8,      "metadataProvider": ["default"],      "metadataSearchType": 1,    "ragMode": 1,      "weights": {          "Embedding": 0.9,          "FullText": 0.8      },      "reranker": "default"  }  '
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `object` | 响应数据对象，包含搜索结果和搜索 ID 等信息。 |
| `data.results` | `array` | 搜索结果列表，每个元素是一个包含片段信息的对象。 |
| `data.results[].chunkId` | `string` | 片段 ID |
| `data.results[].fileId` | `string` | 片段所属的文件 ID |
| `data.results[].fileName` | `string` | 片段所属的文件名 |
| `data.results[].content` | `string` | 片段内容 |
| `data.results[].metadata` | `json` | 片段元数据 |
| `data.results[].url` | `string` | 片段的 URL 地址（如果有） |
| `data.results[].searchScore` | `double` | 近似度得分 |
| `data.results[].rrfScore` | `double` | RRF 得分 |
| `data.results[].rerankScore` | `double` | 重排得分 |
| `data.results[].workspaceId` | `string` | 文件所属的文件空间 ID |
| `data.results[].workspaceName` | `string` | 文件所属的文件空间名称 |
| `data.searchId` | `string` | 本次搜索操作的唯一标识 |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

* * *

*   **响应示例：**

```
{    "data": {        "results": [            {                "chunkId": "4422442085118906369",                "fileId": "4417076017114382336",                "fileName": "文件1.pdf",                "content": "……",                "metadata": {                    "Url": "https://……",                    "FileName": "文件1.pdf",                    "WorkspaceName": "workspace1",                    "FileId": "4417076017114382336",                    "FilePath": "/",                    "Created": "2025-03-03T11:23:08.803",                    "Size": "1160594"                },                "url": "https://……",                "searchScore": 0.153852914388501,                "rrfScore": 0.8768274796195331,                "rerankScore": 0.0,                "workspaceId": "4417069258022846464",                "workspaceName": ""            },            {                "chunkId": "4422442085114712073",                "fileId": "4417076017114382336",                "fileName": "文件1.pdf",                "content": "……",                "metadata": {                    "Url": "https://……",                    "FileName": "文件1.pdf",                    "WorkspaceName": "workspace1",                    "FileId": "4417076017114382336",                    "FilePath": "/",                    "Created": "2025-03-03T11:23:08.803",                    "Size": "1160594"                },                "url": "https://……",                "searchScore": 0.152822583517241,                "rrfScore": 0.8670604574184315,                "rerankScore": 0.0,                "workspaceId": "4417069258022846464",                "workspaceName": ""            },            {                "chunkId": "4422442085114712071",                "fileId": "4417076017114382336",                "fileName": "文件1.pdf",                "content": "……",                "metadata": {                    "Url": "……",                    "FileName": "文件1.pdf",                    "WorkspaceName": "workspace1",                    "FileId": "4417076017114382336",                    "FilePath": "/",                    "Created": "2025-03-03T11:23:08.803",                    "Size": "1160594"                },                "url": "……",                "searchScore": 0.153708375384407,                "rrfScore": 0.8661891817471927,                "rerankScore": 0.0,                "workspaceId": "4417069258022846464",                "workspaceName": ""            }        ],        "searchId": "4423568945336811520"    },    "success": true,    "msg": ""}
```

*   **枚举类型**

**RagObject 枚举（目前不支持QA，即使选了也搜不出来）**

| 枚举值 | 枚举数字 | 说明 |
| --- | --- | --- |
| `Both` | 0 | 同时检索 Q&A 和文档内容。 |
| `Qna` | 1 | 仅检索 Q&A 内容。 |
| `Doc` | 2 | 仅检索文档内容。 |

**SearchMode 枚举**

| 枚举值 | 枚举数字 | 说明 |
| --- | --- | --- |
| `Hybrid` | 1 | 混合检索模式，结合嵌入向量和全文检索。 |
| `Embedding` | 2 | 仅基于嵌入向量的检索模式。 |
| `FullText` | 3 | 仅基于全文检索的检索模式。 |

* * *

*   **Rerank模型配置方式** 以cohere-rerank-v3.5模型的配置方式为例：

```
INSERT INTO dbo.AI_LLM (Id,ModelName,TokenCount,Config,Enable,[Default],Display,DisplayName) VALUES(4183721090264072898,N'rerank-v3.5',255454,N'{"RerankerName":"cohere","Uri":"https://域名/v2/rerank","Token":"bearer token"}',1,0,0,N'cohere-rerank-v3.5');
```

注意：如果使用的是Cohere官网的API，Token字段的值为bearer token，如果使用的是Azure AI Foundry的API，Token字段的值要去掉bearer。

### 文件空间列表接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4%E5%88%97%E8%A1%A8%E6%8E%A5%E5%8F%A3 "文件空间列表接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-2 "基本信息的直接链接")

*   **请求方式**：GET
*   **接口地址**：`/v1/openapi/workspace/all`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-2 "请求参数的直接链接")

无

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-2 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| data | Array | 分类列表；每项包含分类信息及其下的文件空间列表 |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

##### data 数组项结构：分类（WorkspaceCategory）[​](https://docs.serviceme.com/docs/technical-guide/open-api#data-%E6%95%B0%E7%BB%84%E9%A1%B9%E7%BB%93%E6%9E%84%E5%88%86%E7%B1%BBworkspacecategory "data 数组项结构：分类（WorkspaceCategory）的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| id | Number | 分类 Id |
| name | String | 分类名称 |
| icon | String | 图标 |
| workspaces | Array | 该分类下的文件空间列表（见下表） |

##### data\[n\].workspaces 数组项结构：文件空间（WorkspaceInfo）[​](https://docs.serviceme.com/docs/technical-guide/open-api#datanworkspaces-%E6%95%B0%E7%BB%84%E9%A1%B9%E7%BB%93%E6%9E%84%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4workspaceinfo "data[n].workspaces 数组项结构：文件空间（WorkspaceInfo）的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| id | String | 空间 Id |
| name | String | 空间名称 |
| description | String | 空间描述 |
| operationKeys | Array(String) | 操作权限列表 |
| fileCount | Number | 文件数量（统计值） |

返回值示例：

```
{  "data": [    {      "id": 4493041505002323001,      "name": "视频资料",      "icon": "icon-video",      "workspaces": [        {          "id": "4493061452348784640",          "name": "宣传片素材",          "description": "用于存放宣传片视频素材",          "operationKeys": ["read", "write"],          "fileCount": 128        },        {          "id": "4493061452348784641",          "name": "会议录制",          "description": "内部会议录制文件",          "operationKeys": ["read"],          "fileCount": 57        }      ]    },    {      "id": 4493041505002323002,      "name": "文档资料",      "icon": "icon-doc",      "workspaces": [        {          "id": "4493061452348784700",          "name": "产品手册",          "description": "对外发布的产品说明文档",          "operationKeys": [],          "fileCount": 342        }      ]    }  ],  "success": true,  "msg": ""}
```

### 文件空间新增接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4%E6%96%B0%E5%A2%9E%E6%8E%A5%E5%8F%A3 "文件空间新增接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-3 "基本信息的直接链接")

*   **请求方式**：POST
*   **接口地址**：`/v1/openapi/workspace/create`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-3 "请求参数的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| name | String | 空间名称（示例："测试空间"） |
| workspaceTypeId | String | 文件空间类型 ID（示例："4493041505002323969"） |
| classificationId | String | 分类 ID（示例："4035265396658405376"） |
| description | String | 空间描述（示例："测试空间"） |
| quota | Number | 配额（示例：1） |
| fileSize | Number | 文件大小限制（示例：1） |
| fileTypes | Array | 支持的文件类型列表（示例：\[".mov", ".mp4", ".mpeg"\]） |
| enable | Boolean | 是否启用（true = 启用，false = 禁用） |
| operationKeys | Array | 操作权限列表（示例：空数组） |
| notice | String | 空间通知（示例："测试空间"） |
| settings | String | 空间配置（JSON 字符串格式，包含模式、文件大小、支持类型等） |

注：

1.  settings字段说明请看下方的 【文件预处理与配置参数说明】
2.  metadataTemplate字段说明请看下方的 【元数据参数说明】

请求参数示例：

```
{   "name": "测试空间",   "workspaceTypeId": "4493041505002323969",   "classificationId": "4035265396658405376",   "description": "测试空间",   "quota": 1,   "fileSize": 1,   "fileTypes": \[".mov", ".mp4", ".mpeg"],   "enable": true,   "operationKeys": \[],   "notice": "测试空间",   "settings": "{\\"setting\\":{\\"mode\\":\\"default\\",\\"identifier\\":\\"\\",\\"maxLength\\":1024,\\"overlap\\":0},\\"status\\":null,\\"fileSize\\":1,\\"fileTypes\\":\[\\".mov\\",\\".mp4\\",\\".mpeg\\"]}"}
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-3 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| data | String | 新增文件空间的 ID（示例："4493061452348784640"） |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

返回值示例：

```
{   "data": "4493061452348784640",   "success": true,   "msg": ""}
```

### 文件空间编辑接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4%E7%BC%96%E8%BE%91%E6%8E%A5%E5%8F%A3 "文件空间编辑接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-4 "基本信息的直接链接")

*   **请求方式**：POST
*   **接口地址**：`/v1/openapi/workspace/update`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-4 "请求参数的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| id | String | 待编辑文件空间的 ID（示例："4437336392049102848"） |
| workspaceTypeId | String | 文件空间类型 ID（示例："4437336252408139777"） |
| workspaceTypeName | String | 文件空间类型名称（示例："测试空间"） |
| name | String | 空间名称（示例："测试空间"） |
| enable | Boolean | 是否启用（true = 启用，false = 禁用） |
| notice | String | 空间通知（示例："终版测试"） |
| description | String | 空间描述（示例："终版测试"） |
| classificationId | String | 分类 ID（示例："4035265396658405376"） |
| quota | Number/Null | 配额（可为 null，表示不修改） |
| quotaUsage | Number | 配额已使用量（示例：50815916） |
| settings | String | 空间配置（JSON 字符串格式，包含模式、OCR、摘要等高级配置） |
| metadataTemplate | String | 元数据模板（JSON 数组字符串，示例："\\\[{"name":" 测试 ","type":0}\]"） |
| 注： |  |  |

1.  settings字段说明请看下方的 【文件预处理与配置参数说明】
2.  metadataTemplate字段说明请看下方的 【元数据参数说明】

请求参数示例：

```
{   "id": "4437336392049102848",   "workspaceTypeId": "4437336252408139777",   "workspaceTypeName": "测试空间",   "name": "测试空间",   "enable": true,   "notice": "终版测试",   "description": "终版测试",   "classificationId": "4035265396658405376",   "quota": null,   "quotaUsage": 50815916,   "settings": "{\\"setting\\":{\\"mode\\":\\"refine\\",\\"identifier\\":\\"\\",\\"maxLength\\":1024,\\"overlap\\":0,\\"previewEnable\\":true,\\"enable\\":true,\\"documentOCR\\":false,\\"summaryEnable\\":true,\\"imageRecognize\\":false,\\"ocrMode\\":\\"layout\\",\\"summaryPrompt\\":\\"### Summarize the following in the original language in no more than 200 words.\\"},\\"status\\":null,\\"fileSize\\":null,\\"fileTypes\\":\[\\".md\\"],\\"useWorkspaceSetting\\":true}",   "metadataTemplate": "\[{\\"name\\":\\"测试\\",\\"type\\":0}]"}
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-4 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

返回值示例：

```
{   "success": true,   "msg": ""}
```

### 文件空间删除接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4%E5%88%A0%E9%99%A4%E6%8E%A5%E5%8F%A3 "文件空间删除接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-5 "基本信息的直接链接")

*   **请求方式**：DELETE
*   **接口地址**：`/v1/openapi/workspace/delete`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-5 "请求参数的直接链接")

| 参数名 | 类型 | 位置 | 说明 |
| --- | --- | --- | --- |
| ids | Array(Number) | Query 或 Body | 需要删除的文件空间 ID 列表，支持批量 |
| 请求示例： |  |  |  |

```
[  4493061452348784640,  4493061452348784641]
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-5 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

返回值示例：

```
{  "success": true,  "msg": ""}
```

### 文件预处理与配置参数说明[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%96%87%E4%BB%B6%E9%A2%84%E5%A4%84%E7%90%86%E4%B8%8E%E9%85%8D%E7%BD%AE%E5%8F%82%E6%95%B0%E8%AF%B4%E6%98%8E "文件预处理与配置参数说明的直接链接")

该 JSON 结构用于定义文件在空间中的预处理规则、分段模式及功能开关配置，通常作为`settings`字段的核心内容（对应文件空间新增 / 编辑接口中的`settings`参数），以下是各参数的详细说明：

#### 1\. 核心配置对象：`setting`[​](https://docs.serviceme.com/docs/technical-guide/open-api#1-%E6%A0%B8%E5%BF%83%E9%85%8D%E7%BD%AE%E5%AF%B9%E8%B1%A1setting "1-核心配置对象setting的直接链接")

| 参数名 | 类型 | 取值说明 | 备注 |
| --- | --- | --- | --- |
| `mode` | String | 可选值：- `default`：默认分段模式- `refine`：细分分段模式 | 用于控制文件内容的分段策略，细分模式会对内容进行更精细的拆分 |
| `maxLength` | Number | 数值型（示例：1024） | 仅在**自定义分段模型**下生效，定义每段内容的最大长度，默认值为 1024 |
| `overlap` | Number | 数值型（示例：0） | 分片内容的上下重合文本长度，用于避免分段导致的内容断裂，0 表示无重合 |
| `previewEnable` | Boolean | `true`（启用）/ `false`（禁用） | 控制是否开启文件预览功能，启用后用户可在不打开文件的情况下查看部分内容 |
| `enable` | Boolean | `true`（启用）/ `false`（禁用） | 总开关，控制是否启用文件预处理功能（预处理包含 OCR、摘要生成等后续所有子功能） |
| `documentOCR` | Boolean | `true`（开启）/ `false`（关闭） | 控制是否对文档进行 OCR 识别，适用于图片格式文档或包含图片的文档，开启后可提取图片中的文字内容 |
| `ocrMode` | String | 可选值：- `read`：读取模式（仅提取文字内容）- `layout`：布局模式（保留文字的排版结构，如段落、表格位置） | 仅在`documentOCR`为`true`时生效，定义 OCR 识别的精度和输出格式 |
| `summaryEnable` | Boolean | `true`（开启）/ `false`（关闭） | 控制是否自动生成文档摘要，开启后会根据`summaryPrompt`的规则生成摘要 |
| `imageRecognize` | Boolean | `true`（开启）/ `false`（关闭） | 控制是否识别文档中的图片元素，开启后可对图片内容进行基础分析（如图片类型、关键信息） |
| `summaryPrompt` | String | 文本字符串（示例：`"### Summarize the following in the original language in no more than 200 words."`） | 自定义全文摘要的生成规则，支持 markdown 格式，用于指导 AI 生成符合需求的摘要内容 |
| `formulas` | Boolean | `true`（开启）/ `false`（关闭） | 控制是否识别文档中的公式内容（如数学公式、化学方程式），开启后可提取并保留公式的原始格式 |
| `screenshots_by_page` | Boolean | `true`（开启）/ `false`（关闭） | 控制是否按文档页码生成截图，开启后会为每一页文档生成对应的图片截图，便于快速预览页面布局 |

#### 2\. 全局配置开关：`useWorkspaceSetting`[​](https://docs.serviceme.com/docs/technical-guide/open-api#2-%E5%85%A8%E5%B1%80%E9%85%8D%E7%BD%AE%E5%BC%80%E5%85%B3useworkspacesetting "2-全局配置开关useworkspacesetting的直接链接")

| 参数名 | 类型 | 取值说明 | 备注 |
| --- | --- | --- | --- |
| `useWorkspaceSetting` | Boolean | `true`（跟随）/ `false`（自定义） | 控制当前文件的配置是否跟随所属**文件空间（Workspace）** 的全局配置：- `true`：文件使用 Workspace 的默认配置，忽略当前`setting`中的自定义规则- `false`：文件使用当前`setting`中的自定义配置，覆盖 Workspace 的默认规则 |

#### 完整 JSON 示例[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%AE%8C%E6%95%B4-json-%E7%A4%BA%E4%BE%8B "完整 JSON 示例的直接链接")

```
{	"setting": {		"mode": "refine", // 分段模式， default：默认，refine：细分		"maxLength": 1024, // 分段自定义模型下填写，默认1024		"overlap": 0, // 分片上下重合文本长度		"previewEnable": true, // 启用文件预览		"enable": true, // 启用预处理		"documentOCR": true, // 开启ocr		"ocrMode": "layout", // ocr模式，read：读取，layout：布局		"summaryEnable": true, // 开启文档摘要生成		"imageRecognize": true, // 识别文档里面的图片		"summaryPrompt": "### Summarize the following in the original language in no more than 200 words.", // 自定义的全文摘要prompt		"formulas": false, // 公式识别		"screenshots_by_page": false // 按页截图	},	"useWorkspaceSetting": true // 文件的设置，是否跟随Workspace的设置}
```

### 元数据参数说明[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%85%83%E6%95%B0%E6%8D%AE%E5%8F%82%E6%95%B0%E8%AF%B4%E6%98%8E "元数据参数说明的直接链接")

元数据接受一个json字符串作为参数值

#### 1\. 核心配置对象：`setting`[​](https://docs.serviceme.com/docs/technical-guide/open-api#1-%E6%A0%B8%E5%BF%83%E9%85%8D%E7%BD%AE%E5%AF%B9%E8%B1%A1setting-1 "1-核心配置对象setting-1的直接链接")

| 参数名 | 类型 | 取值说明 | 备注 |
| --- | --- | --- | --- |
| `name` | String | 元数据名称 |  |
| `type` | Number | 0：文本类型；1：选项类型 |  |
| `limit` | String | 选项的每一项 |  |

#### 完整 JSON 示例[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%AE%8C%E6%95%B4-json-%E7%A4%BA%E4%BE%8B-1 "完整 JSON 示例的直接链接")

```
{	"metadataTemplate": "[{\"name\":\"测试\",\"type\":0},{\"name\":\"测试2\",\"type\":1,\"limit\":\"[\\\"选项1\\\",\\\"选项2\\\"]\"}]"}
```

### 物理删除文件接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E7%89%A9%E7%90%86%E5%88%A0%E9%99%A4%E6%96%87%E4%BB%B6%E6%8E%A5%E5%8F%A3 "物理删除文件接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-6 "基本信息的直接链接")

*   请求方式：DELETE
*   接口地址：`/v1/openapi/workspace/file/deleteFilePhysically`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-6 "请求参数的直接链接")

| 参数名 | 类型 | 位置 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| id | Number(Int64) | Query | 是 | 需要物理删除的文件 ID |

请求参数示例（Query）：

```
/v1/openapi/workspace/file/deleteFilePhysically?id=4493061452348784640
```

cURL 示例：

```
curl -X DELETE "https://<host>/v1/openapi/workspace/file/deleteFilePhysically?id=4493061452348784640" ^  -H "Authorization: Bearer <token>"
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-6 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

返回示例：

```
{  "success": true,  "msg": ""}
```

#### 行为说明[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%A1%8C%E4%B8%BA%E8%AF%B4%E6%98%8E "行为说明的直接链接")

*   物理删除为不可恢复操作，请谨慎调用。
*   当指定 ID 不存在或无权限时将返回失败。

### 编辑文件元数据接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E7%BC%96%E8%BE%91%E6%96%87%E4%BB%B6%E5%85%83%E6%95%B0%E6%8D%AE%E6%8E%A5%E5%8F%A3 "编辑文件元数据接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-7 "基本信息的直接链接")

*   请求方式：PUT
*   接口地址：`/v1/openapi/workspace/file/metadataExpansionEdit`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-7 "请求参数的直接链接")

| 参数名 | 类型 | 位置 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| id | Number(Int64) | Body | 是 | 需要编辑的文件 ID |
| metadataTemplate | String | Body | 否 | 扩展元数据的 JSON 字符串；为空或省略时将清空扩展元数据。推荐结构示例：`[{"name":"Document type","type":0,"value":"合同"}]` |

请求体示例（JSON）：

```
{  "id": 4493061452348784640,  "metadataTemplate": "[{\"name\":\"Document type\",\"type\":0,\"value\":\"合同\"},{\"name\":\"Department\",\"type\":0,\"value\":\"销售部\"}]"}
```

cURL 示例：

```
curl -X PUT "https://<host>/v1/openapi/workspace/file/metadataExpansionEdit" ^  -H "Authorization: Bearer <token>" ^  -H "Content-Type: application/json" ^  --data-raw "{\"id\":4493061452348784640,\"metadataTemplate\":\"[{\\\"name\\\":\\\"Document type\\\",\\\"type\\\":0,\\\"value\\\":\\\"合同\\\"},{\\\"name\\\":\\\"Department\\\",\\\"type\\\":0,\\\"value\\\":\\\"销售部\\\"}]\"}"
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-7 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

返回示例：

```
{  "success": true,  "msg": ""}
```

#### 行为说明[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%A1%8C%E4%B8%BA%E8%AF%B4%E6%98%8E-1 "行为说明的直接链接")

*   根据入参更新文件的扩展元数据（MetadataExpansion），并重建 doc\_metadata 索引，使变更在检索中生效。
*   当指定 ID 不存在或无权限时将返回失败。

### 文件列表接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8%E6%8E%A5%E5%8F%A3 "文件列表接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-8 "基本信息的直接链接")

*   请求方式：POST
*   接口地址：`/v1/openapi/workspace/file`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-8 "请求参数的直接链接")

| 参数名 | 类型 | 位置 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| workspace | String | Body | 是 | 文件空间名称 |
| pageIndex | Number(Int32) | Body | 否 | 页码，默认 `1` |
| pageSize | Number(Int32) | Body | 否 | 每页条数，默认 `10` |

请求体示例（JSON）：

```
{  "workspace": "公共资料库",  "pageIndex": 1,  "pageSize": 10}
```

cURL 示例：

```
curl -X POST "https://<host>/v1/openapi/workspace/file" ^  -H "Authorization: Bearer <token>" ^  -H "Content-Type: application/json" ^  --data-raw "{\"workspace\":\"公共资料库\",\"pageIndex\":1,\"pageSize\":10}"
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-8 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| pageIndex | Number | 当前页码 |
| pageSize | Number | 每页条数 |
| totalCount | Number | 总条数（可能返回 0 或 -1 表示未知/增量，客户端可按自身策略处理） |
| data | Array<File> | 文件数据列表，字段见下文“文件项字段说明” |

文件项字段说明（示例，实际字段可能因系统版本有所增减）：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| id | Number | 文件 ID |
| fileName | String | 文件名 |
| previewUrl | String | 文件预览地址（当系统配置了预览地址模板时返回） |
| fileCanPreview | Boolean | 是否可预览（由后端预览状态计算得到） |
| previewState | String | 预览状态：`waiting` / `underway` / `success` / `fail` |
| chunkingState | String | 切片处理状态：`waiting` / `underway` / `success` / `fail` |
| modified | String | 最近修改时间（ISO 格式，如 `2024-01-01T12:00:00Z`） |

返回示例：

```
{  "pageIndex": 1,  "pageSize": 10,  "totalCount": 125,  "data": [    {      "id": 4493061452348784640,      "fileName": "示例文档.docx",      "previewUrl": "https://<host>/preview/file/4493061452348784640",      "fileCanPreview": true,      "previewState": "success",      "chunkingState": "underway",      "modified": "2024-07-01T09:30:15Z"    }  ]}
```

#### 行为说明[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%A1%8C%E4%B8%BA%E8%AF%B4%E6%98%8E-2 "行为说明的直接链接")

*   仅返回“文件”（不含文件夹）。
*   默认按 `Modified` 字段倒序排序，支持分页查询。
*   仅查询指定 `workspace` 范围内的文件，调用者需具备该空间的访问权限；非管理员还需具备相应授权。
*   当系统配置了文件预览地址模板时将返回 `previewUrl`；否则该字段为空或省略。
*   `previewState` 与 `chunkingState` 的枚举取值分别为 `waiting` / `underway` / `success` / `fail`。
*   `pageIndex` / `pageSize` 未传时将采用默认值 `1` / `10`。

## 文件空间类型[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4%E7%B1%BB%E5%9E%8B "文件空间类型的直接链接")

### 新增文件空间类型接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%96%B0%E5%A2%9E%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4%E7%B1%BB%E5%9E%8B%E6%8E%A5%E5%8F%A3 "新增文件空间类型接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-9 "基本信息的直接链接")

*   请求方式：POST
*   接口地址：`/v1/openapi/workspaceType`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-9 "请求参数的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String | 文件空间类型编号 |
| title | Array | 多语言标题列表，每个元素包含以下字段：- `languageCode`：语言编码（如 ja-JP、zh-CN、en-US）- `content`：对应语言的标题内容 |
| icon | String | 图标路径（示例：`/icons/01842830fc1348edacf68edd2695614a.png`） |
| sort | Number | 排序序号（示例：1） |
| description | String | 类型描述 |

请求参数示例（Body）：

```
{  "code": "文件空间类型编号",  "title": [    { "languageCode": "zh-CN", "content": "多语言" },    { "languageCode": "en-US", "content": "测试新增" }  ],  "icon": "/icons/01842830fc1348edacf68edd2695614a.png",  "sort": 1,  "description": "描述"}
```

cURL 示例：

```
curl -X POST "https://<host>/v1/openapi/workspaceType" ^  -H "Content-Type: application/json" ^  -H "Authorization: Bearer <token>" ^  -d "{ \"code\": \"文件空间类型编号\", \"title\": [ { \"languageCode\": \"zh-CN\", \"content\": \"多语言\" } ], \"icon\": \"/icons/018...png\", \"sort\": 1, \"description\": \"描述\" }"
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-9 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

返回示例：

```
{ "success": true, "msg": "" }
```

### 编辑文件空间类型接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E7%BC%96%E8%BE%91%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4%E7%B1%BB%E5%9E%8B%E6%8E%A5%E5%8F%A3 "编��辑文件空间类型接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-10 "基本信息的直接链接")

*   请求方式：PUT
*   接口地址：`/v1/openapi/workspaceType`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-10 "请求参数的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| id | String | 待编辑的类型 ID |
| code | String | 文件空间类型编号 |
| title | Array | 多语言标题列表（同上） |
| icon | String | 图标路径 |
| sort | Number | 排序序号 |
| description | String | 类型描述 |

请求参数示例（Body）：

```
{  "id": "4493041505002323969",  "code": "workspace-type-code",  "title": [    { "languageCode": "zh-CN", "content": "中文名称" },    { "languageCode": "en-US", "content": "English Name" }  ],  "icon": "/icons/xxx.png",  "sort": 2,  "description": "更新说明"}
```

cURL 示例：

```
curl -X PUT "https://<host>/v1/openapi/workspaceType" ^  -H "Content-Type: application/json" ^  -H "Authorization: Bearer <token>" ^  -d "{ \"id\": \"4493041505002323969\", \"code\": \"workspace-type-code\", \"title\": [ { \"languageCode\": \"zh-CN\", \"content\": \"中文名称\" } ], \"icon\": \"/icons/xxx.png\", \"sort\": 2, \"description\": \"更新说明\" }"
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-10 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

返回示例：

```
{ "success": true, "msg": "" }
```

### 删除文件空间类型接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%88%A0%E9%99%A4%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4%E7%B1%BB%E5%9E%8B%E6%8E%A5%E5%8F%A3 "删除文件空间类型接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-11 "基本信息的直接链接")

*   请求方式：DELETE
*   接口地址：`/v1/openapi/workspaceType`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-11 "请求参数的直接链接")

| 参数名 | 类型 | 位置 | 说明 |
| --- | --- | --- | --- |
| ids | Array(Number) | Query 或 Body | 待删除的类型 ID 列表，支持批量 |

请求参数示例（Body）：

```
[4493061452348784640, 4493061452348784641]
```

cURL 示例：

```
curl -X DELETE "https://<host>/v1/openapi/workspaceType" ^  -H "Content-Type: application/json" ^  -H "Authorization: Bearer <token>" ^  -d "[4493061452348784640,4493061452348784641]"
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-11 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

返回示例：

```
{ "success": true, "msg": "" }
```

### 获取文件空间类型表单信息接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%8E%B7%E5%8F%96%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4%E7%B1%BB%E5%9E%8B%E8%A1%A8%E5%8D%95%E4%BF%A1%E6%81%AF%E6%8E%A5%E5%8F%A3 "获取文件空间类型表单信息接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-12 "基本信息的直接链接")

*   请求方式：GET
*   接口地址：`/v1/openapi/workspaceType`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-12 "请求参数的直接链接")

| 参数名 | 类型 | 位置 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| id | String | Query | 是 | 类型 ID |

请求参数示例（Query）：

```
/v1/openapi/workspaceType?id=4493061452348784640
```

cURL 示例：

```
curl -X GET "https://<host>/v1/openapi/workspaceType?id=4493061452348784640" ^  -H "Authorization: Bearer <token>"
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-12 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| data | Object(MasterDataVO) | 类型详情（包含 code、title、icon、sort、description 等） |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

返回示例：

```
{  "data": {    "id": "4493061452348784640",    "code": "workspace-type-code",    "title": [      { "languageCode": "zh-CN", "content": "中文名称" }    ],    "icon": "/icons/xxx.png",    "sort": 1,    "description": "说明"  },  "success": true,  "msg": ""}
```

### 启用/禁用文件空间类型接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%90%AF%E7%94%A8%E7%A6%81%E7%94%A8%E6%96%87%E4%BB%B6%E7%A9%BA%E9%97%B4%E7%B1%BB%E5%9E%8B%E6%8E%A5%E5%8F%A3 "启用/禁用文件空间类型接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-13 "基本信息的直接链接")

*   请求方式：PUT
*   接口地址：`/v1/openapi/workspaceType/Enable`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-13 "请求参数的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| id | Number(Int64) | 类型 ID |
| enable | Boolean | 是否启用（true = 启用，false = 禁用） |

请求参数示例（Body）：

```
{ "id": 4493061452348784640, "enable": true }
```

cURL 示例：

```
curl -X PUT "https://<host>/v1/openapi/workspaceType/Enable" ^  -H "Content-Type: application/json" ^  -H "Authorization: Bearer <token>" ^  -d "{ \"id\": 4493061452348784640, \"enable\": true }"
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-13 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

返回示例：

```
{ "success": true, "msg": "" }
```

### 获取文件空间类型下拉接口[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%8E%B7%E5%8F%96%E6%96%87%EF%BF%BD%E4%BB%B6%E7%A9%BA%E9%97%B4%E7%B1%BB%E5%9E%8B%E4%B8%8B%E6%8B%89%E6%8E%A5%E5%8F%A3 "获取文件空间类型下拉接口的直接链接")

#### 基本信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF-14 "基本信息的直接链接")

*   请求方式：GET
*   接口地址：`/v1/openapi/workspaceType/Dropdown`

#### 请求参数[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0-14 "请求参数的直接链接")

无

cURL 示例：

```
curl -X GET "https://<host>/v1/openapi/workspaceType/Dropdown" ^  -H "Authorization: Bearer <token>"
```

#### 返回值[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%BF%94%E5%9B%9E%E5%80%BC-14 "返回值的直接链接")

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| data | Array(DropdownVO) | 下拉数据列表 |
| success | Boolean | 接口调用结果（true = 成功，false = 失败） |
| msg | String | 提示信息（成功时通常为空字符串） |

返回示例：

```
{  "data": [    { "label": "个人空间", "value": "4493061452348784640" },    { "label": "团队空间", "value": "4493061452348784641" }  ],  "success": true,  "msg": ""}
```

## 用户[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E7%94%A8%E6%88%B7 "用户的直接链接")

### 添加用户（支持批量）[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%B7%BB%E5%8A%A0%E7%94%A8%E6%88%B7%E6%94%AF%E6%8C%81%E6%89%B9%E9%87%8F "添加用户（支持批量）的直接链接")

*   **接口地址：**`v1/openapi/user`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| `userName` | 是 | `string` | 无 | 账号/用户名 |
| `password` | 否 | `string` | '' | 密码 |
| `active` | 否 | `boolean` | true | 激活状态 |
| `userInfo` | 否 | `object` | 无 | 用户信息 |
| `userInfo.realName` | 否 | `string` | userName的值 | 真实姓名 |
| `userInfo.spell` | 否 | `string` | 无 | 真实姓名的拼音 |
| `userInfo.serialNumber` | 否 | `string` | 无 | 工号 |
| `userInfo.nickName` | 否 | `string` | 无 | 昵称 |
| `userInfo.gender` | 否 | `number` | 0 | 性别 0:FEMALE, 1:MALE |
| `userInfo.birthday` | 否 | `string` | 无 | 生日 |
| `userInfo.mobilePhone` | 否 | `string` | 无 | 手机号 |
| `userInfo.email` | 否 | `string` | 无 | 邮箱 |
| `userInfo.weChat` | 否 | `string` | 无 | 微信号 |
| `userInfo.avatar` | 否 | `string` | 无 | 头像 |
| `userInfo.region` | 否 | `string` | 无 | 地区 |
| `userInfo.joinTime` | 否 | `string` | 无 | 入职日期 |
| `userInfo.sort` | 否 | `number` | 0 | 排序号 |
| `userInfo.enable` | 否 | `boolean` | false | 启动/禁用 |
| `userInfo.description` | 否 | `string` | 无 | 描述 |
| `userInfo.external` | 否 | `boolean` | false | 内外部用户标识 false: 内部用户, true: 外部用户 |
| `userInfo.officePhoneNumber` | 否 | `string` | 无 | 办公电话 |
| `userInfo.isAad` | 否 | `boolean` | 无 | 账号是否来自AAD(microsoft Entra ID) |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/user' \--header 'Authorization: openapi {access_token}' \--data '[{      "userName": "user1",      "password": "abc123",      "active": true,      "userInfo": {          "realName": "张三",          "spell": "zhangsan",        "serialNumber": "123456",        "nickName": "张三",        "gender": 0,        "birthday": "1990-01-01",        "mobilePhone": "13800138000",        "email": "zhangsan@email.com",        "weChat": "zhangsan",        "avatar": "/icons/e5392a9c9efb423cab69ce040dcb04e7.png",        "region": "中国",        "joinTime": "2023-01-01",        "sort": 101,        "enable": true,        "description": "张三的描述",        "external": false,        "officePhoneNumber": "010-12345678",        "isAad": false    },  }]  '
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `object` | 响应数据对象 |
| `data.accountId` | `string` | 账号 ID |
| `data.userId` | `string` | 用户 ID |
| `data.userName` | `string` | 用户名 |
| `data.realName` | `string` | 用户真名 |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": "",	"data": [		{			"accountId": "123456",			"userId": "123456",			"userName": "user1",			"realName": "张三"		}	]}
```

### 修改用户[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E4%BF%AE%E6%94%B9%E7%94%A8%E6%88%B7 "修改用户的直接链接")

*   **接口地址：**`v1/openapi/user`
    
*   **请求方式：**`put`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| `userName` | 否 | `string` | 无 | 账号/用户名,只用来找到用户不会被修改,和id不能都为空 |
| `id` | 否 | `string` | '' | id,和userName不能都为空 |
| `active` | 是 | `boolean` | true | 激活状态 |
| `realName` | 是 | `string` | userName的值 | 真实姓名 |
| `spell` | 是 | `string` | 无 | 真实姓名的拼音 |
| `serialNumber` | 是 | `string` | 无 | 工号 |
| `nickName` | 是 | `string` | 无 | 昵称 |
| `gender` | 是 | `number` | 0 | 性别 0:FEMALE, 1:MALE |
| `birthday` | 是 | `string` | 无 | 生日 |
| `mobilePhone` | 是 | `string` | 无 | 手机号 |
| `email` | 是 | `string` | 无 | 邮箱 |
| `weChat` | 是 | `string` | 无 | 微信号 |
| `avatar` | 是 | `string` | 无 | 头像 |
| `region` | 是 | `string` | 无 | 地区 |
| `joinTime` | 是 | `string` | 无 | 入职日期 |
| `sort` | 是 | `number` | 0 | 排序号 |
| `enable` | 是 | `boolean` | false | 启动/禁用 |
| `description` | 是 | `string` | 无 | 描述 |
| `external` | 是 | `boolean` | false | 内外部用户标识 false: 内部用户, true: 外部用户 |
| `officePhoneNumber` | 是 | `string` | 无 | 办公电话 |
| `isAad` | 是 | `Boolean` | 无 | 账号是否来自AAD(microsoft Entra ID) |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/user' \--header 'Authorization: openapi {access_token}' \--data '{      "id": "123456",    "userName": "user1",       "realName": "张三",      "spell": "zhangsan",    "serialNumber": "123456",    "nickName": "张三",    "gender": 0,    "birthday": "1990-01-01",    "mobilePhone": "13800138000",    "email": "zhangsan@email.com",    "weChat": "zhangsan",    "avatar": "/icons/e5392a9c9efb423cab69ce040dcb04e7.png",    "region": "中国",    "joinTime": "2023-01-01",    "sort": 101,    "enable": true,    "description": "张三的描述",    "external": false,    "officePhoneNumber": "010-12345678",    "isAad": false}  '
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": ""}
```

### 删除用户[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%88%A0%E9%99%A4%E7%94%A8%E6%88%B7 "删除用户的直接链接")

*   **接口地址：**`v1/openapi/user`
    
*   **请求方式：**`delete`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
|  | 是 | `array` | 无 | 用户Id数组或用户名数组. 数组里只能全都是Id或全都是用户名. |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/user' \--header 'Authorization: openapi {access_token}' \--data '['user1','user2']'
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": ""}
```

### 启用用户[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%90%AF%E7%94%A8%E7%94%A8%E6%88%B7 "启用用户的直接链接")

*   **接口地址：**`v1/openapi/user/{userCode}/enable`
    
*   **请求方式：**`put`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **route参数：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| userCode | 是 | `string` | 无 | 用户Id或用户名 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/user/123456/enable' \--header 'Authorization: openapi {access_token}' \
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": ""}
```

### 禁用用户[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E7%A6%81%E7%94%A8%E7%94%A8%E6%88%B7 "禁用用户的直接链接")

*   **接口地址：**`v1/openapi/user/{userCode}/disable`
    
*   **请求方式：**`put`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **route参数：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| userCode | 是 | `string` | 无 | 用户Id或用户名 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/user/123456/disable' \--header 'Authorization: openapi {access_token}' \
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": ""}
```

### 启用/禁用用户（支持批量）[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%90%AF%E7%94%A8%E7%A6%81%E7%94%A8%E7%94%A8%E6%88%B7%E6%94%AF%E6%8C%81%E6%89%B9%E9%87%8F "启用/禁用用户（支持批量）的直接链接")

*   **接口地址：**`v1/openapi/user/enable`
    
*   **请求方式：**`put`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| codes | 是 | `array` | 无 | 用户Id数组或用户名数组. 数组里只能全都是Id或全都是用户名. |
| operation | 是 | `boolean` | true | true: 启用, false: 禁用 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/user/enable' \--header 'Authorization: openapi {access_token}' \--data '{  "codes": ['user1', 'user2'],  "operation": true}'
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": ""}
```

### 获取用户列表（分页）[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%8E%B7%E5%8F%96%E7%94%A8%E6%88%B7%E5%88%97%E8%A1%A8%E5%88%86%E9%A1%B5 "获取用户列表（分页）的直接链接")

*   **接口地址：**`v1/openapi/user/pageList`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| `orderField` | 是 | `string` | 无 | 用于排序的字段,Id含有时间信息,可以用id排序来用作创建时间的排序 |
| `orderType` | 是 | `string` | 无 | 排序类型, asc: 正序, desc: 倒序 |
| `conditions` | 否 | `array` | 无 | 查询条件,传多个时相互之间是 and 的关系 |
| `conditions.fieldName` | 否 | `string` | 无 | 查询条件的名称,如realName |
| `conditions.fieldValue` | 否 | `string` | 无 | 查询条件的值 |
| `conditions.conditionalType` | 否 | `number` | 0 | 查询条件的比较类型 0: 精确匹配, 1: 模糊匹配, 2: 大于, 3: 大于等于, 4:小于, 5: 小于等于, 6: 包含(in), 7: 不包含(not in), 8: 向左模糊匹配, 9:向右模糊匹配, 10: 不等于, 11: nullOrEmpty, 12: 不为空, 13: notLike |
| `pageIndex` | 是 | `number` | 无 | 页码 |
| `pageSize` | 是 | `number` | 无 | 每页的数量 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/user/pageList' \--header 'Authorization: openapi {access_token}' \{  "orderField": "id",  "orderType": "desc",  "conditions": [    {      "fieldName": "realName",      "fieldValue": "张三",      "conditionalType": 0    }  ],  "pageIndex": 1,  "pageSize": 15}
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `array` | 分页数据 |
| `data.id` | `string` | 账号 ID |
| `data.userId` | `string` | 用户 ID |
| `data.userName` | `string` | 用户名 |
| `data.active` | `boolean` | 是否激活 |
| `data.avatar` | `string` | 头像 |
| `data.birthday` | `string` | 生日 |
| `data.created` | `string` | 用户数据创建日期 |
| `data.modified` | `string` | 用户数据最后修改日期 |
| `data.description` | `string` | 描述 |
| `data.gender` | `number` | 性别 0:FEMALE, 1:MALE |
| `data.mobilePhone` | `string` | 手机号 |
| `data.nickName` | `string` | 昵称 |
| `data.email` | `string` | 邮箱 |
| `data.joinTime` | `string` | 入职日期 |
| `data.region` | `string` | 地区 |
| `data.weChat` | `string` | 微信号 |
| `data.spell` | `string` | 真实姓名的拼音 |
| `data.serialNumber` | `string` | 工号 |
| `data.accountId` | `string` | 用户所属的账号Id |
| `data.sort` | `number` | 排序号 |
| `data.officePhoneNumber` | `string` | 办公电话 |
| `data.external` | `boolean` | 内外部用户标识 false: 内部用户, true: 外部用户 |
| `data.isAad` | `boolean` | 账号是否来自AAD(microsoft Entra ID) |
| `data.enable` | `boolean` | 启动/禁用 |
| `pageIndex` | `number` | 当前页码 |
| `pageSize` | `number` | 页码大小 |
| `totalCount` | `number` | 总条数 |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{    "data": [        {			"accountId": "123456",			"userId": "123456",			"userName": "user1",			"realName": "张三"		}    ],    "pageSize": 15,    "pageIndex": 1,    "totalCount": 1,    "success": true,    "msg": null}
```

### 获取用户信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%8E%B7%E5%8F%96%E7%94%A8%E6%88%B7%E4%BF%A1%E6%81%AF "获取用户信息的直接链接")

*   **接口地址：**`v1/openapi/user/{userCode}`
    
*   **请求方式：**`get`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **route参数：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| userCode | 是 | `string` | 无 | 用户Id或用户名 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/user/123456' \--header 'Authorization: openapi {access_token}' \
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `object` | 响应数据对象 |
| `data.id` | `string` | 账号 ID |
| `data.userId` | `string` | 用户 ID |
| `data.userName` | `string` | 用户名 |
| `data.Active` | `boolean` | 是否激活 |
| `data.Avatar` | `string` | 头像 |
| `data.Birthday` | `string` | 生日 |
| `data.Created` | `string` | 用户数据创建日期 |
| `data.Modified` | `string` | 用户数据最后修改日期 |
| `data.Description` | `string` | 描述 |
| `data.Gender` | `number` | 性别 0:FEMALE, 1:MALE |
| `data.MobilePhone` | `string` | 手机号 |
| `data.NickName` | `string` | 昵称 |
| `data.Email` | `string` | 邮箱 |
| `data.JoinTime` | `string` | 入职日期 |
| `data.Region` | `string` | 地区 |
| `data.WeChat` | `string` | 微信号 |
| `data.Spell` | `string` | 真实姓名的拼音 |
| `data.SerialNumber` | `string` | 工号 |
| `data.AccountId` | `string` | 用户所属的账号Id |
| `data.Sort` | `number` | 排序号 |
| `data.OfficePhoneNumber` | `string` | 办公电话 |
| `data.External` | `boolean` | 内外部用户标识 false: 内部用户, true: 外部用户 |
| `data.IsAad` | `boolean` | 账号是否来自AAD(microsoft Entra ID) |
| `data.Enable` | `boolean` | 启动/禁用 |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": "",	"data": [		{			"accountId": "123456",			"userId": "123456",			"userName": "user1",			"realName": "张三"		}	]}
```

### 获取当前登录用户的信息[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%8E%B7%E5%8F%96%E5%BD%93%E5%89%8D%E7%99%BB%E5%BD%95%E7%94%A8%E6%88%B7%E7%9A%84%E4%BF%A1%E6%81%AF "获取当前登录用户的信息的直接链接")

*   **接口地址：**`v1/openapi/user/me`
    
*   **请求方式：**`get`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
    
*   **请求示例：**
    

```
curl --location 'http://localhost/v1/openapi/user/me' \--header 'Authorization: openapi {access_token}' \
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `object` | 响应数据对象 |
| `data.id` | `string` | 账号 ID |
| `data.userId` | `string` | 用户 ID |
| `data.userName` | `string` | 用户名 |
| `data.Active` | `boolean` | 是否激活 |
| `data.Avatar` | `string` | 头像 |
| `data.Birthday` | `string` | 生日 |
| `data.Created` | `string` | 用户数据创建日期 |
| `data.Modified` | `string` | 用户数据最后修改日期 |
| `data.Description` | `string` | 描述 |
| `data.Gender` | `number` | 性别 0:FEMALE, 1:MALE |
| `data.MobilePhone` | `string` | 手机号 |
| `data.NickName` | `string` | 昵称 |
| `data.Email` | `string` | 邮箱 |
| `data.JoinTime` | `string` | 入职日期 |
| `data.Region` | `string` | 地区 |
| `data.WeChat` | `string` | 微信号 |
| `data.Spell` | `string` | 真实姓名的拼音 |
| `data.SerialNumber` | `string` | 工号 |
| `data.AccountId` | `string` | 用户所属的账号Id |
| `data.Sort` | `number` | 排序号 |
| `data.OfficePhoneNumber` | `string` | 办公电话 |
| `data.External` | `boolean` | 内外部用户标识 false: 内部用户, true: 外部用户 |
| `data.IsAad` | `boolean` | 账号是否来自AAD(microsoft Entra ID) |
| `data.Enable` | `boolean` | 启动/禁用 |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": "",	"data": [		{			"accountId": "123456",			"userId": "123456",			"userName": "user1",			"realName": "张三"		}	]}
```

### 获取当前登录用户的角色[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%8E%B7%E5%8F%96%E5%BD%93%E5%89%8D%E7%99%BB%E5%BD%95%E7%94%A8%E6%88%B7%E7%9A%84%E8%A7%92%E8%89%B2 "获取当前登录用户的角色的直接链接")

*   **说明：** 不包含用户所属的组织的角色，不包含没有授予数据权限的角色（一般除了超管不会有这种情况）
    
*   **接口地址：**`v1/openapi/user/me/roles`
    
*   **请求方式：**`get`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
    
*   **请求示例：**
    

```
curl --location 'http://localhost/v1/openapi/user/me/roles' \--header 'Authorization: openapi {access_token}' \
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `array` | 响应数据对象 |
| `data.roleId` | `string` | 角色ID |
| `data.roleName` | `string` | 角色名称 |
| `data.dataPermissionList` | `array` | 用户在这个角色下的数据权限 |
| `data.dataPermissionList.BusinessTreeType` | `number` | 应用类型 |
| `data.dataPermissionList.DataPermissionObjectId` | `string` | 数据权限对象Id,比如如果是知识库权限就是那个知识库的Id |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": "",	"data": [		{			"roleId": "123456",			"roleName": "知识库访客",			"dataPermissionList": [                {                    "BusinessTreeType": 1,                    "DataPermissionObjectId": "123456"                }            ]		}	]}
```

### 获取用户已关联的角色[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%8E%B7%E5%8F%96%E7%94%A8%E6%88%B7%E5%B7%B2%E5%85%B3%E8%81%94%E7%9A%84%E8%A7%92%E8%89%B2 "获取用户已关联的角色的直接链接")

*   **接口地址：**`v1/openapi/user/{userCode}/roles`
    
*   **请求方式：**`get`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **route参数：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| userCode | 是 | `string` | 无 | 用户Id或用户名 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/user/123456/roles' \--header 'Authorization: openapi {access_token}' \
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `array` | 响应数据对象 |
| `data.roleId` | `string` | 角色ID |
| `data.roleName` | `string` | 角色名称 |
| `data.dataPermissionList` | `array` | 用户在这个角色下的数据权限 |
| `data.dataPermissionList.BusinessTreeType` | `number` | 应用类型 |
| `data.dataPermissionList.DataPermissionObjectId` | `string` | 数据权限对象Id,比如如果是知识库权限就是那个知识库的Id |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": "",	"data": [		{			"roleId": "123456",			"roleName": "知识库访客",			"dataPermissionList": [                {                    "BusinessTreeType": 1,                    "DataPermissionObjectId": "123456"                }            ]		}	]}
```

### 用户角色关系修改[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E7%94%A8%E6%88%B7%E8%A7%92%E8%89%B2%E5%85%B3%E7%B3%BB%E4%BF%AE%E6%94%B9 "用户角色关系修改的直接链接")

*   **接口地址：**`v1/openapi/user/{userCode}/roles`
    
*   **请求方式：**`put`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **route参数：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| userCode | 是 | `string` | 无 | 用户Id或用户名 |

*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
|  | 是 | `array` | 无 | 角色Id数组或角色名称数组. 数组里只能全都是Id或全都是名称. |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/user/123456/roles' \--header 'Authorization: openapi {access_token}' \{  ["1","3","5"]}
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `array` | 响应数据对象 |
| `data.roleId` | `string` | 角色ID |
| `data.roleName` | `string` | 角色名称 |
| `data.dataPermissionList` | `array` | 用户在这个角色下的数据权限 |
| `data.dataPermissionList.BusinessTreeType` | `number` | 应用类型 |
| `data.dataPermissionList.DataPermissionObjectId` | `string` | 数据权限对象Id,比如如果是知识库权限就是那个知识库的Id |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": "",	"data": [		{			"roleId": "123456",			"roleName": "知识库访客",			"dataPermissionList": [                {                    "BusinessTreeType": 1,                    "DataPermissionObjectId": "123456"                }            ]		}	]}
```

## 组织[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E7%BB%84%E7%BB%87 "组织的直接链接")

### 添加组织[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%B7%BB%E5%8A%A0%E7%BB%84%E7%BB%87 "添加组织的直接链接")

*   **接口地址：**`v1/openapi/organization`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| `code` | 是 | `string` | 无 | 组织代号,在系统中唯一，不可重复 |
| `parentId` | 否 | `string` | 无 | 父级组织机构Id和父级组Code称至少要填一项 |
| `parentCode` | 否 | `string` | 无 | 父级组织机构Code,和父级组织Id至少要填一项 |
| `name` | 是 | `string` | 无 | 名称 |
| `location` | 否 | `string` | 无 | 地址 |
| `remarks` | 否 | `string` | 无 | 备注 |
| `contact` | 否 | `string` | 无 | 联系方式 |
| `Info` | 否 | `string` | 无 | 机构信息 |
| `Extension` | 否 | `string` | 无 | 扩展信息 |
| `IsSubsidiary` | 否 | `boolean` | false | 是否子公司 |
| `sort` | 否 | `number` | 0 | 排序号 |
| `isEnable` | 否 | `boolean` | false | 启动/禁用 |
| `external` | 否 | `boolean` | false | 内外部组织标识 false: 内部, true: 外部 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/organization' \--header 'Authorization: openapi {access_token}' \--data '{      "code": "123456",    "parentId": "12345",    "name": "组织名称",    "location": "地址"}  '
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `object` | 响应数据对象 |
| `data.id` | `string` | 组织ID |
| `data.code` | `string` | 组织代号 |
| `data.parentId` | `string` | 父级组织Id |
| `data.parentName` | `string` | 父级组织名称 |
| `data.name` | `string` | 名称 |
| `data.location` | `string` | 地址 |
| `data.remarks` | `string` | 备注 |
| `data.contact` | `string` | 联系方式 |
| `data.Info` | `string` | 机构信息 |
| `data.Extension` | `number` | 扩展信息 |
| `data.IsSubsidiary` | `boolean` | 是否子公司 |
| `data.sort` | `number` | 排序号 |
| `data.isEnable` | `boolean` | 启动/禁用 |
| `data.external` | `boolean` | 内外部组织标识 |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": "",	"data": [		{			"id": "123456",            "code": "123456",            "parentId": "12345",            "name": "组织名称",            "location": "地址"		}	]}
```

### 更新组织[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%9B%B4%E6%96%B0%E7%BB%84%E7%BB%87 "更新组织的直接链接")

*   **接口地址：**`v1/openapi/organization`
    
*   **请求方式：**`put`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| `id` | 否 | `string` | 无 | 组织id,和code至少要填一项 |
| `code` | 否 | `string` | 无 | 组织代号,和id至少要填一项 |
| `parentId` | 否 | `string` | 无 | 父级组织机构Id和父级组织Code至少要填一项 |
| `parentCode` | 否 | `string` | 无 | 父级组织机构Code,和父级组织Id至少要填一项 |
| `name` | 是 | `string` | 无 | 名称 |
| `location` | 否 | `string` | 无 | 地址 |
| `remarks` | 否 | `string` | 无 | 备注 |
| `contact` | 否 | `string` | 无 | 联系方式 |
| `Info` | 否 | `string` | 无 | 机构信息 |
| `Extension` | 否 | `string` | 无 | 扩展信息 |
| `IsSubsidiary` | 否 | `boolean` | false | 是否子公司 |
| `sort` | 否 | `number` | 0 | 排序号 |
| `isEnable` | 否 | `boolean` | false | 启动/禁用 |
| `external` | 否 | `boolean` | false | 内外部组织标识 false: 内部, true: 外部 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/organization' \--header 'Authorization: openapi {access_token}' \--data '{      "code": "123456",    "parentId": "12345",    "name": "组织名称",    "location": "地址"}  '
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `object` | 响应数据对象 |
| `data.id` | `string` | 组织ID |
| `data.code` | `string` | 组织代号 |
| `data.parentId` | `string` | 父级组织Id |
| `data.parentName` | `string` | 是否激活 |
| `data.name` | `string` | 名称 |
| `data.location` | `string` | 地址 |
| `data.remarks` | `string` | 备注 |
| `data.contact` | `string` | 联系方式 |
| `data.Info` | `string` | 机构信息 |
| `data.Extension` | `number` | 扩展信息 |
| `data.IsSubsidiary` | `boolean` | 是否子公司 |
| `data.sort` | `number` | 排序号 |
| `data.isEnable` | `boolean` | 启动/禁用 |
| `data.external` | `boolean` | 内外部组织标识 |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": "",	"data": [		{			"id": "123456",            "code": "123456",            "parentId": "12345",            "name": "组织名称",            "location": "地址"		}	]}
```

### 删除组织[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%88%A0%E9%99%A4%E7%BB%84%E7%BB%87 "删除组织的直接链接")

*   **接口地址：**`v1/openapi/organization`
    
*   **请求方式：**`delete`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
|  | 是 | `array` | 无 | 组织Id数组或组织Code数组. 数组里只能全都是Id或全都是组织Code. |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/organization' \--header 'Authorization: openapi {access_token}' \--data '['org1','org2']'
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": ""}
```

### 获取树状组织结构[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E8%8E%B7%E5%8F%96%E6%A0%91%E7%8A%B6%E7%BB%84%E7%BB%87%E7%BB%93%E6%9E%84 "获取树状组织结构的直接链接")

*   **接口地址：**`v1/openapi/organization/tree`
    
*   **请求方式：**`get`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求query：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| `external` | 否 | `boolean` | false | 是否外部组织 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/organization/tree?external=false' \--header 'Authorization: openapi {access_token}' \
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `array` | 响应数据对象 |
| `data.nodeId` | `string` | 组织ID |
| `data.nodeName` | `string` | 组织名称 |
| `data.parentNodeId` | `string` | 父级组织Id |
| `data.code` | `string` | 组织代号 |
| `data.path` | `string` | 根节点至当前节点的路径--节点走过的id(用'/'来分开) |
| `data.external` | `boolean` | 内外部组织标识 |
| `data.childNodeList` | `array` | 子组织 |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": "",	"data": [        {            "isExternal": false,            "sort": 1,            "nodeId": "4034994050380595200",            "nodeName": "内部组织",            "path": "4034994050380595200/4419926899526991872",            "parentNodeId": "-1",            "childNodeList": [                {                    "isExternal": false,                    "sort": 1,                    "nodeId": "4419926899526991872",                    "nodeName": "IT",                    "path": "4034994050380595200/4419926899526991872",                    "parentNodeId": "4034994050380595200",                }            ]        }    ]}
```

### 根据用户组织关系获取用户（分页）[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%A0%B9%E6%8D%AE%E7%94%A8%E6%88%B7%E7%BB%84%E7%BB%87%E5%85%B3%E7%B3%BB%E8%8E%B7%E5%8F%96%E7%94%A8%E6%88%B7%E5%88%86%E9%A1%B5 "根据用户组织关系获取用户（分页）的直接链接")

*   **接口地址：**`v1/openapi/organization/getAllOrgUserPageList`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| `orderField` | 是 | `string` | 无 | 用于排序的字段,Id含有时间信息,可以用id排序来用作创建时间的排序 |
| `orderType` | 是 | `string` | 无 | 排序类型, asc: 正序, desc: 倒序 |
| `conditions` | 否 | `array` | 无 | 查询条件,传多个时相互之间是 and 的关系 |
| `conditions.fieldName` | 否 | `string` | 无 | 查询条件的名称,如organizationId |
| `conditions.fieldValue` | 否 | `string` | 无 | 查询条件的值 |
| `conditions.conditionalType` | 否 | `number` | 0 | 查询条件的比较类型 0: 精确匹配, 1: 模糊匹配, 2: 大于, 3: 大于等于, 4:小于, 5: 小于等于, 6: 包含(in), 7: 不包含(not in), 8: 向左模糊匹配, 9:向右模糊匹配, 10: 不等于, 11: nullOrEmpty, 12: 不为空, 13: notLike |
| `pageIndex` | 是 | `number` | 无 | 页码 |
| `pageSize` | 是 | `number` | 无 | 每页的数量 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/organization/getAllOrgUserPageList' \--header 'Authorization: openapi {access_token}' \{  "orderField": "id",  "orderType": "desc",  "conditions": [    {      "fieldName": "organizationName",      "fieldValue": "123456",      "conditionalType": 0    }  ],  "pageIndex": 1,  "pageSize": 15}
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `array` | 分页数据 |
| `data.userId` | `string` | 用户 ID |
| `data.account` | `string` | 用户名 |
| `data.accountId` | `boolean` | 账号 ID |
| `data.realName` | `string` | 真实姓名 |
| `data.organizationName` | `string` | 组织名称 |
| `data.organizationId` | `string` | 组织ID |
| `data.organizationParentId` | `string` | 父级组织ID |
| `data.Email` | `string` | 邮箱 |
| `data.Sort` | `number` | 排序号 |
| `data.External` | `boolean` | 内外部用户标识 false: 内部用户, true: 外部用户 |
| `pageIndex` | `number` | 当前页码 |
| `pageSize` | `number` | 页码大小 |
| `totalCount` | `number` | 总条数 |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{    "data": [        {            "account": "user1",            "accountId": "123456",            "userId": "123456",            "realName": "user1",            "organizationName": "org1",            "organizationId": "123456",            "external": false,            "organizationParentId": "12345",            "sort": 1,            "email": ""        }    ],    "pageSize": 15,    "pageIndex": 1,    "totalCount": 1,    "success": true,    "msg": null}
```

### 添加用户组织关系[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%B7%BB%E5%8A%A0%E7%94%A8%E6%88%B7%E7%BB%84%E7%BB%87%E5%85%B3%E7%B3%BB "添加用户组织关系的直接链接")

*   **接口地址：**`v1/openapi/organization/relationship`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| `organizationId` | 是 | `string` | 无 | 组织Id |
| `userId` | 是 | `string` | 无 | 用户Id |
| `sort` | 否 | `number` | 0 | 排序号 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/organization/relationship' \--header 'Authorization: openapi {access_token}' \--data '[{      "organizationId": "123456",    "userId": "12345"}]  '
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": ""}
```

### 删除用户组织关系[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E5%88%A0%E9%99%A4%E7%94%A8%E6%88%B7%E7%BB%84%E7%BB%87%E5%85%B3%E7%B3%BB "删除用户组织关系的直接链接")

*   **接口地址：**`v1/openapi/organization/relationship`
    
*   **请求方式：**`delete`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| `organizationIds` | 是 | `array` | 无 | 组织Id |
| `userIds` | 是 | `array` | 无 | 用户Id |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/organization/relationship' \--header 'Authorization: openapi {access_token}' \--data '{      "organizationIds": ["123456"],    "userIds": ["12345"]}  '
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{	"success": true,	"msg": ""}
```

### 查询组织下的用户(分页)[​](https://docs.serviceme.com/docs/technical-guide/open-api#%E6%9F%A5%E8%AF%A2%E7%BB%84%E7%BB%87%E4%B8%8B%E7%9A%84%E7%94%A8%E6%88%B7%E5%88%86%E9%A1%B5 "查询组织下的用户(分页)的直接链接")

*   **接口地址：**`v1/openapi/organization/getUserPages`
    
*   **请求方式：**`post`
    
*   **请求header：**
    

| 参数名称 | 必填 | 类型 | 参数解释 |
| --- | --- | --- | --- |
| Authorization | 是 | string | 填SERVICEME access token，值填写格式：openapi `{access_token}` |

*   **Content Type：**`application/json`
*   **请求body：**

| 参数名称 | 必填 | 类型 | 默认值 | 参数解释 |
| --- | --- | --- | --- | --- |
| `orderField` | 是 | `string` | 无 | 用于排序的字段,Id含有时间信息,可以用id排序来用作创建时间的排序 |
| `orderType` | 是 | `string` | 无 | 排序类型, asc: 正序, desc: 倒序 |
| `conditions` | 否 | `array` | 无 | 查询条件,传多个时相互之间是 and 的关系 |
| `conditions.fieldName` | 否 | `string` | 无 | 查询条件的名称,必须至少传入OrganizationId或OrganizationCode作为筛选条件 |
| `conditions.fieldValue` | 否 | `string` | 无 | 查询条件的值 |
| `conditions.conditionalType` | 否 | `number` | 0 | 查询条件的比较类型 0: 精确匹配, 1: 模糊匹配, 2: 大于, 3: 大于等于, 4:小于, 5: 小于等于, 6: 包含(in), 7: 不包含(not in), 8: 向左模糊匹配, 9:向右模糊匹配, 10: 不等于, 11: nullOrEmpty, 12: 不为空, 13: notLike |
| `pageIndex` | 是 | `number` | 无 | 页码 |
| `pageSize` | 是 | `number` | 无 | 每页的数量 |

*   **请求示例：**

```
curl --location 'http://localhost/v1/openapi/user/pageList' \--header 'Authorization: openapi {access_token}' \{  "orderField": "id",  "orderType": "desc",  "conditions": [    {      "fieldName": "OrganizationCode",      "fieldValue": "org1",      "conditionalType": 0    }  ],  "pageIndex": 1,  "pageSize": 15}
```

*   **响应body：**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `array` | 分页数据 |
| `data.id` | `string` | 用户 ID |
| `data.account` | `string` | 用户名 |
| `data.name` | `string` | 真实姓名 |
| `data.ownerMainDepartment` | `string` | 用户主岗 |
| `data.sort` | `number` | 排序号 |
| `data.status` | `boolean` | 用户启用状态 |
| `data.create` | `datetime` | 用户的创建时间 |
| `pageIndex` | `number` | 当前页码 |
| `pageSize` | `number` | 页码大小 |
| `totalCount` | `number` | 总条数 |
| `success` | `boolean` | 请求是否成功 |
| `msg` | `string` | 请求返回的消息（如果有） |

*   **响应示例：**

```
{    "data": [        {			"accountId": "123456",			"userId": "123456",			"userName": "user1",			"realName": "张三"		}    ],    "pageSize": 15,    "pageIndex": 1,    "totalCount": 1,    "success": true,    "msg": null}
```