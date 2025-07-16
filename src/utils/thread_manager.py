import threading
import time
from typing import List, Optional, Callable


class ThreadManager:
    def __init__(self):
        self.threads: List[threading.Thread] = []
        self.stop_events: List[threading.Event] = []
        self.lock = threading.Lock()
    
    def create_thread(self, target: Callable, args=(), kwargs=None, timeout=30):
        """创建可控制的线程"""
        if kwargs is None:
            kwargs = {}
        
        print(f"[线程管理器] 开始创建线程，目标函数: {target}")
        print(f"[线程管理器] 参数: args={args}, kwargs={kwargs}, timeout={timeout}")
        
        stop_event = threading.Event()
        
        def wrapped_target():
            thread_name = threading.current_thread().name
            print(f"[线程 {thread_name}] 线程开始执行")
            try:
                # 为当前线程设置stop_event属性
                current_thread = threading.current_thread()
                current_thread.stop_event = stop_event
                
                if hasattr(target, '__call__'):
                    # 如果目标函数支持stop_event参数，传递给它
                    import inspect
                    sig = inspect.signature(target)
                    print(f"[线程 {thread_name}] 目标函数签名: {sig}")
                    if 'stop_event' in sig.parameters:
                        kwargs['stop_event'] = stop_event
                        print(f"[线程 {thread_name}] 检测到stop_event参数，已添加到kwargs")
                    
                    print(f"[线程 {thread_name}] 准备调用目标函数: {target}")
                    target(*args, **kwargs)
                    print(f"[线程 {thread_name}] 目标函数执行完成")
                else:
                    print(f"[线程 {thread_name}] 目标不是可调用对象，直接执行")
                    target()
            except Exception as e:
                print(f"[线程 {thread_name}] 线程执行错误: {e}")
                import traceback
                print(f"[线程 {thread_name}] 详细错误信息:")
                traceback.print_exc()
            finally:
                print(f"[线程 {thread_name}] 线程结束，清理资源")
                # 清理线程属性
                if hasattr(current_thread, 'stop_event'):
                    delattr(current_thread, 'stop_event')
        
        thread = threading.Thread(target=wrapped_target, daemon=True)
        thread.name = f"GameThread-{len(self.threads)+1}"
        
        with self.lock:
            self.threads.append(thread)
            self.stop_events.append(stop_event)
        
        print(f"[线程管理器] 线程创建成功: {thread.name}")
        return thread, stop_event
    
    def start_thread(self, target: Callable, args=(), kwargs=None, timeout=30):
        """创建并启动线程"""
        print(f"[线程管理器] 启动线程请求: {target}")
        thread, stop_event = self.create_thread(target, args, kwargs, timeout)
        print(f"[线程管理器] 正在启动线程: {thread.name}")
        thread.start()
        print(f"[线程管理器] 线程已启动: {thread.name}")
        return thread, stop_event
    
    def stop_all_threads(self, timeout=5):
        """停止所有线程"""
        with self.lock:
            # 发送停止信号
            for stop_event in self.stop_events:
                stop_event.set()
            
            # 等待线程结束
            for thread in self.threads:
                if thread.is_alive():
                    thread.join(timeout)
                    if thread.is_alive():
                        print(f"警告：线程 {thread.name} 在 {timeout} 秒后仍在运行")
            
            # 清理
            self.threads.clear()
            self.stop_events.clear()
    
    def cleanup_finished_threads(self):
        """清理已结束的线程"""
        with self.lock:
            alive_threads = []
            alive_events = []
            
            for thread, event in zip(self.threads, self.stop_events):
                if thread.is_alive():
                    alive_threads.append(thread)
                    alive_events.append(event)
            
            self.threads = alive_threads
            self.stop_events = alive_events


# 全局线程管理器实例
thread_manager = ThreadManager()