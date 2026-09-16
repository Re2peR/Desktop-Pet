# 古风少女桌宠（Windows）

一个轻量的 PySide6 桌面宠物：透明无边框、始终置顶，角色和食物限制在主屏幕右下角活动，使用 60 帧古风少女动画，支持按时间问候、投喂和身体部位互动。

默认节奏经过放缓：动画约每 190ms 切换一帧，普通移动速度约 68 像素/秒，发现食物后的靠近速度约 105 像素/秒。

## 直接运行

已经打包好的版本可直接双击 `dist\GuofengDesktopPet.exe`，不需要安装 Python。若要从源码运行，则需要 Windows 10/11 和 Python 3.10 或更新版本；双击 `run.bat`，首次运行会在项目目录建立独立环境并安装依赖，之后会直接启动。

也可以在 PowerShell 中运行：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## 操作

- 按住角色左键移动即可拖拽，松开后它会继续活动。
- 轻点头部、肚子或脚部，会分别出现摸头、挠肚子和怕痒反馈。
- 右键角色打开“投喂”子菜单，可选择草莓、饼干、胡萝卜、西兰花或酸柠檬。
- 喜欢的食物会触发开心动画；不喜欢的食物会触发哭泣动画和对应台词。
- 食物也会自动随机出现；角色发现后会主动靠近、拾取并进食。
- 早晨会说早安，午间会提醒吃午饭；下午、晚上和深夜也有不同问候，每个时段每天只自动出现一次。
- 右键菜单还包含“暂停/继续”“随机生成食物”和“退出”。
- 角色和食物都只会在主屏幕右下角约 620×440 像素以内的活动区出现，不会跑遍整个桌面；拖拽也会限制在该区域内。

## 打包为 EXE

双击 `build.bat`。完成后可执行文件位于：

```text
dist\GuofengDesktopPet.exe
```

这是单文件、无控制台窗口的构建。Windows Defender 对未签名的个人 PyInstaller 程序偶尔会提示，请按你的安全策略处理；正式分发建议进行代码签名。

## macOS 运行与打包

支持 macOS 12 或更新版本，建议使用 Python 3.10–3.12。

从源码直接运行：在 Finder 中右键 `run_macos.command`，选择“打开”。首次运行会建立独立环境并安装依赖；如果系统提示脚本没有执行权限，在终端运行：

```bash
chmod +x run_macos.command build_macos.sh
./run_macos.command
```

生成原生应用和磁盘映像：

```bash
./build_macos.sh
```

输出文件为 `dist/GuofengDesktopPet.app` 和 `dist/GuofengDesktopPet.dmg`。脚本会启用高分辨率显示、隐藏 Dock 图标并进行本机临时签名。因为没有 Apple Developer ID，首次打开时可能需要在 Finder 中右键应用并选择“打开”。正式分发需要开发者证书和 Apple 公证。

项目也包含 `.github/workflows/build-macos.yml`，上传到 GitHub 后可以手动运行工作流，在 macOS 14 构建机上下载 `.app` 和 `.dmg` 成品。

## 更换角色素材

内置素材根据提供的红色汉服古风少女设定图制作。运行时使用 `assets/guofeng_frames/` 中的 60 张独立透明 PNG；三张原始 5×4 图集保存在 `assets/guofeng_sheets/`，原始设定参考保存在 `assets/guofeng_reference.png`。

```text
00–05  六帧待机呼吸
06–17  十二帧行走循环
18–21  四帧发现食物
22–25  四帧拾取
26–31  六帧进食
32–37  六帧开心
38–43  六帧哭泣
44–49  六帧挥手问候
50–53  四帧摸头反馈
54–56  三帧摸肚子反馈
57–58  两帧困倦
59      脚部怕痒反馈
```

每个独立帧为 280×280 RGBA PNG，程序按文件名顺序加载 `frame_000.png` 到 `frame_059.png` 并缩放显示。

## 项目结构

```text
main.py                         桌宠行为、窗口与交互
assets/guofeng_frames/          60 张独立透明动画帧（当前使用）
assets/guofeng_sheets/          三张 5×4 原始图集
assets/guofeng_reference.png    古风少女原始设定参考
tools/split_guofeng_sheets.py    60 帧拆分工具
run.bat                         一键安装并运行
build.bat                       一键打包 EXE
run_macos.command               macOS 双击运行脚本
build_macos.sh                  macOS 一键生成 APP 和 DMG
requirements.txt                Python 依赖
```
