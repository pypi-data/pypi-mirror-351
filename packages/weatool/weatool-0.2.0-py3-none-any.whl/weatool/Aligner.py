import os
import logging
import xarray as xr
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

class Aligner(ABC):
    """
    数据对齐基类
    负责处理切分数据和预测结果的格式对齐、时间对齐和维度对齐
    需要继承此类实现具体的对齐逻辑
    """
    
    def __init__(self, split_data_folder: str, forecast_data_folder: str, output_folder: str):
        """
        初始化Aligner类
        
        Args:
            split_data_folder: 切分数据文件夹路径
            forecast_data_folder: 预测数据文件夹路径  
            output_folder: 输出文件夹路径
        """
        # 获取当前项目目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.split_data_folder = os.path.join(current_dir, split_data_folder)
        self.forecast_data_folder = os.path.join(current_dir, forecast_data_folder)
        self.output_folder = os.path.join(current_dir, output_folder)

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        

        self._setup_logging()
        
        self.logger.info(f"Aligner初始化完成")
        self.logger.info(f"切分数据目录: {self.split_data_folder}")
        self.logger.info(f"预测数据目录: {self.forecast_data_folder}")
        self.logger.info(f"输出目录: {self.output_folder}")

    def _setup_logging(self):
        """设置日志配置"""
        logs_dir = os.path.join(self.output_folder, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"aligner_{timestamp}.log"
        log_filepath = os.path.join(logs_dir, log_filename)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.logger = logging.getLogger('Aligner')
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

    def find_data_pairs(self) -> List[Tuple[str, str]]:
        """
        查找匹配的数据对
        
        Returns:
            List[Tuple[str, str]]: (切分数据文件路径, 预测数据文件路径) 的列表
        """
        
        split_files = []
        if os.path.exists(self.split_data_folder):
            for file in os.listdir(self.split_data_folder):
                if file.endswith('.nc'):
                    split_files.append(file)
        

        forecast_files = []
        if os.path.exists(self.forecast_data_folder):
            for file in os.listdir(self.forecast_data_folder):
                if file.endswith('.nc') and '_forecast' in file:
                    forecast_files.append(file)
        
        pairs = []
        for split_file in split_files:
            split_base = split_file.replace('.nc', '')
            for forecast_file in forecast_files:
                if split_base in forecast_file:
                    split_path = os.path.join(self.split_data_folder, split_file)
                    forecast_path = os.path.join(self.forecast_data_folder, forecast_file)
                    pairs.append((split_path, forecast_path))
                    break
        
        self.logger.info(f"找到 {len(pairs)} 对匹配的数据文件")
        return pairs

    @abstractmethod
    def align_time_dimension(self, split_data: xr.Dataset, forecast_data: xr.Dataset) -> Tuple[xr.Dataset, xr.Dataset]:
        """
        实现：时间维度对齐
        
        Args:
            split_data: 切分数据
            forecast_data: 预测数据
            
        Returns:
            Tuple[xr.Dataset, xr.Dataset]: 时间对齐后的 (切分数据, 预测数据)
        """
        pass

    @abstractmethod  
    def align_spatial_dimension(self, split_data: xr.Dataset, forecast_data: xr.Dataset) -> Tuple[xr.Dataset, xr.Dataset]:
        """
        实现：空间维度对齐
        
        Args:
            split_data: 切分数据
            forecast_data: 预测数据
            
        Returns:
            Tuple[xr.Dataset, xr.Dataset]: 空间对齐后的 (切分数据, 预测数据)
        """
        pass

    @abstractmethod
    def align_variables(self, split_data: xr.Dataset, forecast_data: xr.Dataset) -> Tuple[xr.Dataset, xr.Dataset]:
        """
        实现：变量维度对齐
        
        Args:
            split_data: 切分数据
            forecast_data: 预测数据
            
        Returns:
            Tuple[xr.Dataset, xr.Dataset]: 变量对齐后的 (切分数据, 预测数据)
        """
        pass

    @abstractmethod
    def save_aligned_data(self, split_data: xr.Dataset, forecast_data: xr.Dataset, 
                         output_split_path: str, output_forecast_path: str):
        """
        实现：保存对齐后的数据
        
        Args:
            split_data: 对齐后的切分数据
            forecast_data: 对齐后的预测数据
            output_split_path: 切分数据输出路径
            output_forecast_path: 预测数据输出路径
        """
        pass

    def align_single_pair(self, split_file: str, forecast_file: str) -> bool:
        """
        对齐单个数据对
        
        Args:
            split_file: 切分数据文件路径
            forecast_file: 预测数据文件路径
            
        Returns:
            bool: 对齐是否成功
        """
        try:
            self.logger.info(f"开始对齐: {os.path.basename(split_file)} <-> {os.path.basename(forecast_file)}")
            
            split_data = xr.open_dataset(split_file)
            forecast_data = xr.open_dataset(forecast_file)
            
            # 执行对齐步骤
            split_data, forecast_data = self.align_time_dimension(split_data, forecast_data)
            split_data, forecast_data = self.align_spatial_dimension(split_data, forecast_data) 
            split_data, forecast_data = self.align_variables(split_data, forecast_data)
            
            # 生成输出文件名
            split_base = os.path.splitext(os.path.basename(split_file))[0]
            forecast_base = os.path.splitext(os.path.basename(forecast_file))[0]
            
            output_split_path = os.path.join(self.output_folder, f"{split_base}_aligned.nc")
            output_forecast_path = os.path.join(self.output_folder, f"{forecast_base}_aligned.nc")
            
            self.save_aligned_data(split_data, forecast_data, output_split_path, output_forecast_path)
            
            # 关闭数据集
            split_data.close()
            forecast_data.close()
            
            self.logger.info(f"对齐完成: {os.path.basename(split_file)}")
            return True
            
        except Exception as e:
            self.logger.error(f"对齐失败 {os.path.basename(split_file)}: {str(e)}")
            return False

    def align_all_data(self) -> Dict[str, int]:
        """
        对齐所有数据
        
        Returns:
            Dict[str, int]: 包含成功和失败数量的统计信息
        """
        self.logger.info("=" * 50)
        self.logger.info("开始数据对齐任务")
        
        # 查找数据对
        data_pairs = self.find_data_pairs()
        if not data_pairs:
            self.logger.error("未找到匹配的数据对")
            return {'total': 0, 'success': 0, 'failed': 0}
        
        success_count = 0
        failed_count = 0
        
        for i, (split_file, forecast_file) in enumerate(data_pairs, 1):
            self.logger.info(f"处理进度: {i}/{len(data_pairs)}")
            
            if self.align_single_pair(split_file, forecast_file):
                success_count += 1
            else:
                failed_count += 1
        
        # 记录统计信息
        self.logger.info("=" * 50)
        self.logger.info(f"数据对齐任务完成")
        self.logger.info(f"处理数据对: {len(data_pairs)}")
        self.logger.info(f"成功对齐: {success_count}")
        self.logger.info(f"失败数量: {failed_count}")
        self.logger.info(f"成功率: {success_count/len(data_pairs):.1%}")
        self.logger.info("=" * 50)
        
        return {
            'total': len(data_pairs),
            'success': success_count, 
            'failed': failed_count
        }


