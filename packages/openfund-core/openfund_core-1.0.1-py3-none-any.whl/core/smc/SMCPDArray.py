import logging
import pandas as pd

from core.smc.SMCFVG import SMCFVG
from core.smc.SMCOrderBlock import SMCOrderBlock

class SMCPDArray(SMCFVG,SMCOrderBlock):
    PD_HIGH_COL = "pd_high"
    PD_LOW_COL = "pd_low"
    PD_MID_COL = "pd_mid"
    PD_TYPE_COL = "pd_type"

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def find_PDArrays(
        self, struct: pd.DataFrame, side, start_index=-1
    ) -> pd.DataFrame:
        """_summary_
            寻找PDArrays,包括Fair Value Gap (FVG)|Order Block (OB)|Breaker Block(BB)|Mitigation Block(BB) 
        Args:
            data (pd.DataFrame): K线数据
            side (_type_): 交易方向 'buy'|'sell'
            threshold (_type_): 阈值价格，通常为溢价和折价区的CE
            check_balanced (bool): 是否检查FVG是否被平衡过,默认为True
            start_index (int): 开始查找索引的起点,默认为-1

        Returns:
            pd.DataFrame: _description_

        """
       
        df = (
            struct.copy()
            if start_index == -1
            else struct.copy().iloc[max(0, start_index - 1) :]
        )
        # check_columns = [self.HIGH_COL, self.LOW_COL, self.CLOSE_COL]
        # self.check_columns(df, check_columns)

        df_FVGs = self.find_FVGs(df, side)
        # self.logger.info(f"fvgs:\n{df_FVGs[['timestamp', self.FVG_SIDE, self.FVG_TOP, self.FVG_BOT, self.FVG_WAS_BALANCED]]}")


        df_OBs = self.find_OBs(df, side)
        # self.logger.info("find_OBs:\n %s", df_OBs)
        
        # 使用更简洁的方式重命名和合并时间戳列
        timestamp_mapping = {self.TIMESTAMP_COL: ['ts_OBs', 'ts_FVGs']}
        df_OBs = df_OBs.rename(columns={self.TIMESTAMP_COL: timestamp_mapping[self.TIMESTAMP_COL][0]})
        df_FVGs = df_FVGs.rename(columns={self.TIMESTAMP_COL: timestamp_mapping[self.TIMESTAMP_COL][1]})

        # 使用更高效的方式合并数据框
        df_PDArrays = pd.concat(
            [df_OBs, df_FVGs], 
            axis=1,
            join='outer'
        ).sort_index()

        # 使用更清晰的方式合并时间戳列
        df_PDArrays[self.TIMESTAMP_COL] = df_PDArrays[timestamp_mapping[self.TIMESTAMP_COL][0]].fillna(
            df_PDArrays[timestamp_mapping[self.TIMESTAMP_COL][1]]
        )
        df_PDArrays[self.PD_TYPE_COL] = df_PDArrays[[self.FVG_SIDE, self.OB_DIRECTION_COL]].apply(
            lambda x: 'FVG-OB' if pd.notna(x.iloc[0]) and pd.notna(x.iloc[1]) else 'FVG' if pd.notna(x.iloc[0]) else 'OB', axis=1
        )
     
        df_PDArrays.loc[:, self.PD_HIGH_COL] = df_PDArrays[[self.FVG_TOP, self.OB_HIGH_COL]].max(axis=1)
        df_PDArrays.loc[:, self.PD_LOW_COL] = df_PDArrays[[self.FVG_BOT, self.OB_LOW_COL]].min(axis=1)
        df_PDArrays.loc[:, self.PD_MID_COL] = (df_PDArrays[self.PD_HIGH_COL] + df_PDArrays[self.PD_LOW_COL]) / 2
        
        
        

        return df_PDArrays

