import cdsapi
import os
import logging
import time
from datetime import datetime

class Downloader:
    def __init__(self, folder: str, year: str, month: str, days: list[str], times: list[str]):
        # 获取当前项目目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.folder = os.path.join(current_dir, folder)
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        
        # 初始化日志
        self._setup_logging()
        
        self.param_sfc = [
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "2m_temperature",
            "surface_pressure",
            "mean_sea_level_pressure",
            "total_column_water_vapour",
            "100m_u_component_of_wind",
            "100m_v_component_of_wind",
            "sea_surface_temperature",
        ]
        self.param_level_pl = (
            [
                "temperature",
                "u_component_of_wind",
                "v_component_of_wind",
                "geopotential",
                "relative_humidity",
            ],
            [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50],
        )
        self.month = month
        self.days = days
        self.times = times
        self.year = year
        
        # 记录初始化信息
        self.logger.info(f"Downloader初始化完成 - 年份: {year}, 月份: {month}")
        self.logger.info(f"数据保存目录: {self.folder}")
        self.logger.info(f"下载天数: {len(days)}天, 时间点: {len(times)}个")

    def _setup_logging(self):
        """设置日志配置"""
        # 创建logs目录
        logs_dir = os.path.join(self.folder, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # 生成日志文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"downloader_{timestamp}.log"
        log_filepath = os.path.join(logs_dir, log_filename)
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 创建logger
        self.logger = logging.getLogger('Downloader')
        self.logger.setLevel(logging.INFO)
        
        self.logger.handlers.clear()
        
        # 文件处理器
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"日志系统初始化完成，日志文件: {log_filepath}")

    def start(self):
        """开始下载数据"""
        self.logger.info("=" * 50)
        self.logger.info("开始执行数据下载任务")
        start_time = time.time()
        
        sfc_list = []
        pl_list = []
        month_str = self.year + self.month
        sfc_path = os.path.join(self.folder, month_str + "_sfc.nc")
        pl_path = os.path.join(self.folder, month_str + "_pl.nc")
        
        datetime_params = {
            "year": self.year, 
            "month": self.month, 
            "day": self.days, 
            "time": self.times
        }
        
        retrieve_sfc = dict(
            format="netcdf",
            product_type="reanalysis",
            variable=self.param_sfc,
            **datetime_params,
        )
        
        retrieve_pl = dict(
            format="netcdf",
            product_type="reanalysis",
            variable=self.param_level_pl[0],
            pressure_level=self.param_level_pl[1],
            **datetime_params,
        )
        
        sfc_list.append((retrieve_sfc, sfc_path))
        pl_list.append((retrieve_pl, pl_path))

        # 记录下载参数
        self.logger.info(f"准备下载数据 - 文件前缀: {month_str}")
        self.logger.info(f"地面变量数量: {len(self.param_sfc)}")
        self.logger.info(f"等压面变量数量: {len(self.param_level_pl[0])}")
        self.logger.info(f"等压面层数: {len(self.param_level_pl[1])}")

        # 执行下载
        success_count = 0
        total_count = 2
        
        if self.download_data("reanalysis-era5-single-levels", retrieve_sfc, sfc_path):
            success_count += 1
            
        if self.download_data("reanalysis-era5-pressure-levels", retrieve_pl, pl_path):
            success_count += 1

        # 记录总结信息
        end_time = time.time()
        duration = end_time - start_time
        self.logger.info("=" * 50)
        self.logger.info(f"下载任务完成")
        self.logger.info(f"成功下载: {success_count}/{total_count} 个文件")
        self.logger.info(f"总耗时: {duration:.2f} 秒")
        self.logger.info("=" * 50)

    def download_data(self, product_name: str, request_params: dict, file_path: str) -> bool:
        """
        下载数据
        
        Args:
            product_name: 产品名称
            request_params: 请求参数
            file_path: 保存路径
            
        Returns:
            bool: 下载是否成功
        """
        file_name = os.path.basename(file_path)
        
        try:
            if not os.path.exists(file_path):
                self.logger.info(f"开始下载: {file_name}")
                self.logger.info(f"产品类型: {product_name}")
                self.logger.info(f"保存路径: {file_path}")
                
                # 记录请求参数
                self.logger.debug(f"请求参数: {request_params}")
                
                download_start_time = time.time()
                
                # 在函数内部创建 cdsapi.Client 实例
                api = cdsapi.Client(progress=False)
                
                self.logger.info(f"正在从CDS服务器下载 {file_name}...")
                api.retrieve(product_name, request_params, file_path)
                
                download_end_time = time.time()
                download_duration = download_end_time - download_start_time
                
                # 检查文件是否成功下载
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    file_size_mb = file_size / (1024 * 1024)
                    self.logger.info(f"下载成功: {file_name}")
                    self.logger.info(f"文件大小: {file_size_mb:.2f} MB")
                    self.logger.info(f"下载耗时: {download_duration:.2f} 秒")
                    return True
                else:
                    self.logger.error(f"下载失败: 文件未创建 - {file_name}")
                    return False
                    
            else:
                self.logger.info(f"文件已存在，跳过下载: {file_name}")
                file_size = os.path.getsize(file_path)
                file_size_mb = file_size / (1024 * 1024)
                self.logger.info(f"现有文件大小: {file_size_mb:.2f} MB")
                return True
                
        except Exception as e:
            self.logger.error(f"下载失败: {file_name}")
            self.logger.error(f"错误信息: {str(e)}")
            
            # 删除部分下载的文件
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    self.logger.info(f"已删除部分下载的文件: {file_name}")
                except Exception as remove_error:
                    self.logger.error(f"删除部分文件失败: {str(remove_error)}")
            
            return False

    def get_log_info(self):
        """获取日志信息"""
        log_files = []
        logs_dir = os.path.join(self.folder, 'logs')
        if os.path.exists(logs_dir):
            for file in os.listdir(logs_dir):
                if file.startswith('downloader_') and file.endswith('.log'):
                    log_files.append(os.path.join(logs_dir, file))
        
        return sorted(log_files, key=os.path.getmtime, reverse=True)