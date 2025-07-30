import os
import logging
import numpy as np
import xarray as xr
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple
import pickle
import json
from contextlib import contextmanager

class BaseWeatherModel(ABC):
    """气象模型基类，需要继承此类实现具体模型"""
    
    @abstractmethod
    def load_model(self, model_path: str, **kwargs) -> Any:
        """
        加载气象模型
        
        Args:
            model_path: 模型文件路径
            **kwargs: 其他模型加载参数
            
        Returns:
            加载的模型对象
        """
        pass
    
    @abstractmethod
    def preprocess_data(self, input_data: xr.Dataset) -> Any:
        """
        数据预处理
        
        Args:
            input_data: 输入数据
            
        Returns:
            预处理后的数据
        """
        pass
    
    @abstractmethod
    def predict(self, model: Any, processed_data: Any, **kwargs) -> Any:
        """
        执行预测
        
        Args:
            model: 加载的模型
            processed_data: 预处理后的数据
            **kwargs: 预测参数
            
        Returns:
            预测结果
        """
        pass
    
    @abstractmethod
    def postprocess_result(self, prediction: Any, input_data: xr.Dataset) -> xr.Dataset:
        """
        结果后处理
        
        Args:
            prediction: 原始预测结果
            input_data: 原始输入数据（用于获取坐标信息等）
            
        Returns:
            标准化的预测结果（xarray.Dataset格式）
        """
        pass


class ModelParameterManager:
    """模型参数管理器，负责参数冻结和解冻"""
    
    def __init__(self):
        self.frozen_models = {}
        self.original_states = {}
    
    def freeze_model_parameters(self, model: Any, model_id: str = None) -> str:
        """
        冻结模型参数
        
        Args:
            model: 要冻结的模型
            model_id: 模型标识符，如果不提供则自动生成
            
        Returns:
            str: 模型标识符
        """
        if model_id is None:
            model_id = f"model_{len(self.frozen_models)}"
        
        # 检查是否为PyTorch模型
        if hasattr(model, 'parameters'):
            original_requires_grad = {}
            for name, param in model.named_parameters():
                original_requires_grad[name] = param.requires_grad
                param.requires_grad = False
            
            self.original_states[model_id] = original_requires_grad
            self.frozen_models[model_id] = model
            if hasattr(model, 'eval'):
                model.eval()
        return model_id
    
    def unfreeze_model_parameters(self, model_id: str):
        """解冻模型参数"""
        if model_id not in self.frozen_models:
            raise ValueError(f"模型 {model_id} 未找到或未被冻结")
        
        model = self.frozen_models[model_id]
        original_state = self.original_states[model_id]
        if hasattr(model, 'parameters') and isinstance(original_state, dict):
            for name, param in model.named_parameters():
                if name in original_state:
                    param.requires_grad = original_state[name]
        
        # 清理记录
        del self.frozen_models[model_id]
        del self.original_states[model_id]
    
    def is_frozen(self, model_id: str) -> bool:
        """检查模型是否已冻结"""
        return model_id in self.frozen_models
    
    def get_frozen_models(self) -> List[str]:
        """获取所有已冻结的模型ID"""
        return list(self.frozen_models.keys())


class Forecast:
    """气象预测模块"""
    
    def __init__(self, input_folder: str, output_folder: str, model_adapter: BaseWeatherModel,
                 model_path: str, batch_size: int = 1, device: str = 'auto'):
        """
        初始化Forecast类
        
        Args:
            input_folder: 输入数据文件夹（切分后的数据）
            output_folder: 输出结果文件夹
            model_adapter: 模型适配器实例
            model_path: 模型文件路径
            batch_size: 批处理大小
            device: 计算设备 ('cpu', 'cuda', 'auto')
        """
        # 获取当前项目目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_folder = os.path.join(current_dir, input_folder)
        self.output_folder = os.path.join(current_dir, output_folder)
        
        # 创建输出目录
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        

        self.model_adapter = model_adapter
        self.model_path = model_path
        self.model = None
        self.model_id = None
        self.param_manager = ModelParameterManager()
        self.batch_size = batch_size
        self.device = self._setup_device(device)
        self.prediction_cache = {}
        self._setup_logging()
        self.logger.info(f"Forecast模块初始化完成")
        self.logger.info(f"输入目录: {self.input_folder}")
        self.logger.info(f"输出目录: {self.output_folder}")
        self.logger.info(f"模型路径: {model_path}")
        self.logger.info(f"计算设备: {self.device}")
        self.logger.info(f"批处理大小: {batch_size}")

    def _setup_logging(self):
        """设置日志配置"""
        logs_dir = os.path.join(self.output_folder, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"forecast_{timestamp}.log"
        log_filepath = os.path.join(logs_dir, log_filename)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.logger = logging.getLogger('Forecast')
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



    @contextmanager
    def _frozen_model_context(self):
        """冻结模型参数的上下文管理器"""
        if self.model is not None and self.model_id is None:
            # 冻结参数
            self.model_id = self.param_manager.freeze_model_parameters(self.model)
            self.logger.info(f"模型参数已冻结 (ID: {self.model_id})")
        
        try:
            yield
        finally:
            pass

    def load_model(self, **kwargs) -> bool:
        """
        加载气象预测模型
        
        Args:
            **kwargs: 传递给模型适配器的参数
            
        Returns:
            bool: 加载是否成功
        """
        try:
            self.logger.info("开始加载气象预测模型...")
            
            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                self.logger.error(f"模型文件不存在: {self.model_path}")
                return False
            
            self.model = self.model_adapter.load_model(self.model_path, **kwargs)
            
            if self.model is None:
                self.logger.error("模型加载失败")
                return False
            
            # 冻结模型参数
            self.model_id = self.param_manager.freeze_model_parameters(self.model)
            
            self.logger.info(f"模型加载成功，参数已冻结 (ID: {self.model_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"模型加载异常: {str(e)}")
            return False

    def _get_input_files(self) -> List[str]:
        """获取输入文件列表"""
        files = []
        if not os.path.exists(self.input_folder):
            self.logger.error(f"输入目录不存在: {self.input_folder}")
            return files
        
        for file in os.listdir(self.input_folder):
            if file.endswith('.nc'):
                files.append(os.path.join(self.input_folder, file))
        
        files.sort()
        self.logger.info(f"找到 {len(files)} 个输入文件")
        return files

    def _load_input_data(self, file_path: str) -> Optional[xr.Dataset]:
        """加载输入数据"""
        try:
            self.logger.debug(f"加载输入文件: {os.path.basename(file_path)}")
            dataset = xr.open_dataset(file_path)
            return dataset
        except Exception as e:
            self.logger.error(f"加载输入文件失败 {file_path}: {str(e)}")
            return None

    def _save_prediction_result(self, prediction: xr.Dataset, input_file: str, 
                               output_suffix: str = "_forecast") -> str:
        """
        保存预测结果
        
        Args:
            prediction: 预测结果
            input_file: 输入文件路径
            output_suffix: 输出文件后缀
            
        Returns:
            str: 输出文件路径
        """
        try:
            # 生成输出文件名
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_filename = f"{base_name}{output_suffix}.nc"
            output_path = os.path.join(self.output_folder, output_filename)
            
            # 添加预测元数据
            prediction.attrs.update({
                'prediction_model': str(type(self.model_adapter).__name__),
                'prediction_time': datetime.now().isoformat(),
                'input_file': os.path.basename(input_file),
                'device': self.device,
                'model_frozen': self.param_manager.is_frozen(self.model_id) if self.model_id else False
            })
            
            # 保存为netCDF格式
            prediction.to_netcdf(output_path, format='NETCDF4')
            
            self.logger.info(f"预测结果已保存: {output_filename}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"保存预测结果失败: {str(e)}")
            raise

    def predict_single_file(self, input_file: str, **predict_kwargs) -> Optional[str]:
        """
        对单个文件进行预测
        
        Args:
            input_file: 输入文件路径
            **predict_kwargs: 传递给预测函数的参数
            
        Returns:
            Optional[str]: 输出文件路径，失败时返回None
        """
        if self.model is None:
            self.logger.error("模型未加载，请先调用load_model()")
            return None
        
        try:
            self.logger.info(f"开始预测: {os.path.basename(input_file)}")
            
            
            input_data = self._load_input_data(input_file)
            if input_data is None:
                return None
            
            with self._frozen_model_context():
                processed_data = self.model_adapter.preprocess_data(input_data)
                # 执行预测
                raw_prediction = self.model_adapter.predict(
                    self.model, processed_data, **predict_kwargs
                )
                prediction_dataset = self.model_adapter.postprocess_result(
                    raw_prediction, input_data
                )
            output_path = self._save_prediction_result(prediction_dataset, input_file)
            input_data.close()
            if hasattr(prediction_dataset, 'close'):
                prediction_dataset.close()
            
            self.logger.info(f"文件预测完成: {os.path.basename(input_file)}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"预测失败 {os.path.basename(input_file)}: {str(e)}")
            return None

   
