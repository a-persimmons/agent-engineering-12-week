"""课程概念图：可维护的 SVG，图文同时描述同一条技术关系。"""
from pathlib import Path
from html import escape
import json

COLORS={'normal':('#f0f5fa','#b8cad9','#16354d'),'green':('#e6f6ee','#72b899','#175841'),'warn':('#fff4e6','#d5a366','#805222'),'dark':('#18384f','#18384f','#ffffff')}
FIGURES=[]
def node(x,y,title,sub='',tone='normal',w=220,h=72):return (x,y,title,sub,tone,w,h)
def edge(path,label='',x=0,y=0,tone='normal',dashed=False):return (path,label,x,y,tone,dashed)
def add(week,concept,title,caption,steps,nodes,edges,height=420,bands=None):
    FIGURES.append(dict(week=week,concept=concept,title=title,caption=caption,steps=steps,nodes=nodes,edges=edges,height=height,bands=bands or []))

add(0,1,'异步等待时，事件循环可以做别的事','await 让出的是等待时间。图中两项 I/O 重叠进行，但最终结果仍要等它们各自完成。',[
'主任务创建查询日志与查询文档两个协程。','日志等待网络时，事件循环可调度文档查询；两者不是同一个调用。','TaskGroup 等全部任务完成后，主任务才读取两个结果。'],[
node(190,20,'创建两个任务','TaskGroup','dark'),node(30,160,'日志查询','等待日志服务'),node(350,160,'文档查询','等待文档服务'),node(190,310,'汇总两个结果','退出 TaskGroup','green')],[edge('M300 92V125H140V160','调度',115,130),edge('M300 125H460V160','调度',450,130),edge('M140 232V274H300V310','日志完成',140,276),edge('M460 232V274H300','文档完成',460,276)],400)

add(1,1,'一次行动，怎样回到下一次决策？','模型只提出行动请求；Python 执行工具，把观察送回模型。新的决策使用新的证据。',[
'模型读当前消息，提出 get_logs 调用。','运行时校验并执行工具，拿到日志事实。','结果与原调用关联后回传；需要更多证据就再次请求模型，否则结束。'],[
node(30,30,'模型决策','选择下一步','dark'),node(350,30,'执行工具','Python 负责调用'),node(350,190,'获得观察','日志 / 文档 / 错误'),node(30,190,'更新上下文','回传结果与调用 id'),node(30,340,'结束任务','答案或明确的停止原因','green')],[edge('M250 66H350','行动请求',300,48),edge('M460 102V190','执行结果',460,152),edge('M350 226H250','观察回传',300,208),edge('M140 190V102','继续决策',140,151,'green'),edge('M30 66H14V376H30','决定结束',74,296,'green')],440)
add(1,3,'“停止”不只有成功这一种','停止状态需要明确区分：完成、等待补充和预算耗尽，不能都包装为成功。',[
'每轮开始前检查预算；不足就返回 incomplete。','预算充足才调用模型和工具。','依据实际结果标记完成或需要补充，未满足条件不能写 done。'],[
node(190,20,'检查剩余预算','轮次 / 时间 / 工具数量','dark'),node(30,170,'预算仍充足','执行下一轮'),node(350,170,'预算已耗尽','incomplete','warn'),node(30,320,'证据满足目标','完成并返回答案','green'),node(350,320,'仍缺关键资料','请求补充 / 转人工','warn')],[edge('M300 92V128H140V170','充足',140,130),edge('M300 128H460V170','不足',460,130,'warn'),edge('M140 242V320','验证通过',140,287,'green'),edge('M250 206H300V356H350','无法自行补齐',300,281,'warn')],420)

add(2,2,'工具失败后，先分类再处理','同样是失败，修正参数、有限重试和立即拒绝是三种不同动作。',[
'在执行前检查工具名、参数和用户权限。','非法参数交给模型修正；无权限不能靠重试绕过。','执行中的瞬时只读错误才进入有限重试，成功后返回结构化结果。'],[
node(190,20,'收到工具请求','名字 + 参数','dark'),node(30,170,'参数不合法','返回 invalid_args','warn'),node(350,170,'校验与权限通过','开始受控执行'),node(30,330,'瞬时读故障','退避 + 有限重试','warn'),node(350,330,'得到有效结果','返回 ok + data','green')],[edge('M300 92V125H140V170','修正输入',140,130,'warn'),edge('M300 125H460V170','允许执行',460,130),edge('M460 242V280H140V330','超时等瞬时错误',185,282,'warn'),edge('M460 242V330','执行成功',465,287,'green')],430)
add(2,3,'一次意图，重试多少次都只写一次','幂等键识别同一业务意图；同键不同参数不是重试，而是冲突。',[
'用 owner + key 查询已有操作。','没有记录时原子创建；已有且参数相同就返回原结果。','已有但参数不同就拒绝，不能悄悄执行另一个意图。'],[
node(190,20,'检查 owner + key','绑定业务意图','dark'),node(30,175,'没有记录','事务内创建一次','green'),node(350,175,'已经存在','比较参数'),node(30,330,'同键、同参数','返回原来的 id','green'),node(350,330,'同键、不同参数','冲突：拒绝写入','warn')],[edge('M300 92V130H140V175','首次请求',140,135),edge('M300 130H460V175','再次请求',460,135),edge('M460 247V284H140V330','相同',140,290,'green'),edge('M460 247V330','不同',460,290,'warn')],430)

add(3,0,'模型调用与 MCP：各自在哪一层？','Host 连接模型与 MCP Client。模型产生的工具调用，由 Host 转交给 Client，再由 Server 执行。',[
'Client 向 Server 发现工具，Host 把工具定义提供给模型。','模型返回结构化调用；Host 负责关联、校验和预算。','Client 按 MCP 协议调用 Server；工具结果沿原路回到模型上下文。'],[
node(30,40,'模型','提出工具调用','dark'),node(350,40,'Host / Agent 应用','管理上下文与执行'),node(350,200,'MCP Client','发现工具 / 转发请求'),node(30,200,'MCP Server','暴露协议能力'),node(30,350,'实际资源','文件 / 数据库 / API','green')],[edge('M250 64H350','调用请求',300,42),edge('M350 94H250','定义与结果',300,125),edge('M460 112V200','应用内调用',460,165),edge('M350 222H250','MCP 请求',300,200),edge('M250 254H350','MCP 结果',300,284),edge('M140 272V350','受控访问',140,316)],450)
add(3,3,'文件工具的边界在服务端','路径先解析，再检查根目录与文件规则。模型不能通过换一种说法扩大允许目录。',[
'服务端拿到相对路径后执行 resolve，包含符号链接解析。','只有仍处于 workspace 内、且满足扩展名与大小规则的路径才允许操作。','越界路径一律拒绝；生产仍需操作系统隔离防止竞态。'],[
node(190,20,'模型请求文件路径','notes.md / ../secret.txt','dark'),node(190,155,'resolve + 规则检查','目录 / 扩展名 / 大小'),node(30,315,'允许的 workspace','读取 / 受限新建','green'),node(350,315,'根目录外的资源','拒绝访问','warn')],[edge('M300 92V155','服务端校验',300,132),edge('M300 227V265H140V315','满足规则',140,270,'green'),edge('M300 265H460V315','越界或违规',460,270,'warn')],410)

add(4,2,'状态图：分支由当前状态决定','节点返回状态更新，条件边读取更新后的 attempts 决定继续收集还是结束。',[
'collect 只返回一条新增证据与新的 attempts。','reducer 把证据追加到 State，不重复追加旧列表。','route 在 attempts < 2 时回到 collect，否则进入 finish。'],[
node(190,20,'collect 节点','返回增量 evidence'),node(190,150,'合并 State','evidence 累加；次数更新','dark'),node(190,280,'route 条件边','检查 attempts'),node(190,420,'finish 节点','产生结果 → END','green')],[edge('M300 92V150','reducer',300,129),edge('M300 222V280','读取新状态',300,260),edge('M190 316H60V56H190','不足 2 次',76,190,'green'),edge('M300 352V420','达到 2 次',300,396,'green')],515)
add(4,4,'暂停后恢复，会重新进入节点','interrupt 前的代码会再次执行。把真实写操作放在审批后，并用幂等保护。',[
'第一次进入节点，运行到 interrupt 后保存状态并暂停。','外部用户批准后，以相同 thread_id 传入 Command(resume=...)。','节点从头重入，interrupt 返回恢复值；通过授权后才执行幂等操作。'],[
node(30,30,'第一次进入节点','先执行节点前半段'),node(30,175,'interrupt 暂停','保存状态与审批请求','warn'),node(350,175,'外部用户批准','同一 thread_id 恢复'),node(350,30,'节点从头重入','前半段会再次执行','dark'),node(350,350,'审批后的幂等操作','仅执行获批的具体动作','green')],[edge('M140 102V175','暂停',140,145),edge('M250 211H350','等待外部输入',300,190),edge('M460 175V102','Command',465,145),edge('M570 66H590V386H570','恢复值通过校验',488,290,'green')],450)

add(5,0,'三层记忆，三种生命周期','任务状态、会话历史、长期事实保存不同信息。跨层使用时仍要检查范围、来源与时效。',[
'工作记忆保存这次任务查到的证据与当前假设。','会话记忆保存这个线程的交互或摘要，支持继续对话。','长期资料跨会话保存项目约束，经检索与校验后进入当前上下文。'],[
node(30,40,'工作记忆','任务：已查证据与假设'),node(30,175,'会话记忆','线程：消息、摘要与索引'),node(30,310,'长期记忆','跨会话：环境 / 约束','green'),node(350,175,'本轮模型上下文','按预算选择与校验','dark')],[edge('M250 76H460V175','当前状态',450,130),edge('M250 211H350','会话历史',300,193),edge('M250 346H460V247','按需检索',460,293,'green')],415)

add(5,3,'上下文不是一个无限增长的聊天框','先为核心信息和输出预留空间，再在剩余预算中放证据与历史。这里的区域是职责示意，不代表固定 token 比例。',[
'固定约束、当前问题与工具定义先占用必需预算。','优先选择相关且有效的证据，历史可以摘要并保留原文指针。','为输出预留空间；原始材料放在外部，需要时再次检索。'],[
node(30,40,'核心上下文','约束 / 问题 / 工具定义','dark',540),node(30,150,'按预算选入','相关证据 / 有效记忆 / 摘要','normal',320),node(390,150,'外部原始资料','按需回溯','normal',180),node(30,300,'预留输出空间','不能把整个窗口都塞满输入','green',540)],[edge('M300 112V150','分配剩余预算',300,135),edge('M390 186H350','检索',370,165),edge('M190 222V300','保留生成余量',195,267)],405)

add(6,1,'固定 RAG 与 Agentic RAG 的区别','两种方案可以共用同一个检索器。变化在于：由谁决定查什么，以及是否继续查。',[
'固定 RAG 按预设路径完成一次检索与生成。','Agentic RAG 先判断证据缺口，再检索并观察结果。','证据不足时改查；达到目标或预算时停止。'],[
node(30,40,'固定一次检索','预设查询流程'),node(30,205,'生成答案','基于检索结果','green'),node(350,40,'模型判断缺口','决定是否需要检索','dark'),node(350,205,'检索并观察','query / hits / 来源'),node(350,370,'答案或资料不足','引用已验证的来源','green')],[edge('M140 112V205','固定路径',140,165),edge('M460 112V205','需要检索',460,165),edge('M350 241H310V76H350','继续查',306,170,'green'),edge('M460 277V370','完成或停止',460,331,'green')],470)
add(6,2,'回答错了，按证据流定位失败','先定位正确证据在哪一步丢失，再选择切片、召回、排序或生成侧的修复。',[
'原文里不存在答案：补充资料，而不是只改 Prompt。','原文有答案但候选没出现：检查切片与召回；候选里有但未进入上下文：检查排序与预算。','上下文已有正确证据而答案仍错：检查生成约束与语义忠实度。'],[
node(30,30,'原文资料','答案是否存在？'),node(350,30,'资料缺失','补数据 / 明确不知道','warn'),node(30,175,'召回与排序','证据是否进入 Prompt？'),node(350,175,'证据丢失','检查切片 / 召回 / 预算','warn'),node(30,320,'生成答案','断言是否受证据支持？'),node(350,320,'无依据断言','修生成与证据评测','warn')],[edge('M250 66H350','不存在',300,48,'warn'),edge('M140 102V175','存在',140,148),edge('M250 211H350','没进入',300,192,'warn'),edge('M140 247V320','已进入',140,291),edge('M250 356H350','不支持',300,339,'warn')],420)

add(7,1,'Supervisor 调度，角色交接产物','Supervisor 选择下一角色，但执行器仍检查前置条件。改写草稿后，旧的 review 必须失效。',[
'Researcher 输出带来源的 evidence，而不是全部聊天。','Writer 基于 evidence 生成 draft；Reviewer 输出 ok 与 feedback。','Supervisor 依据产物状态继续调度，只有当前草稿审阅通过才能完成。'],[
node(190,20,'Supervisor','状态 / 预算 / 下一角色','dark'),node(30,195,'Researcher','输出 evidence + 来源'),node(350,195,'Writer','输出 draft；旧审阅失效'),node(350,370,'Reviewer','输出 ok + feedback'),node(30,370,'完成条件检查','当前草稿审阅通过','green')],[edge('M190 56H140V195','调度',140,133),edge('M410 56H460V195','调度',460,133),edge('M250 231H350','证据交接',300,214),edge('M460 267V370','草稿',460,327),edge('M350 406H250','审阅结果',300,388,'green'),edge('M570 406H590V56H410','反馈给调度器',481,121,'normal',True)],475)

add(8,1,'一次有效改进，要走完整个评估闭环','开发集用来定位与调参；保留集用于最后验证。每个分数都要能回到具体案例。',[
'固定案例与版本，先得到基线与逐例轨迹。','按失败类型定位问题，只修改明确的因素。','在同一开发集回归，并用独立保留集确认泛化与退化。'],[
node(30,30,'固定开发集','输入 / gold / 预期行为'),node(350,30,'运行基线','模型与 Prompt 版本','dark'),node(350,195,'逐例轨迹与指标','定位失败发生在哪一层'),node(30,195,'修改并回归','一次优先改一个因素'),node(30,365,'独立保留集','验证收益与退化','green')],[edge('M250 66H350','执行',300,49),edge('M460 102V195','保存证据',460,153),edge('M350 231H250','失败分类',300,213),edge('M140 195V102','开发集重测',140,151,'green'),edge('M140 267V365','方案确定后',140,325,'green')],465)
add(8,3,'Trace 把一个任务拆成可定位的步骤','同一个 task trace 下，检索、模型与工具形成父子关系。指标告诉你哪里变差，轨迹告诉你为什么。',[
'任务使用统一 trace_id，保留 case_id 与版本。','模型、检索和工具各记录耗时、状态及脱敏后的输入输出。','定位到具体 observation，再判断是数据、模型还是执行器问题。'],[
node(30,30,'任务 Trace','case-001 / prompt-v2','dark',540),node(70,165,'检索 Observation','query / 文档 id / 耗时',w=480),node(70,280,'模型 Observation','模型版本 / usage / 输出',w=480),node(70,395,'工具 Observation','参数 / 返回值 / 错误',w=480)],[edge('M45 102V201H70'),edge('M45 201V316H70'),edge('M45 316V431H70')],495)

add(9,1,'SSE：事件随执行进展逐条到达','这是 POST 流式响应的简化时序。只有 done 表示成功结束，error 或断线需要另外处理。',[
'客户端发送请求并通过鉴权后，服务端开始流式响应。','start、tool、result 是独立事件，各自携带完整 JSON 数据。','成功才发送 done；流启动后的异常用 error 事件说明，不能依赖 HTTP 200 判断完成。'],[
node(30,20,'客户端','读取事件流','dark'),node(350,20,'FastAPI 服务','运行 Agent','dark')],[edge('M140 92V470','','',0,'normal',True),edge('M460 92V470','','',0,'normal',True),edge('M140 130H460','POST + 鉴权',300,119),edge('M460 200H140','start',300,189,'green'),edge('M460 265H140','tool / result',300,254,'green'),edge('M460 335H140','done：成功结束',300,324,'green'),edge('M460 420H140','或 error：明确失败',300,409,'warn',True)],490)
add(9,4,'不可信内容不能直接获得执行权','提示词与 Guardrails 是辅助；最终能否操作资源，要由可信执行器和权限系统强制决定。',[
'检索文档可能包含恶意指令，模型也可能被诱导提出危险动作。','工具请求必须经过身份、参数、资源范围与审批校验。','只读动作可按策略放行；敏感动作等待授权；越权动作直接拒绝。'],[
node(30,30,'外部文档 / 用户内容','可能包含 Prompt 注入','warn'),node(350,30,'模型提出动作','请求 ≠ 授权'),node(190,195,'可信执行器','身份 / 权限 / 参数 / 审批','dark'),node(30,370,'获准的具体操作','受限资源范围','green'),node(350,370,'越权或未获批准','拒绝 / 等待人工','warn')],[edge('M250 66H350','进入上下文',300,49),edge('M460 102V145H300V195','结构化请求',410,150),edge('M300 267V315H140V370','通过',140,323,'green'),edge('M300 315H460V370','不通过',460,323,'warn')],470)

add(10,1,'按职责拆开项目，按契约连接模块','模型、工具、状态和评估变化的原因不同。清楚的模块边界让替换模型与排查问题更容易。',[
'API 处理身份与交互；Runtime 管循环、状态、预算和停止。','模型适配器只负责模型协议，工具模块负责资源访问，记忆模块负责状态与资料。','评估和可观测性跨模块收集证据，不替代业务执行。'],[
node(190,20,'API / 用户入口','认证 / 输入 / 事件流'),node(190,150,'Agent Runtime','循环 / 状态 / 预算','dark'),node(30,295,'模型适配器','请求与响应协议'),node(350,295,'工具与记忆模块','资源访问 / 状态存储'),node(30,450,'评估与可观测性','贯穿各层：用例 / 轨迹 / 指标','green',540)],[edge('M300 92V150'),edge('M300 222V255H140V295'),edge('M300 255H460V295'),edge('M140 367V450','记录',140,414,'green',True),edge('M460 367V450','记录',460,414,'green',True)],550)

add(11,2,'最危险的超时：已经提交，响应却丢了','本地没有收到成功，不代表远端没有执行。重试必须识别原业务意图。',[
'第一次请求到达服务端，业务写入已经提交。','成功响应丢失，客户端只看到超时，此时真实状态未知。','客户端使用同一个幂等键重试；服务端找到原记录并返回原 id。'],[
node(30,20,'客户端','持有同一幂等键','dark'),node(350,20,'服务端','保存已提交记录','dark'),node(350,170,'首次写入提交','id = 42','green'),node(30,310,'客户端超时','不知道是否已成功','warn'),node(350,310,'重试命中原记录','仍返回 id = 42','green')],[edge('M140 92V130H460V170','首次请求：key-1',300,130),edge('M350 206H140V310','响应丢失',210,206,'warn',True),edge('M250 346H350','重试 key-1',300,325),edge('M460 382V425H140V382','原结果，不再次创建',300,430,'green')],455)
add(11,3,'一个数据库事务，不能覆盖远端副作用','本地数据库提交与外部 API 执行是两件事。跨系统可靠性需要幂等、状态机或 outbox 等额外设计。',[
'数据库可以原子地保存业务记录与待发送事件。','后台投递器读取待发送事件，调用远端 API。','远端也可能已执行但响应丢失，需要远端幂等键和本地状态核对；outbox 本身不保证只投递一次。'],[
node(30,45,'本地数据库事务','业务记录 + outbox','dark',540),node(190,205,'后台投递器','读取待发送事件'),node(30,365,'远端 API','用幂等键请求'),node(350,365,'本地投递状态','记录成功 / 待重试','green')],[edge('M300 117V205','事务提交后',300,168),edge('M300 277V315H140V365','发起调用',140,320),edge('M250 401H350','响应 / 核对结果',300,380,'green'),edge('M460 365V241H410','必要时重试',486,293,'normal',True)],465)

add(12,0,'系统设计先回答问题，再选择组件','先确定目标、数据、权限和预算；只有需要动态决策的部分才交给 Agent。',[
'明确用户目标与成功标准，列出约束和失败情形。','判断下一步能否预先确定；能确定时优先使用可验证的固定流程。','动态部分使用受约束 Agent，最后用同一套任务评估验证两种选择。'],[
node(190,20,'目标与约束','数据 / 权限 / 延迟 / 成本','dark'),node(190,155,'是否需要动态决策？','下一步依赖未知观察吗'),node(30,305,'固定 Workflow','预先规定主要执行路径'),node(350,305,'受约束 Agent','模型根据反馈选择下一步'),node(190,455,'用真实任务验证','结果 / 代价 / 失败边界','green')],[edge('M300 92V155'),edge('M300 227V260H140V305','不需要',140,267),edge('M300 260H460V305','需要',460,267),edge('M140 377V417H300V455'),edge('M460 377V417H300')],555)


def svg(figure):
    title=escape(figure['title']); caption=escape(figure['caption'])
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="{figure["height"]}" viewBox="0 0 600 {figure["height"]}" role="img" aria-labelledby="title desc">',f'<title id="title">{title}</title><desc id="desc">{caption}</desc>', '<defs>']
    for tone in COLORS:
        color=COLORS[tone][1] if tone=='dark' else {'normal':'#728c9d','green':'#278064','warn':'#b37a38'}[tone]
        parts.append(f'<marker id="arrow-{tone}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="{color}"/></marker>')
    parts+=['</defs>','<rect width="600" height="100%" fill="#ffffff"/>','<g font-family="system-ui, -apple-system, Segoe UI, PingFang SC, Microsoft YaHei, sans-serif">']
    labels=[]
    for path,label,x,y,tone,dashed in figure['edges']:
        color={'normal':'#728c9d','green':'#278064','warn':'#b37a38','dark':'#18384f'}[tone]
        parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#arrow-{tone})"'+(' stroke-dasharray="6 5"' if dashed else '')+'/>')
        if label:
            width=sum(15 if ord(c)>127 else 8 for c in label)+14
            labels.append(f'<rect x="{x-width/2}" y="{y-14}" width="{width}" height="23" rx="4" fill="white"/><text x="{x}" y="{y+2}" text-anchor="middle" font-size="15" fill="{color}">{escape(label)}</text>')
    parts+=labels
    for x,y,title,sub,tone,w,h in figure['nodes']:
        fill,stroke,color=COLORS[tone]
        assert 0<=x and x+w<=600 and 0<=y and y+h<=figure['height'],(figure['title'],title)
        assert sum(20 if ord(c)>127 else 11 for c in title)<=w-16,(figure['title'],title)
        assert sum(15 if ord(c)>127 else 8 for c in sub)<=w-12,(figure['title'],sub)
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x+w/2}" y="{y+30}" text-anchor="middle" font-size="20" font-weight="600" fill="{color}">{escape(title)}</text>')
        if sub: parts.append(f'<text x="{x+w/2}" y="{y+55}" text-anchor="middle" font-size="15" fill="'+('#c9e6df' if tone=='dark' else '#50677a')+f'">{escape(sub)}</text>')
    parts+=['</g></svg>']
    return ''.join(parts)

def attach_diagrams(course,out):
    folder=out/'diagrams';folder.mkdir(exist_ok=True)
    for index,f in enumerate(FIGURES,1):
        filename=f'week-{f["week"]:02d}-concept-{f["concept"]+1:02d}.svg'
        (folder/filename).write_text(svg(f),encoding='utf-8')
        course[f['week']]['concepts'][f['concept']]['diagram']={
            'src':'diagrams/'+filename,'title':f['title'],'caption':f['caption'],
            'steps':f['steps'],'alt':f['title']+'。'+'；'.join(f['steps']),
            'width':600,'height':f['height']}
    print(f'Attached {len(FIGURES)} concept diagrams')
