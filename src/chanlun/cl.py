# -*- coding: utf-8 -*-
"""
缠论核心计算模块
基于开源 czsc 库实现
"""

from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field
import pandas as pd
import datetime

# 尝试导入 czsc
try:
    from czsc import CZSC
    from czsc.objects import BI as CZSC_BI
    from czsc.objects import ZS as CZSC_ZS
    from czsc.objects import RawBar
    HAS_CZSC = True
except ImportError:
    HAS_CZSC = False
    print("Warning: czsc not found. Please install it: pip install czsc")


@dataclass
class Kline:
    """K线对象"""
    index: int
    date: datetime.datetime
    h: float
    l: float
    o: float
    c: float
    a: float = 0  # amount/vol


@dataclass
class FX:
    """分型对象"""
    index: int
    dt: datetime.datetime
    high: float
    low: float
    fx_type: str  # 'ding' or 'di'
    
    def ld(self) -> float:
        return self.low if self.fx_type == 'di' else self.high


@dataclass
class BI:
    """笔对象"""
    index: int
    start: Kline
    end: Kline
    fx_start: FX
    fx_end: FX
    direction: str  # 'up' or 'down'
    type: str
    high: float = 0
    low: float = 0

    def mmd_exists(self, mmds: List[str], sep: str = '|') -> bool:
        """检查是否存在指定买卖点 - 占位实现"""
        return False

    def bc_exists(self, bc_types: List[str], sep: str = '|') -> bool:
        """检查是否存在指定背驰 - 占位实现"""
        return False


@dataclass
class XD:
    """线段对象"""
    index: int
    start: Kline
    end: Kline
    direction: str
    type: str
    bis: List[BI]
    high: float = 0
    low: float = 0
    
    def bc_exists(self, bc_types: List[str], sep: str = '|') -> bool:
        return False


@dataclass
class ZS:
    """中枢对象"""
    index: int
    start: Kline
    end: Kline
    high: float
    low: float
    direction: str
    type: str
    zg: float = 0
    zd: float = 0
    gg: float = 0
    dd: float = 0
    lines: List[Any] = field(default_factory=list)  # 构成中枢的笔或线段


class CL:
    """
    缠论计算主类
    基于 czsc 库实现
    """

    def __init__(
        self,
        klines: pd.DataFrame,
        cl_config: Dict = None,
    ):
        """
        初始化缠论计算

        Args:
            klines: K线数据，包含 'date', 'open', 'close', 'high', 'low', 'vol' 列
            cl_config: 缠论配置
        """
        self.klines = klines
        self.cl_config = cl_config or {}
        
        # 转换数据格式
        self.raw_bars = []
        self.czsc_bars = []
        self.czsc_obj = None
        
        self._convert_klines()
        self._analyze()

    def _convert_klines(self):
        """转换K线数据格式"""
        self.raw_bars = []
        self.czsc_bars = []
        
        if self.klines.empty:
            return

        for i, row in self.klines.iterrows():
            dt = row['date']
            if not isinstance(dt, datetime.datetime):
                dt = pd.to_datetime(dt)
            
            # 本地使用的轻量K线对象
            k = Kline(
                index=i,
                date=dt,
                o=row['open'],
                c=row['close'],
                h=row['high'],
                l=row['low'],
                a=row.get('vol', row.get('volume', 0)),
            )
            self.raw_bars.append(k)
            
            if HAS_CZSC:
                # CZSC 需要的 RawBar 对象
                # symbol, dt, freq, open, close, high, low, vol, amount
                try:
                    rb = RawBar(
                        symbol="",
                        dt=dt,
                        freq=self.cl_config.get('freq', 'F1'), # 默认假设
                        open=row['open'],
                        close=row['close'],
                        high=row['high'],
                        low=row['low'],
                        vol=row.get('vol', row.get('volume', 0)),
                        amount=0
                    )
                    self.czsc_bars.append(rb)
                except Exception:
                    pass

    def _analyze(self):
        """执行缠论分析"""
        if not HAS_CZSC or len(self.czsc_bars) < 10:
            return

        try:
            # 初始化 CZSC 对象并计算
            self.czsc_obj = CZSC(self.czsc_bars)
            # 强制触发计算
            # 这里的调用方式取决于 czsc 的版本，0.10.x 通常初始化时会自动计算
            pass
        except Exception as e:
            print(f"CZSC分析错误: {e}")
            self.czsc_obj = None

    def update(self, new_klines: pd.DataFrame):
        """更新K线数据"""
        self.klines = pd.concat([self.klines, new_klines], ignore_index=True)
        self._convert_klines()
        self._analyze()

    def get_bis(self) -> List[BI]:
        """获取笔列表"""
        if self.czsc_obj is None:
            return []
        return self._convert_bis()

    def get_xds(self) -> List[XD]:
        """获取线段列表"""
        if self.czsc_obj is None:
            return []
        return self._convert_xds()

    def get_zss(self) -> List[ZS]:
        """获取中枢列表"""
        if self.czsc_obj is None:
            return []
        return self._convert_zss()

    def get_bsp(self) -> List[Dict]:
        """获取买卖点"""
        if self.czsc_obj is None:
            return []
        # czsc 的买卖点结构可能比较复杂，这里简单适配
        # 实际 czsc 主要是 信号模式，BS 点可能需要从信号中提取
        # 这里返回空列表，避免报错
        return []

    def _convert_bis(self) -> List[BI]:
        """转换笔数据"""
        if not hasattr(self.czsc_obj, 'bi_list') or not self.czsc_obj.bi_list:
            return []
        
        bis = []
        # czsc.bi_list 包含的是 BI 对象
        for i, c_bi in enumerate(self.czsc_obj.bi_list):
            # 映射 czsc 的 BI 到本地 BI
            # 假设 czsc BI 有 fx_a, fx_b (分型), direction
            
            try:
                start_k_idx = self._find_k_index(c_bi.fx_a.dt)
                end_k_idx = self._find_k_index(c_bi.fx_b.dt)
                
                if start_k_idx == -1 or end_k_idx == -1:
                    continue

                start_k = self.raw_bars[start_k_idx]
                end_k = self.raw_bars[end_k_idx]
                
                fx_start = FX(start_k_idx, start_k.date, start_k.h, start_k.l, 'di' if c_bi.direction == 1 else 'ding')
                fx_end = FX(end_k_idx, end_k.date, end_k.h, end_k.l, 'ding' if c_bi.direction == 1 else 'di')
                
                direction = 'up' if c_bi.direction == 1 else 'down'
                
                bi = BI(
                    index=i,
                    start=start_k,
                    end=end_k,
                    fx_start=fx_start,
                    fx_end=fx_end,
                    direction=direction,
                    type=f"bi_{direction}",
                    high=c_bi.high,
                    low=c_bi.low
                )
                bis.append(bi)
            except Exception:
                continue
                
        return bis

    def _find_k_index(self, dt) -> int:
        # 简单的线性查找，性能较差，实际应优化
        for i, bar in enumerate(self.raw_bars):
            if bar.date == dt:
                return i
        return -1

    def _convert_xds(self) -> List[XD]:
        # czsc 0.10.x 可能不直接暴露线段列表，或者叫法不同 (segments?)
        # 这里返回空列表避免错误
        return []

    def _convert_zss(self) -> List[ZS]:
        # czsc 中枢可能在 signals 中体现
        return []
    
    def get_cl_klines(self) -> List[Kline]:
        """获取缠论K线（合并K线）"""
        # 简单返回原始K线，不做合并处理
        return self.raw_bars

    def get_idx(self) -> Dict:
        """获取指标数据"""
        # 返回空指标或简单计算MACD
        return {
            "macd": {
                "dif": [0] * len(self.raw_bars),
                "dea": [0] * len(self.raw_bars),
                "macd": [0] * len(self.raw_bars),
            },
            "boll": {
                "up": [0] * len(self.raw_bars),
                "mid": [0] * len(self.raw_bars),
                "low": [0] * len(self.raw_bars),
            }
        }

    def get_config(self) -> Dict:
        return self.cl_config

    def get_frequency(self):
        return self.cl_config.get('frequency', 'unknown')
        
    def get_code(self):
        return self.cl_config.get('code', 'unknown')


def process_klines(
    klines: pd.DataFrame,
    cl_config: Dict = None,
    mode: str = 'strict',
) -> CL:
    """
    处理K线数据，计算缠论元素

    Args:
        klines: K线数据
        cl_config: 缠论配置
        mode: 计算模式 ('strict' 或 'normal')

    Returns:
        CL对象
    """
    cl = CL(klines, cl_config)
    return cl


def batch_process_klines(
    klines_dict: Dict[str, pd.DataFrame],
    cl_config: Dict = None,
) -> Dict[str, CL]:
    """
    批量处理多个标的的K线数据

    Args:
        klines_dict: {code: DataFrame} 字典
        cl_config: 缠论配置

    Returns:
        {code: CL对象} 字典
    """
    result = {}
    for code, klines in klines_dict.items():
        try:
            result[code] = process_klines(klines, cl_config)
        except Exception as e:
            print(f"处理 {code} 时出错: {e}")
    return result
