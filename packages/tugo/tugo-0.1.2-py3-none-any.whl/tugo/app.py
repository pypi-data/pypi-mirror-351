import asyncio
import random
import time
import os
import sys
import io
import types
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import flet as ft


@dataclass
class CrawlerConfig:
    process_count: int = 3
    retry_count: int = 0
    retry_interval: float = 0.0

    def update(self, process_count: int, retry_count: int, interval: float):
        self.process_count = process_count
        self.retry_count = retry_count
        self.retry_interval = interval

    def __str__(self):
        return (
            f"并发数: {self.process_count}\n"
            f"重试次数: {self.retry_count}\n"
            f"重试间隔: {self.retry_interval} 秒"
        )


class TextIOWrapper(io.TextIOBase):
    def __init__(self, page):
        self.page = page
        self.original_stdout = sys.stdout

    def write(self, text):
        if text.strip() and not getattr(self, "_in_write", False):
            try:
                self._in_write = True
                self.original_stdout.write(text.rstrip('\n') + '\n')
                self.original_stdout.flush()
                self.page.loop.call_soon_threadsafe(
                    lambda: self.page.pubsub.send_all({
                        "type": "log",
                        "data": {"message": text.strip()}
                    })
                )
            except Exception as e:
                self.original_stdout.write(f"[Log Error] {str(e)}\n")
                self.original_stdout.flush()
            finally:
                self._in_write = False


class CrawlerApp:
    def __init__(self):
        self.config = CrawlerConfig()
        self.is_running = False
        self.is_timing = False
        self.start_time = 0.0
        self.global_semaphore: Optional[asyncio.Semaphore] = None
        self.page: Optional[ft.Page] = None
        self.timer_task: Optional[asyncio.Task] = None
        self.write_queue = asyncio.Queue()
        self.writer_task = None

    def create_config_view(self):
        return ft.Column([
            ft.Text("⚙️ 当前配置", style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Text(f"并发数: {self.config.process_count}", selectable=True),
            ft.Text(f"重试次数: {self.config.retry_count}", selectable=True),
            ft.Text(f"重试间隔: {self.config.retry_interval} 秒", selectable=True),
        ], width=200, height=150)

    def refresh_semaphore(self):
        self.global_semaphore = asyncio.Semaphore(self.config.process_count)

    def send_update(self, type_: str, **kwargs):
        # 只打印某些类型的消息，例如log和error
        # if type_ in ["log", "error"]:
        #     print(f"发送消息: {type_}, 数据: {kwargs}")
        
        try:
            self.page.loop.call_soon_threadsafe(
                lambda: self.page.pubsub.send_all({"type": type_, "data": kwargs})
            )
        except Exception as e:
            print(f"发送消息失败: {e}")

    async def file_writer(self):
        # 先写入标题行到两个文件
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        header = f"===== 爬虫运行开始于 {timestamp} =====\n"

        # 初始化文件并写入标题
        for filename in ["success.txt", "failed.txt"]:
            try:
                with open(filename, "a", encoding="utf-8") as f:  # 使用'w'模式覆盖旧文件
                    f.write(header)
            except Exception as e:
                self.send_update("error", message=f"文件初始化失败: {str(e)}")

        # 然后进入正常的写入循环
        while True:
            data = await self.write_queue.get()
            if data is None:  # 终止信号
                break

            filename, content = data
            try:
                with open(filename, "a", encoding="utf-8") as f:  # 使用'a'模式追加
                    f.write(content + "\n")
            except Exception as e:
                self.send_update("error", message=f"文件写入失败: {str(e)}")
            finally:
                self.write_queue.task_done()

    async def do_main(self, url):
        # 把同步函数包装进线程中执行
        return await asyncio.to_thread(self._sync_do_main, url)

    def _sync_do_main(self, url):
        return True

    async def crawl_single_url(self, url: str, idx: int, total: int):
        try:
            await self.global_semaphore.acquire()
        except (asyncio.CancelledError, Exception):
            return

        if not self.is_running:
            self.global_semaphore.release()
            return

        try:
            result = await self.do_main(url)
            success = bool(result)  # 确保 result 是一个"真值"（例如 True）
            if success:
                await self.write_queue.put(("success.txt", url))
            else:
                await self.write_queue.put(("failed.txt", f"{url}|采集失败"))
        except Exception as e:
            await self.write_queue.put(("failed.txt", f"{url}|{str(e)}"))
            self.send_update("error", message=f"[{idx}/{total}] {url} 采集失败: {str(e)}")
            success = False

        self.send_update("result", url=url, success=success)
        self.send_update("progress", value=idx / total)
        self.send_update("status", value=f"正在爬取 ({idx}/{total}): {url}")

        try:
            self.global_semaphore.release()
        except:
            pass

    # async def process_crawl_results(self, urls: List[str]):
    #     total = len(urls)
    #     self.send_update("progress", value=0)
    #     self.send_update("status", value="开始爬取...")
    #
    #     tasks = [
    #         self.crawl_single_url(url, i + 1, total)
    #         for i, url in enumerate(urls)
    #     ]
    #
    #     batch_size = self.config.process_count
    #     for i in range(0, len(tasks), batch_size):
    #         batch = tasks[i:i + batch_size]
    #         await asyncio.gather(*batch)
    #         await asyncio.sleep(0.1)
    #
    #     self.send_update("status", value="爬取完成！" if self.is_running else "已终止运行")
    #     self.is_running = False
    #     self.is_timing = False

    async def process_crawl_results(self, urls: List[str]):
        try:
            total = len(urls)
            self.send_update("progress", value=0)
            self.send_update("status", value="开始爬取...")

            semaphore = asyncio.Semaphore(self.config.process_count)

            async def sem_task(task):
                async with semaphore:
                    return await task

            tasks = [
                sem_task(self.crawl_single_url(url, i + 1, total))
                for i, url in enumerate(urls)
            ]

            await asyncio.gather(*tasks)

            self.send_update("status", value="爬取完成！" if self.is_running else "已终止运行")
            self.is_running = False
            self.is_timing = False
        finally:
            # 安全关闭写入器
            if self.writer_task:
                await self.write_queue.put(None)
                await self.writer_task

    async def update_timer(self):
        """更新计时器的异步任务"""
        while self.is_timing:
            try:
                elapsed = time.time() - self.start_time
                # 使用pubsub发送计时器更新消息
                self.send_update("timer", elapsed=elapsed)
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Timer update error: {e}")
                break

    async def start_crawling(self, e):
        self.tab_control.selected_index = 0
        self.switch_tab(None)

        file_path = self.file_input.value
        if not file_path or not os.path.exists(file_path):
            self.send_update("status", value="请先选择有效的 txt 文件")
            return

        # 停止之前的计时器任务
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()

        self.start_time = time.time()
        self.is_timing = True
        self.is_running = True

        # 启动写入器任务 - 这会先写入标题行
        self.writer_task = asyncio.create_task(self.file_writer())

        # 启动计时器任务
        self.timer_task = asyncio.create_task(self.update_timer())

        # 清理UI状态
        self.log_view.controls.clear()
        self.success_list.controls.clear()
        self.failed_list.controls.clear()
        self.success_count.value = "0"
        self.failed_count.value = "0"
        self.progress.value = 0
        self.time_counter.value = "运行时间: 0.0秒"
        self.page.update()

        self.send_update("log", message=f"⚙️ 当前配置:\n{str(self.config)}")

        with open(file_path, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]

        self.refresh_semaphore()

        async def refresh_task():
            while self.is_running:
                await asyncio.sleep(0.1)
                try:
                    self.page.update()
                except:
                    pass

        asyncio.create_task(refresh_task())
        asyncio.create_task(self.process_crawl_results(urls))

    def stop_crawling(self, e):
        self.is_running = False
        self.is_timing = False

        # 取消计时器任务
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()

        self.send_update("status", value="正在停止...")

    def handle_file_pick(self, e):
        self.file_picker.pick_files(allowed_extensions=["txt"])

    def handle_file_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.file_input.value = e.files[0].path
            self.page.update()

    def update_theme(self, e):
        mode = self.theme_dropdown.value
        if mode == "dark":
            self.page.bgcolor = None
            self.page.theme_mode = ft.ThemeMode.DARK
        elif mode == "eye_care":
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.page.bgcolor = ft.Colors.GREEN_50
        else:
            self.page.bgcolor = None
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.update()

    def update_config(self, e):
        try:
            new_config = {
                "process_count": int(self.process_dropdown.value),
                "retry_count": int(self.retry_dropdown.value),
                "interval": float(self.interval_input.value)
            }
            self.config.update(**new_config)
            self.refresh_semaphore()
            self.send_update("log", message="⚙️ 配置已更新")
        except Exception as ex:
            self.send_update("error", message=f"配置更新失败: {ex}")

    def switch_tab(self, e):
        self.content_area.controls.clear()
        if self.tab_control.selected_index == 0:
            self.config_container.content = self.create_config_view()
            self.content_area.controls.append(self.main_view)
        else:
            self.content_area.controls.append(self.settings_view)
        self.page.update()

    async def on_pubsub_message(self, msg: Dict[str, Any]):
        try:
            msg_type = msg["type"]
            data = msg["data"]
    
            if msg_type == "progress" and self.progress and hasattr(self.progress, "page") and self.progress.page:
                self.progress.value = data["value"]
                self.progress.update()
    
            elif msg_type == "status" and self.status and hasattr(self.status, "page") and self.status.page:
                self.status.value = data["value"]
                self.status.update()
    
            elif msg_type == "timer" and self.time_counter and hasattr(self.time_counter, "page") and self.time_counter.page:
                # 处理计时器更新消息
                elapsed = data["elapsed"]
                d, r = divmod(elapsed, 86400)
                h, r = divmod(r, 3600)
                m, s = divmod(r, 60)
                parts = []
                if d: parts.append(f"{int(d)}天")
                if h: parts.append(f"{int(h)}小时")
                if m: parts.append(f"{int(m)}分")
                self.time_counter.value = f"运行时间: {''.join(parts)}{s:.1f}秒"
                self.time_counter.update()
    
            elif msg_type == "log":
                # 强制更新页面以确保日志显示
                self.log_view.controls.append(ft.Text(data["message"], selectable=True))
                if len(self.log_view.controls) > 100:
                    self.log_view.controls.pop(0)
                # 确保页面更新
                self.page.update()
    
            elif msg_type == "result":
                if not self.success_list or not hasattr(self.success_list, "page") or not self.success_list.page:
                    return
                    
                target_list = self.success_list if data["success"] else self.failed_list
                target_list.controls.append(ft.Text(data["url"], selectable=True))
    
                stat = self.success_count if data["success"] else self.failed_count
                stat.value = str(len(target_list.controls))
                stat.update()
    
                target_list.update()
    
            elif msg_type == "error":
                print(f"[ERROR] {data['message']}")
    
            elif msg_type == "config":
                self.config.update(**data)
                self.send_update("log", message="⚙️ 配置已更新")
        except Exception as e:
            print(f"处理pubsub消息出错: {str(e)}")

    def create_ui_components(self):
        # 创建 UI 组件
        self.file_input = ft.TextField(
            label="选择txt文件",
            expand=True,
            read_only=True,
        )
        self.file_button = ft.ElevatedButton(
            "选择文件",
            icon=ft.icons.FOLDER_OUTLINED,
        )

        # 添加单条URL测试组件
        self.single_url_input = ft.TextField(
            label="输入单个URL进行测试",
            expand=True,
            hint_text="例如: https://example.com",
        )
        self.test_single_button = ft.FilledButton(
            "测试URL",
            icon=ft.icons.SCIENCE_OUTLINED,
        )

        self.progress = ft.ProgressBar(width=400)
        self.status = ft.Text("等待开始...", size=14)
        self.success_list = ft.ListView(
            height=120,
            auto_scroll=True,
            spacing=2,
            padding=10,
        )
        self.failed_list = ft.ListView(
            height=120,
            auto_scroll=True,
            spacing=2,
            padding=10,
        )
        self.log_view = ft.ListView(
            height=200,
            auto_scroll=True,
            spacing=2,
            padding=10,
        )
        self.config_container = ft.Container(
            content=self.create_config_view(),
            padding=10,
        )
        self.time_counter = ft.Text(
            "运行时间: 0.0秒",
            key="time_counter",
            size=14,
        )

        # 统计标签
        self.success_count = ft.Text(
            "0",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.GREEN_400,
            key="success_count"
        )
        self.failed_count = ft.Text(
            "0",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.RED_400,
            key="failed_count"
        )

        # 控制按钮
        self.start_button = ft.FilledButton(
            "开始爬取",
            icon=ft.icons.PLAY_ARROW_OUTLINED,
            on_click=self.start_crawling
        )
        self.stop_button = ft.FilledButton(
            "停止爬取",
            icon=ft.icons.STOP_OUTLINED,
            on_click=self.stop_crawling
        )

        # 文件选择器
        self.file_picker = ft.FilePicker(on_result=self.handle_file_result)
        self.file_button.on_click = self.handle_file_pick

        # 设置组件
        self.theme_dropdown = ft.Dropdown(
            label="主题模式",
            options=[
                ft.dropdown.Option("default", "默认主题"),
                ft.dropdown.Option("dark", "深色主题"),
                ft.dropdown.Option("eye_care", "护眼模式")
            ],
            value="default",
            width=200,
        )
        self.retry_dropdown = ft.Dropdown(
            label="重试次数",
            options=[ft.dropdown.Option(str(i), f"{i}次") for i in range(0, 6)],
            value=str(self.config.retry_count),
            width=150,
        )
        self.process_dropdown = ft.Dropdown(
            label="并发数",
            options=[ft.dropdown.Option(str(i), f"{i}个") for i in range(1, 17)],
            value=str(self.config.process_count),
            width=150,
        )
        self.interval_input = ft.TextField(
            label="重试间隔 (秒)",
            value=str(self.config.retry_interval),
            width=150,
            suffix_text="秒",
        )

        # 绑定事件处理器
        self.theme_dropdown.on_change = self.update_theme
        self.retry_dropdown.on_change = self.update_config
        self.process_dropdown.on_change = self.update_config
        self.interval_input.on_change = self.update_config

    def create_views(self):
        # 主视图
        self.main_view = ft.Column([
            # 单条URL测试部分
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🔍 单条URL测试", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.Row([self.single_url_input, self.test_single_button]),
                    ]),
                    padding=20,
                ),
                margin=ft.margin.only(bottom=20)
            ),
            # 批量测试部分
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📑 批量URL测试", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.Row([self.file_input, self.file_button]),
                        ft.Container(height=10),
                        ft.Row([self.start_button, self.stop_button]),
                        ft.Container(height=20),
                        ft.Row([self.progress, self.time_counter]),
                        self.status,
                    ]),
                    padding=20,
                ),
                margin=ft.margin.only(bottom=20)
            ),
            ft.Row([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("✅ 成功的 URL", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                                self.success_count
                            ]),
                            self.success_list
                        ]),
                        padding=10,
                    ),
                    expand=True
                ),
                ft.Container(width=20),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("❌ 失败的 URL", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                                self.failed_count
                            ]),
                            self.failed_list
                        ]),
                        padding=10,
                    ),
                    expand=True
                ),
            ]),
            ft.Container(height=20),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📝 日志输出", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.Container(
                            content=self.log_view,
                            height=300,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=8,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE
                        )
                    ]),
                    padding=20,
                )
            )
        ], scroll=ft.ScrollMode.AUTO, spacing=0)

        # 设置视图
        self.settings_view = ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("⚙️ 设置", style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight=ft.FontWeight.BOLD),
                        ft.Container(height=20),
                        ft.Text("界面设置", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        ft.Container(height=10),
                        self.theme_dropdown,
                        ft.Container(height=20),
                        ft.Text("爬虫设置", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        ft.Container(height=10),
                        ft.Row([self.retry_dropdown, self.interval_input, self.process_dropdown], spacing=20)
                    ]),
                    padding=20,
                )
            )
        ])

        # 标签页
        self.tab_control = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="主界面",
                    icon=ft.icons.HOME_OUTLINED,
                ),
                ft.Tab(
                    text="设置",
                    icon=ft.icons.SETTINGS_OUTLINED,
                )
            ],
            expand=0
        )
        self.content_area = ft.Column()
        self.main_container = ft.Column([self.tab_control, self.content_area], expand=True)

    async def test_single_url(self, e):
        if not self.single_url_input.value:
            self.send_update("status", value="请输入要测试的URL")
            print("测试URL: 未输入URL")
            return

        url = self.single_url_input.value.strip()
        print(f"测试URL: {url}")
        
        # 发送开始测试的日志
        self.send_update("log", message=f"🔍 开始测试URL: {url}")
        self.send_update("status", value=f"正在测试: {url}")
        
        try:
            print("调用do_main方法...")
            result = await self.do_main(url)
            print(f"do_main返回结果: {result}")
            success = bool(result)  # 确保 result 是一个"真值"（例如 True）
            if success:
                print(f"测试成功: {url}")
                self.send_update("log", message=f"✅ {url} 测试成功")
            else:
                print(f"测试失败: {url}")
                self.send_update("log", message=f"❌ {url} 测试失败")
        except Exception as e:
            print(f"测试出错: {url}, 错误: {str(e)}")
            self.send_update("log", message=f"❌ {url} 测试出错: {str(e)}")

        self.send_update("status", value="测试完成")
        print("测试完成")

    def handle_test_single_url(self, e):
        """处理单条URL测试按钮点击"""
        url = self.single_url_input.value.strip()
        if not url:
            self.send_update("status", value="请输入要测试的URL")
            print("测试URL: 未输入URL")
            return
            
        print(f"开始处理URL测试: {url}")
        
        # 使用page.loop来安全地调度异步任务
        asyncio.run_coroutine_threadsafe(self.test_single_url(e), self.page.loop)

    async def initialize(self, page: ft.Page):
        self.page = page
        self.page.title = "简单爬虫工具"
        self.page.padding = 20
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.scroll = ft.ScrollMode.AUTO

        # 创建所有UI组件
        self.create_ui_components()
        self.create_views()

        # 设置异步事件处理器
        self.test_single_button.on_click = self.handle_test_single_url
        
        # 设置标签页切换事件
        self.tab_control.on_change = self.switch_tab

        # 添加文件选择器到页面
        self.page.overlay.append(self.file_picker)

        # 添加主容器到页面
        self.page.add(self.main_container)

        # 初始显示主视图
        self.content_area.controls.append(self.main_view)
        self.page.update()

        # 确保UI完全加载后再订阅消息
        print("订阅pubsub消息...")
        self.page.pubsub.subscribe(self.on_pubsub_message)
        
        # 发送一条测试消息
        self.send_update("log", message="⚙️ 系统初始化完成")

        # 重定向输出
        sys.stdout = TextIOWrapper(self.page)
        sys.stderr = TextIOWrapper(self.page)


async def main():
    def test(self, url):
        print(f"测试函数被调用，URL: {url}")
        # 返回一个真值，以便测试成功
        return True
        
    app = CrawlerApp()
    app._sync_do_main = test.__get__(app, CrawlerApp)
    await ft.app_async(
        target=app.initialize,
        view=ft.FLET_APP
    )


if __name__ == "__main__":
    asyncio.run(main())