import xarray as xr
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Union
import netCDF4 as nc

class Spliter:
    def __init__(self, input_folder: str, output_folder: str, time_window: int = 24, 
                 overlap: int = 0, time_unit: str = 'hours'):
        """
        初始化Spliter类
        
        Args:
            input_folder: 输入数据文件夹路径
            output_folder: 输出数据文件夹路径
            time_window: 时间窗口大小，默认24小时
            overlap: 时间窗口重叠时长，默认0
            time_unit: 时间单位，支持'hours', 'days', 'minutes'
        """
        # 获取当前项目目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_folder = os.path.join(current_dir, input_folder)
        self.output_folder = os.path.join(current_dir, output_folder)
        
        # 创建输出目录
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        # 时间窗口配置
        self.time_window = time_window
        self.overlap = overlap
        self.time_unit = time_unit
        
        # 支持的文件格式
        self.supported_formats = ['.nc', '.nc4', '.netcdf']
        
        # 初始化日志
        self._setup_logging()
        
        self.logger.info(f"Spliter初始化完成")
        self.logger.info(f"输入目录: {self.input_folder}")
        self.logger.info(f"输出目录: {self.output_folder}")
        self.logger.info(f"时间窗口: {time_window} {time_unit}")
        self.logger.info(f"重叠时长: {overlap} {time_unit}")

    def _setup_logging(self):
        """设置日志配置"""
        logs_dir = os.path.join(self.output_folder, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"spliter_{timestamp}.log"
        log_filepath = os.path.join(logs_dir, log_filename)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.logger = logging.getLogger('Spliter')
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _convert_time_to_timedelta(self, value: int) -> timedelta:
        """将时间值转换为timedelta对象"""
        if self.time_unit == 'hours':
            return timedelta(hours=value)
        elif self.time_unit == 'days':
            return timedelta(days=value)
        elif self.time_unit == 'minutes':
            return timedelta(minutes=value)
        else:
            raise ValueError(f"不支持的时间单位: {self.time_unit}")

    def _get_input_files(self) -> List[str]:
        """获取输入文件列表"""
        files = []
        if not os.path.exists(self.input_folder):
            self.logger.error(f"输入目录不存在: {self.input_folder}")
            return files
        
        for file in os.listdir(self.input_folder):
            if any(file.lower().endswith(fmt) for fmt in self.supported_formats):
                files.append(os.path.join(self.input_folder, file))
        
        files.sort()
        self.logger.info(f"找到 {len(files)} 个输入文件")
        return files

    def _load_dataset(self, file_path: str) -> Optional[xr.Dataset]:
        """加载数据集"""
        try:
            self.logger.info(f"加载文件: {os.path.basename(file_path)}")
            ds = xr.open_dataset(file_path)
            
            # 检查时间维度
            time_dims = ['time', 'Time', 'TIME', 'valid_time']
            time_dim = None
            for dim in time_dims:
                if dim in ds.dims:
                    time_dim = dim
                    break
            
            if time_dim is None:
                self.logger.warning(f"未找到时间维度: {file_path}")
                return None
                
            # 确保时间维度是datetime格式
            if not pd.api.types.is_datetime64_any_dtype(ds[time_dim]):
                try:
                    ds[time_dim] = pd.to_datetime(ds[time_dim])
                except Exception as e:
                    self.logger.error(f"时间维度转换失败: {e}")
                    return None
            
            # 统一时间维度名称为'time'
            if time_dim != 'time':
                ds = ds.rename({time_dim: 'time'})
            
            self.logger.info(f"数据集加载成功 - 时间范围: {ds.time.min().values} 到 {ds.time.max().values}")
            self.logger.info(f"时间步数: {len(ds.time)}")
            
            return ds
            
        except Exception as e:
            self.logger.error(f"加载文件失败 {file_path}: {str(e)}")
            return None

    def _generate_time_windows(self, start_time: pd.Timestamp, end_time: pd.Timestamp) -> List[Tuple[pd.Timestamp, pd.Timestamp]]:
        """生成时间窗口列表"""
        windows = []
        window_delta = self._convert_time_to_timedelta(self.time_window)
        step_delta = self._convert_time_to_timedelta(self.time_window - self.overlap)
        
        current_start = start_time
        window_count = 0
        
        while current_start < end_time:
            current_end = current_start + window_delta
            
            # 确保不超过数据的结束时间
            if current_end > end_time:
                current_end = end_time
            
            # 检查窗口是否有足够的数据
            if current_end > current_start:
                windows.append((current_start, current_end))
                window_count += 1
            
            current_start += step_delta
            
            # 如果当前开始时间已经超过或等于结束时间，退出循环
            if current_start >= end_time:
                break
        
        self.logger.info(f"生成了 {len(windows)} 个时间窗口")
        return windows

    def _split_dataset(self, dataset: xr.Dataset, windows: List[Tuple[pd.Timestamp, pd.Timestamp]], 
                      base_filename: str) -> List[str]:
        """根据时间窗口切分数据集"""
        output_files = []
        
        for i, (start_time, end_time) in enumerate(windows):
            try:
                # 选择时间窗口内的数据
                window_data = dataset.sel(time=slice(start_time, end_time))
                
                if len(window_data.time) == 0:
                    self.logger.warning(f"时间窗口 {i+1} 无数据: {start_time} - {end_time}")
                    continue
                
                # 生成输出文件名
                start_str = start_time.strftime("%Y%m%d_%H%M%S")
                end_str = end_time.strftime("%Y%m%d_%H%M%S")
                output_filename = f"{base_filename}_window_{i+1:04d}_{start_str}_{end_str}.nc"
                output_path = os.path.join(self.output_folder, output_filename)
                
                # 添加元数据
                window_data.attrs.update({
                    'split_info': f'Time window {i+1}',
                    'window_start': start_time.isoformat(),
                    'window_end': end_time.isoformat(),
                    'window_duration': f'{self.time_window} {self.time_unit}',
                    'overlap': f'{self.overlap} {self.time_unit}',
                    'created_by': 'Spliter',
                    'creation_time': datetime.now().isoformat()
                })
                
                # 保存为netCDF4格式
                self._save_to_netcdf4(window_data, output_path)
                
                output_files.append(output_path)
                self.logger.info(f"窗口 {i+1} 保存成功: {output_filename}")
                self.logger.info(f"  时间范围: {start_time} - {end_time}")
                self.logger.info(f"  数据点数: {len(window_data.time)}")
                
            except Exception as e:
                self.logger.error(f"处理时间窗口 {i+1} 失败: {str(e)}")
                continue
        
        return output_files

    def _save_to_netcdf4(self, dataset: xr.Dataset, output_path: str):
        """保存数据集为netCDF4格式"""
        try:
            # 设置编码参数以优化netCDF4格式
            encoding = {}
            for var in dataset.data_vars:
                encoding[var] = {
                    'zlib': True,  # 启用压缩
                    'complevel': 4,  # 压缩级别
                    'shuffle': True,  # 启用shuffle filter
                    'fletcher32': False,  # 校验和
                }
            
            # 为坐标变量设置编码
            for coord in dataset.coords:
                if coord not in encoding:
                    encoding[coord] = {'zlib': True, 'complevel': 4}
            
            dataset.to_netcdf(
                output_path,
                format='NETCDF4',
                engine='netcdf4',
                encoding=encoding
            )
            
        except Exception as e:
            self.logger.error(f"保存netCDF4文件失败 {output_path}: {str(e)}")
            raise

    def split_data(self, file_pattern: Optional[str] = None) -> List[str]:
        """
        执行数据切分
        
        Args:
            file_pattern: 文件名模式过滤器，如 '*sfc*' 只处理包含sfc的文件
            
        Returns:
            List[str]: 输出文件列表
        """
        self.logger.info("=" * 50)
        self.logger.info("开始执行数据切分任务")
        
        input_files = self._get_input_files()
        if not input_files:
            self.logger.error("未找到输入文件")
            return []
        
        # 应用文件模式过滤
        if file_pattern:
            import fnmatch
            input_files = [f for f in input_files if fnmatch.fnmatch(os.path.basename(f), file_pattern)]
            self.logger.info(f"应用文件模式 '{file_pattern}' 后，剩余 {len(input_files)} 个文件")
        
        all_output_files = []
        
        for file_path in input_files:
            try:
                self.logger.info(f"处理文件: {os.path.basename(file_path)}")
                
                # 加载数据集
                dataset = self._load_dataset(file_path)
                if dataset is None:
                    continue
                
                # 获取时间范围
                start_time = pd.to_datetime(dataset.time.min().values)
                end_time = pd.to_datetime(dataset.time.max().values)
                
                # 生成时间窗口
                windows = self._generate_time_windows(start_time, end_time)
                if not windows:
                    self.logger.warning(f"未生成有效时间窗口: {os.path.basename(file_path)}")
                    continue
                
                # 获取基础文件名
                base_filename = os.path.splitext(os.path.basename(file_path))[0]
                
                # 切分数据
                output_files = self._split_dataset(dataset, windows, base_filename)
                all_output_files.extend(output_files)
                
                # 关闭数据集
                dataset.close()
                
                self.logger.info(f"文件 {os.path.basename(file_path)} 处理完成，生成 {len(output_files)} 个切分文件")
                
            except Exception as e:
                self.logger.error(f"处理文件失败 {os.path.basename(file_path)}: {str(e)}")
                continue
        
        self.logger.info("=" * 50)
        self.logger.info(f"数据切分任务完成")
        self.logger.info(f"处理了 {len(input_files)} 个输入文件")
        self.logger.info(f"生成了 {len(all_output_files)} 个输出文件")
        self.logger.info("=" * 50)
        
        return all_output_files

    def get_split_summary(self) -> dict:
        """获取切分任务摘要信息"""
        output_files = []
        if os.path.exists(self.output_folder):
            for file in os.listdir(self.output_folder):
                if file.endswith('.nc'):
                    output_files.append(os.path.join(self.output_folder, file))
        
        summary = {
            'total_output_files': len(output_files),
            'output_folder': self.output_folder,
            'time_window': f"{self.time_window} {self.time_unit}",
            'overlap': f"{self.overlap} {self.time_unit}",
            'output_files': [os.path.basename(f) for f in output_files]
        }
        
        return summary

    def validate_split_results(self) -> bool:
        """验证切分结果的完整性"""
        try:
            output_files = []
            if os.path.exists(self.output_folder):
                for file in os.listdir(self.output_folder):
                    if file.endswith('.nc'):
                        output_files.append(os.path.join(self.output_folder, file))
            
            if not output_files:
                self.logger.warning("未找到输出文件进行验证")
                return False
            
            valid_count = 0
            for file_path in output_files:
                try:
                    with xr.open_dataset(file_path) as ds:
                        # 检查基本属性
                        if 'time' in ds.dims and len(ds.time) > 0:
                            valid_count += 1
                        else:
                            self.logger.warning(f"文件验证失败: {os.path.basename(file_path)}")
                except Exception as e:
                    self.logger.error(f"文件验证异常 {os.path.basename(file_path)}: {str(e)}")
            
            success_rate = valid_count / len(output_files)
            self.logger.info(f"验证完成: {valid_count}/{len(output_files)} 个文件有效 ({success_rate:.1%})")
            
            return success_rate > 0.9  # 90%以上文件有效认为验证通过
            
        except Exception as e:
            self.logger.error(f"验证过程出错: {str(e)}")
            return False