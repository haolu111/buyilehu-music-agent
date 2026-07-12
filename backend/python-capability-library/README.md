# Music Agent Python Capability Library

该目录是从“第一版”项目中独立整理出的后端能力组件库，不包含 Vue 页面、前端演示、生成页面、上传文件、运行缓存、数据库、密钥或个人数据。

## 内容

- `app/services/`：音乐课堂活动、组件注册、教学材料绑定、音乐规则、音高与音色、虚拟乐器、课堂套件及媒体处理能力。
- `contracts/music/`：组件运行所需的版本化音乐数据契约。

## 使用

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

在该目录作为工作目录时，可继续使用原有导入路径：

```python
from app.services.public_api import (
    build_default_music_media_session,
    build_primary_music_game_runtime,
    build_toolkit_spec,
)
```

部分媒体处理能力需要系统中可用的 FFmpeg。模型调用能力只读取运行环境变量，不在仓库中保存凭据。

## 数据边界

本目录只保存源码和静态契约。运行时产生的 `.env`、缓存、音视频、上传文件、数据库、日志和用户数据必须保留在仓库外或受忽略的本地目录中。
