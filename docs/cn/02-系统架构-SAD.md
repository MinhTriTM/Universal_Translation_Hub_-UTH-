# 软件架构文档 (SAD)

## Universal Translation Hub (UTH)

**遵循 IEEE 1471-2000 / ISO/IEC 42010 标准**

| 项目 | 内容 |
|------|------|
| 项目名称 | Universal Translation Hub (UTH) |
| 版本 | 1.0 |
| 作者 | Đoàn Minh Trí — DTHU大学 |
| AI平台 | 小米 MiMo V2.5 |
| 日期 | 2026-05-22 |

---

## 目录

1. [引言](#1-引言)
2. [逻辑视图](#2-逻辑视图)
3. [过程视图](#3-过程视图)
4. [物理视图](#4-物理视图)
5. [开发视图](#5-开发视图)
6. [设计决策](#6-设计决策)
7. [架构质量属性](#7-架构质量属性)

---

## 1. 引言

### 1.1 目的

本文档描述 Universal Translation Hub (UTH) 的软件架构，遵循 IEEE 1471-2000（系统与软件工程 — 架构描述）标准。文档通过 4+1 视图模型（逻辑视图、过程视图、物理视图、开发视图 + 场景视图）全面展示系统架构。

### 1.2 范围

本文档覆盖 UTH 系统的整体架构设计，包括：
- 分层架构设计
- 10 个 AI 智能体的设计模式
- 3 条处理管道的流程设计
- 部署架构和模块依赖关系

### 1.3 架构目标

| 目标 | 描述 | 优先级 |
|------|------|--------|
| 模块化 | 各管道独立，可单独开发和测试 | 最高 |
| 可扩展性 | 新增游戏引擎或语言对时最小化改动 | 高 |
| 容错性 | 单个智能体失败不影响整体系统 | 高 |
| 性能 | 充分利用 GPU 和 MiMo API 并行能力 | 中 |
| 可观测性 | 完整的日志和进度监控 | 中 |

---

## 2. 逻辑视图

### 2.1 分层架构

UTH 采用 6 层分层架构，每层职责清晰，层间通过定义良好的接口通信。

```
┌─────────────────────────────────────────────────────────────────┐
│ 第1层: 用户界面层 (Presentation Layer)                           │
│ ┌──────────┐ ┌──────────────┐ ┌─────────────┐                  │
│ │  Web UI  │ │  CLI 接口    │ │  REST API   │                  │
│ │(Jinja2)  │ │(argparse)    │ │(OpenAPI 3.0)│                  │
│ └──────────┘ └──────────────┘ └─────────────┘                  │
├─────────────────────────────────────────────────────────────────┤
│ 第2层: 智能体编排层 (Agent Orchestration Layer)                  │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐         │
│ │ Director     │ │ Router       │ │ Task Scheduler   │         │
│ │ Agent        │ │ Agent        │ │ (Celery/asyncio) │         │
│ └──────────────┘ └──────────────┘ └──────────────────┘         │
├─────────────────────────────────────────────────────────────────┤
│ 第3层: 管道层 (Pipeline Layer)                                   │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│ │ 游戏管道     │ │ 漫画管道     │ │ 影视管道     │             │
│ │ (12种引擎)   │ │(OCR+修复+渲染│ │(STT+TTS+配音)│             │
│ └──────────────┘ └──────────────┘ └──────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│ 第4层: 共享服务层 (Shared Services Layer)                        │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────────────┐│
│ │ 翻译引擎 │ │ 翻译记忆 │ │ 术语管理 │ │ 语音服务(TTS/VC)    ││
│ └──────────┘ └──────────┘ └──────────┘ └─────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│ 第5层: AI 模型层 (AI Model Layer)                                │
│ ┌────────────┐ ┌────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐│
│ │MiMo-V2.5   │ │MiMo    │ │MiMo    │ │MiMo-TTS │ │Voice     ││
│ │-Pro        │ │-V2.5   │ │-V2.5   │ │VoiceClone│ │Design    ││
│ │(推理)      │ │(通用)  │ │(TTS)   │ │(克隆)   │ │(设计)    ││
│ └────────────┘ └────────┘ └────────┘ └─────────┘ └──────────┘│
├─────────────────────────────────────────────────────────────────┤
│ 第6层: 基础设施层 (Infrastructure Layer)                         │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│ │ SQLite   │ │ FFmpeg   │ │ VLC      │ │ 文件系统 │           │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 智能体设计模式

#### 2.2.1 总体模式：多智能体协作 + 编排者模式

UTH 采用 **编排者模式（Orchestrator Pattern）**，Director Agent 作为中心协调者，管理 9 个专业子智能体的生命周期和任务分配。

```
                    ┌─────────────────┐
                    │  Director Agent │
                    │  (MiMo-V2.5-Pro)│
                    │                 │
                    │ ┌─────────────┐ │
                    │ │ 任务分解器  │ │
                    │ │ 状态管理器  │ │
                    │ │ 结果聚合器  │ │
                    │ │ 错误处理器  │ │
                    │ └─────────────┘ │
                    └────────┬────────┘
                             │ 编排指令
            ┌────────────────┼────────────────┐
            │                │                │
     ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
     │   Router    │ │ Translator  │ │     QA      │
     │   Agent     │ │   Agent     │ │   Agent     │
     └─────────────┘ └─────────────┘ └─────────────┘
            │                │                │
     ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
     │    OCR      │ │ Inpainting  │ │   Render    │
     │   Agent     │ │   Agent     │ │   Agent     │
     └─────────────┘ └─────────────┘ └─────────────┘
            │                │                │
     ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
     │    STT      │ │   Voice     │ │  VoiceClone │
     │   Agent     │ │   Agent     │ │   Agent     │
     └─────────────┘ └─────────────┘ └─────────────┘
```

#### 2.2.2 智能体内部结构

每个智能体遵循统一的内部结构：

```python
class BaseAgent(ABC):
    """智能体基类 — 定义统一接口"""

    def __init__(self, name: str, model: MiMoModel):
        self.name = name
        self.model = model          # 使用的 MiMo 模型
        self.status = AgentStatus.IDLE
        self.metrics = AgentMetrics()

    @abstractmethod
    async def process(self, task: Task) -> Result:
        """处理任务的核心方法"""
        pass

    @abstractmethod
    async def validate_input(self, task: Task) -> bool:
        """验证输入数据"""
        pass

    async def execute(self, task: Task) -> Result:
        """统一执行流程"""
        await self.validate_input(task)
        self.status = AgentStatus.RUNNING
        try:
            result = await self.process(task)
            self.status = AgentStatus.COMPLETED
            return result
        except Exception as e:
            self.status = AgentStatus.FAILED
            return await self.handle_error(e, task)

    async def handle_error(self, error: Exception, task: Task) -> Result:
        """统一错误处理：重试3次后降级"""
        for attempt in range(3):
            try:
                return await self.process(task)
            except Exception:
                continue
        return Result(status=Status.FAILED, error=error)
```

#### 2.2.3 智能体通信模式

智能体之间通过 **消息传递** 通信，而非直接调用：

```
Agent A ──[TaskMessage]──→ MessageQueue ──[TaskMessage]──→ Agent B
                                                         ──[ResultMessage]──→ Director
```

| 通信模式 | 使用场景 | 实现方式 |
|----------|----------|----------|
| 同步请求-响应 | 简单查询（术语查找） | asyncio 直接调用 |
| 异步任务队列 | 耗时处理（OCR、修复） | asyncio.Queue |
| 发布-订阅 | 进度更新通知 | WebSocket 广播 |
| 流水线 | 管道内顺序处理 | 链式 async 生成器 |

#### 2.2.4 各智能体设计细节

**Router Agent — 策略模式**

```python
class RouterAgent(BaseAgent):
    """路由器智能体 — 使用策略模式识别输入类型"""

    def __init__(self):
        super().__init__("Router", MiMoModel.V2_5)
        self.detectors = {
            "game": GameDetector(),      # 检测游戏引擎
            "comic": ComicDetector(),    # 检测漫画图片
            "video": VideoDetector(),    # 检测视频文件
        }

    async def process(self, task: Task) -> RoutingResult:
        # 并行运行所有检测器
        results = await asyncio.gather(*[
            detector.detect(task.input_files)
            for detector in self.detectors.values()
        ])
        # 选择置信度最高的结果
        best = max(results, key=lambda r: r.confidence)
        return RoutingResult(pipeline=best.type, config=best.config)
```

**Translator Agent — 管道过滤器模式**

```python
class TranslatorAgent(BaseAgent):
    """翻译智能体 — 管道过滤器模式"""

    def __init__(self):
        super().__init__("Translator", MiMoModel.V2_5)
        self.pipeline = [
            TMLookupFilter(),      # 1. 查翻译记忆库
            TerminologyFilter(),   # 2. 术语一致性检查
            MiMoTranslateFilter(), # 3. MiMo AI 翻译
            PostProcessFilter(),   # 4. 后处理（标点、格式）
            QAFilter(),            # 5. 质量检查
        ]

    async def process(self, task: Task) -> TranslationResult:
        text = task.source_text
        for filter in self.pipeline:
            text = await filter.apply(text, task.context)
        return TranslationResult(text=text)
```

### 2.3 核心类图

```
┌─────────────────────────────────────────────────────────┐
│                    UTH 系统核心类                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │  UTHSystem   │───→│ PipelineMgr  │                   │
│  │              │    │              │                   │
│  │ - agents[]   │    │ - pipelines[]│                   │
│  │ - config     │    │ + route()    │                   │
│  │ + start()    │    │ + execute()  │                   │
│  │ + shutdown() │    └──────┬───────┘                   │
│  └──────────────┘           │                           │
│         │                   ├── GamePipeline             │
│         │                   ├── ComicPipeline            │
│         │                   └── VideoPipeline            │
│         │                                               │
│  ┌──────▼──────┐    ┌──────────────┐                   │
│  │ BaseAgent   │    │ MiMoClient   │                   │
│  │ (抽象基类)  │───→│              │                   │
│  │             │    │ + chat()     │                   │
│  │ + process() │    │ + tts()      │                   │
│  │ + execute() │    │ + stt()      │                   │
│  └──────┬──────┘    │ + voiceclone()│                  │
│         │           └──────────────┘                   │
│         │                                               │
│  ┌──────┴──────────────────────────────────────────┐   │
│  │  10个具体智能体实现                               │   │
│  │  Director | Router | Translator | OCR |          │   │
│  │  Inpainting | Render | STT | Voice |            │   │
│  │  VoiceClone | QA                                │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │TranslationM  │    │ Terminology  │                   │
│  │emory         │    │ Manager      │                   │
│  │              │    │              │                   │
│  │ + lookup()   │    │ + lookup()   │                   │
│  │ + store()    │    │ + extract()  │                   │
│  │ + export()   │    │ + validate() │                   │
│  └──────────────┘    └──────────────┘                   │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │ Database     │    │ Config       │                   │
│  │ Manager      │    │ Manager      │                   │
│  │              │    │              │                   │
│  │ + query()    │    │ + load()     │                   │
│  │ + migrate()  │    │ + get()      │                   │
│  │ + backup()   │    │ + validate() │                   │
│  └──────────────┘    └──────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 过程视图

### 3.1 游戏翻译管道流程

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 用户选择 │───→│ 引擎检测 │───→│ 文本提取 │───→│ 翻译处理 │
│ 游戏文件 │    │(Router)  │    │(GameEng) │    │(Transltr)│
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                     │
┌──────────┐    ┌──────────┐    ┌──────────┐         │
│ 输出补丁 │←───│ 文件注入 │←───│ 质量检查 │←────────┘
│ (补丁包) │    │(GameEng) │    │ (QA)     │
└──────────┘    └──────────┘    └──────────┘

详细步骤:
1. 用户选择游戏文件/文件夹
2. Router Agent 检测游戏引擎类型
3. 对应引擎插件提取可翻译文本
4. Translator Agent 调用 MiMo-V2.5 翻译
   ├─ 查询翻译记忆库 (TM)
   ├─ 应用术语表
   ├─ AI 翻译
   └─ 后处理
5. QA Agent 检查翻译质量
6. 引擎插件将翻译写回游戏文件
7. 生成补丁包（保留原文件不变）
```

### 3.2 漫画翻译管道流程

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 用户选择 │───→│ 图片预处 │───→│ OCR 文字 │───→│ 文字区域 │
│ 漫画图片 │    │ 理       │    │ 识别     │    │ 分类     │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                     │
          ┌──────────────────────────────────────────┘
          │
          ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ AI 翻译  │───→│ 图像修复 │───→│ 文字渲染 │───→│ 输出图片 │
│(Transltr)│    │(Inpaint) │    │ (Render) │    │ (PNG/JPG)│
└──────────┘    └──────────┘    └──────────┘    └──────────┘

详细步骤:
1. 用户选择漫画图片文件（JPG/PNG/PDF）
2. 图片预处理（去噪、增强对比度）
3. OCR Agent 使用 MiMo-V2.5 识别文字
   ├─ 文字区域检测
   ├─ 竖排/横排文字识别
   └─ 文字类型分类（对白/旁白/音效）
4. 识别结果按类型分类
5. Translator Agent 翻译识别出的文字
6. Inpainting Agent 修复文字区域
   ├─ 移除原文文字
   └─ 恢复背景图像
7. Render Agent 将翻译文字渲染到图片
   ├─ 匹配原始字体风格
   ├─ 调整文字大小和布局
   └─ 应用描边和阴影效果
8. 输出翻译后的图片
```

### 3.3 影视配音管道流程

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 用户选择 │───→│ 音视频分 │───→│ STT 语音 │───→│ 说话人   │
│ 视频文件 │    │ 离       │    │ 识别     │    │ 分离     │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                     │
          ┌──────────────────────────────────────────┘
          │
          ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ AI 翻译  │───→│ 声音克隆 │───→│ TTS 合成 │───→│ 音视频   │
│(Transltr)│    │(VoiceCl) │    │ (Voice)  │    │ 混合     │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                     │
                                                     ▼
                                              ┌──────────┐
                                              │ 输出视频 │
                                              │(MKV/MP4) │
                                              └──────────┘

详细步骤:
1. 用户选择视频文件（MKV/MP4）和字幕（ASS/SRT）
2. FFmpeg 分离音轨和视频轨
3. STT Agent 使用 MiMo-V2.5 识别语音
   ├─ 语音转文字
   ├─ 时间戳对齐
   └─ 说话人分离
4. 识别结果按说话人分组
5. Translator Agent 翻译对白
6. VoiceClone Agent 克隆角色声音
   ├─ 提取角色声音样本（10-30秒）
   └─ 生成声音配置文件
7. Voice Agent 使用 MiMo-TTS 合成越南语语音
   ├─ 应用克隆的声音特征
   ├─ 调节语速和情感
   └─ 生成 WAV 音频
8. FFmpeg 混合 TTS 音频和原始背景音
9. FFmpeg 合成最终视频
10. VLC 预览播放验证
```

### 3.4 管道并行执行模型

```
┌────────────────────────────────────────────────────────┐
│                 Director Agent 调度器                    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  任务队列:                                              │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐             │
│  │ T1  │ │ T2  │ │ T3  │ │ T4  │ │ T5  │  ...        │
│  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘             │
│     │       │       │       │       │                  │
│     ▼       ▼       ▼       ▼       ▼                  │
│  ┌──────────────────────────────────────┐              │
│  │        asyncio 事件循环               │              │
│  │                                      │              │
│  │  Worker 1: T1 (游戏文本提取)         │              │
│  │  Worker 2: T2 (漫画 OCR)             │              │
│  │  Worker 3: T3 (影视 STT)             │              │
│  │  Worker 4: T1 (翻译) [等待提取完成]  │              │
│  │  ...                                 │              │
│  └──────────────────────────────────────┘              │
│                                                        │
│  并发控制:                                              │
│  - 最大并发 AI 请求数: 10 (受 MiMo API 限制)           │
│  - 最大并发文件处理数: 受 GPU 内存限制                   │
│  - 任务优先级: P0 > P1 > P2                            │
└────────────────────────────────────────────────────────┘
```

---

## 4. 物理视图

### 4.1 部署架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    用户工作站 (Windows 11)                    │
│                 Dell Alienware x14 R2                        │
│            RTX 4060 8GB | 16GB RAM | SSD                     │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              UTH Application (Python 3.12)             │  │
│  │                                                       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐              │  │
│  │  │FastAPI   │ │ Agent    │ │ Pipeline │              │  │
│  │  │Server    │ │ Runtime  │ │ Engine   │              │  │
│  │  │:8080     │ │          │ │          │              │  │
│  │  └──────────┘ └──────────┘ └──────────┘              │  │
│  │                                                       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐              │  │
│  │  │ SQLite   │ │ FFmpeg   │ │ VLC      │              │  │
│  │  │ Database │ │ Encoder  │ │ Preview  │              │  │
│  │  └──────────┘ └──────────┘ └──────────┘              │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              NVIDIA GPU (RTX 4060)                     │  │
│  │  ┌──────────────┐ ┌──────────────┐                    │  │
│  │  │ CUDA Runtime │ │ cuDNN        │                    │  │
│  │  │ (图像处理)   │ │ (AI推理加速) │                    │  │
│  │  └──────────────┘ └──────────────┘                    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 小米 MiMo API 云服务                          │
│                                                             │
│  ┌────────────┐ ┌────────┐ ┌────────┐ ┌─────────┐         │
│  │MiMo-V2.5   │ │MiMo    │ │MiMo-TTS│ │Voice    │         │
│  │-Pro        │ │-V2.5   │ │        │ │Clone    │         │
│  └────────────┘ └────────┘ └────────┘ └─────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 目录结构

```
universal-translation-hub/
├── main.py                          # 应用入口
├── requirements.txt                 # Python 依赖
├── .env                             # 环境变量（API 密钥）
├── config/
│   ├── settings.yaml                # 全局配置
│   ├── engines/                     # 游戏引擎配置
│   │   ├── rpgmaker.yaml
│   │   ├── unity.yaml
│   │   ├── renpy.yaml
│   │   └── ...
│   └── voices/                      # 声音配置文件
├── src/
│   ├── __init__.py
│   ├── agents/                      # 10个AI智能体
│   │   ├── base.py                  # BaseAgent 抽象基类
│   │   ├── director.py              # Director Agent
│   │   ├── router.py                # Router Agent
│   │   ├── translator.py            # Translator Agent
│   │   ├── ocr.py                   # OCR Agent
│   │   ├── inpainting.py            # Inpainting Agent
│   │   ├── render.py                # Render Agent
│   │   ├── stt.py                   # STT Agent
│   │   ├── voice.py                 # Voice Agent (TTS)
│   │   ├── voiceclone.py            # VoiceClone Agent
│   │   └── qa.py                    # QA Agent
│   ├── pipelines/                   # 3条处理管道
│   │   ├── base.py                  # BasePipeline 抽象基类
│   │   ├── game.py                  # 游戏管道
│   │   ├── comic.py                 # 漫画管道
│   │   └── video.py                 # 影视管道
│   ├── engines/                     # 游戏引擎插件
│   │   ├── base.py                  # BaseEngine 抽象基类
│   │   ├── rpgmaker_mv.py
│   │   ├── rpgmaker_vxace.py
│   │   ├── unity.py
│   │   ├── renpy.py
│   │   ├── kirikiri.py
│   │   ├── nscripter.py
│   │   └── wolf.py
│   ├── services/                    # 共享服务
│   │   ├── mimo_client.py           # MiMo API 客户端
│   │   ├── translation_memory.py    # 翻译记忆库
│   │   ├── terminology.py           # 术语管理器
│   │   ├── audio_processor.py       # 音频处理（FFmpeg）
│   │   └── video_processor.py       # 视频处理（FFmpeg+VLC）
│   ├── models/                      # 数据模型
│   │   ├── database.py              # SQLite 管理
│   │   ├── translation.py           # 翻译单元模型
│   │   ├── project.py               # 项目模型
│   │   └── voice_profile.py         # 声音配置模型
│   ├── api/                         # REST API 路由
│   │   ├── routes.py
│   │   ├── websocket.py
│   │   └── schemas.py
│   └── utils/                       # 工具函数
│       ├── file_handler.py
│       ├── encoding.py
│       └── logger.py
├── templates/                       # Jinja2 HTML 模板
├── static/                          # 静态资源
├── tests/                           # 测试文件
└── docs/                            # 文档
    ├── cn/                          # 中文文档
    ├── en/                          # 英文文档
    └── vi/                          # 越南语文档
```

---

## 5. 开发视图

### 5.1 模块依赖关系图

```
┌──────────────────────────────────────────────────────────┐
│                     main.py (入口)                        │
└──────────────────────────┬───────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │   api/   │    │ agents/  │    │pipelines/│
    │ (FastAPI)│    │(智能体)  │    │ (管道)   │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         │               │    ┌──────────┘
         │               │    │
         │               ▼    ▼
         │        ┌──────────────┐
         │        │  engines/    │
         │        │ (游戏引擎)   │
         │        └──────┬───────┘
         │               │
         ▼               ▼
    ┌──────────────────────────┐
    │       services/          │
    │  ┌────────┐ ┌─────────┐ │
    │  │ mimo   │ │ audio   │ │
    │  │ client │ │ process │ │
    │  └────────┘ └─────────┘ │
    │  ┌────────┐ ┌─────────┐ │
    │  │ tm     │ │ term    │ │
    │  │ memory │ │ manager │ │
    │  └────────┘ └─────────┘ │
    └────────────┬─────────────┘
                 │
                 ▼
    ┌──────────────────────────┐
    │        models/           │
    │  ┌────────┐ ┌─────────┐ │
    │  │database│ │ config  │ │
    │  │(SQLite)│ │(YAML)   │ │
    │  └────────┘ └─────────┘ │
    └──────────────────────────┘
```

### 5.2 技术栈明细

| 层次 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 运行时 | Python | 3.12+ | 主要编程语言 |
| Web 框架 | FastAPI | 0.110+ | REST API 和 Web 服务 |
| 模板引擎 | Jinja2 | 3.1+ | HTML 模板渲染 |
| 异步框架 | asyncio | 内置 | 异步任务编排 |
| 数据库 | SQLite | 3.40+ | 本地数据存储 |
| ORM | SQLAlchemy | 2.0+ | 数据库访问层 |
| 数据迁移 | Alembic | 1.13+ | 数据库迁移管理 |
| HTTP 客户端 | httpx | 0.27+ | MiMo API 调用 |
| 图像处理 | Pillow | 10.0+ | 图像读写和基础处理 |
| 图像修复 | OpenCV | 4.9+ | 图像修复和预处理 |
| 音视频 | FFmpeg | 6.0+ | 音视频处理 |
| 视频预览 | python-vlc | 3.0+ | VLC 集成预览 |
| 任务队列 | asyncio.Queue | 内置 | 异步任务队列 |
| 配置管理 | PyYAML | 6.0+ | YAML 配置文件解析 |
| 日志 | loguru | 0.7+ | 结构化日志 |
| 测试 | pytest | 8.0+ | 单元和集成测试 |
| CLI | argparse | 内置 | 命令行接口 |

### 5.3 外部依赖关系

```toml
[project]
dependencies = [
    "fastapi>=0.110",
    "uvicorn[standard]>=0.27",
    "jinja2>=3.1",
    "sqlalchemy[asyncio]>=2.0",
    "alembic>=1.13",
    "httpx>=0.27",
    "pillow>=10.0",
    "opencv-python>=4.9",
    "python-vlc>=3.0",
    "pyyaml>=6.0",
    "loguru>=0.7",
    "python-multipart>=0.0.9",
    "websockets>=12.0",
]
```

---

## 6. 设计决策

### 6.1 架构决策记录 (ADR)

#### ADR-001: 选择多智能体架构而非单体架构

| 项目 | 内容 |
|------|------|
| 状态 | 已采纳 |
| 决策 | 采用 10 个独立 AI 智能体的多智能体架构 |
| 理由 | 1. 各智能体职责单一，便于独立开发和测试<br>2. 不同智能体可使用不同的 MiMo 模型<br>3. 单个智能体失败不影响整体系统<br>4. 便于并行处理提升性能 |
| 风险 | 智能体间通信增加复杂度 |
| 缓解 | 统一 BaseAgent 接口，消息队列通信 |

#### ADR-002: 选择 FastAPI 而非 Flask/Django

| 项目 | 内容 |
|------|------|
| 状态 | 已采纳 |
| 决策 | 使用 FastAPI 作为 Web 框架 |
| 理由 | 1. 原生异步支持，适合 IO 密集型 AI 调用<br>2. 自动 OpenAPI 文档生成<br>3. WebSocket 原生支持（实时进度推送）<br>4. Pydantic 数据验证，类型安全 |
| 替代方案 | Flask（无原生异步）、Django（过重） |

#### ADR-003: 选择 SQLite 而非 PostgreSQL

| 项目 | 内容 |
|------|------|
| 状态 | 已采纳 |
| 决策 | 使用 SQLite 作为本地数据库 |
| 理由 | 1. 零配置，无需安装数据库服务器<br>2. 单文件数据库，便于备份和迁移<br>3. 性能满足单用户桌面应用场景<br>4. SQLAlchemy 抽象层支持未来切换 |
| 风险 | 不支持多用户并发写入 |
| 缓解 | 当前为单用户应用，未来可迁移到 PostgreSQL |

#### ADR-004: 游戏引擎插件化设计

| 项目 | 内容 |
|------|------|
| 状态 | 已采纳 |
| 决策 | 每种游戏引擎实现为独立插件 |
| 理由 | 1. 新增引擎只需实现 BaseEngine 接口<br>2. 各引擎独立，互不影响<br>3. 社区可贡献新引擎插件 |
| 接口 | `extract()`, `inject()`, `detect()` |

#### ADR-005: MiMo API 客户端统一封装

| 项目 | 内容 |
|------|------|
| 状态 | 已采纳 |
| 决策 | 所有 MiMo 模型调用通过统一客户端 |
| 理由 | 1. 统一错误处理和重试逻辑<br>2. 统一 rate limiting 和 credits 监控<br>3. 便于切换模型或添加新模型 |

---

## 7. 架构质量属性

### 7.1 质量属性场景

| 质量属性 | 场景 | 测量指标 |
|----------|------|----------|
| **性能** | 用户提交 100 页漫画翻译 | 总处理时间 ≤ 20 分钟 |
| **可靠性** | MiMo API 暂时不可用 | 自动重试 3 次，指数退避 |
| **可扩展性** | 新增一种游戏引擎 | 仅需实现 1 个新文件（≤ 500 行） |
| **可维护性** | 修改翻译提示词 | 仅修改配置文件，无需改代码 |
| **可观测性** | 排查翻译质量问题 | 通过日志可追溯每个翻译决策 |

### 7.2 性能预算

| 操作 | 目标时间 | 瓶颈 |
|------|----------|------|
| 系统启动 | ≤ 10s | 模型加载 |
| 游戏文本提取（1000句） | ≤ 1min | 文件 I/O |
| 翻译（100句） | ≤ 1min | MiMo API 延迟 |
| 漫画 OCR（10页） | ≤ 1min | GPU 推理 |
| 图像修复（10页） | ≤ 2min | GPU 推理 |
| TTS 合成（100句） | ≤ 2min | MiMo TTS API |

---

**文档结束**

*本文档遵循 IEEE 1471-2000 标准编写，使用 4+1 视图模型描述 UTH 系统架构。*
