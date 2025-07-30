import logging
import time
import ccxt
import pandas as pd


from decimal import Decimal
from core.utils.OPTools import OPTools
from ccxt.base.exchange import ConstructorArgs


class Exchange:
    def __init__(self, config:ConstructorArgs, exchangeKey:str = "okx",) :
        # 配置交易所
        self.exchange = getattr(ccxt, exchangeKey)(config)
        self.logger = logging.getLogger(__name__)



    def getMarket(self, symbol:str):
        # 配置交易对
        self.exchange.load_markets()
        
        return self.exchange.market(symbol)

    def get_tick_size(self,symbol) -> Decimal:     
        
        market = self.getMarket(symbol)
        if market and 'precision' in market and 'price' in market['precision']:            
            return OPTools.toDecimal(market['precision']['price'])
        else:
            raise ValueError(f"{symbol}: 无法从市场数据中获取价格精度")

    def amount_to_precision(self,symbol, contract_size):
        return self.exchange.amount_to_precision(symbol, contract_size)
    
    def get_position_mode(self):
    
        try:
            # 假设获取账户持仓模式的 API
            response = self.exchange.private_get_account_config()
            data = response.get('data', [])
            if data and isinstance(data, list):
                # 取列表的第一个元素（假设它是一个字典），然后获取 'posMode'
                position_mode = data[0].get('posMode', 'single')  # 默认值为单向
                
                return position_mode
            else:
               
                return 'single'  # 返回默认值
        except Exception as e:        
            error_message = f"Error fetching position mode: {e}"
            self.logger.error(error_message)        
            raise Exception(error_message)  
    
    def set_leverage(self,symbol, leverage, mgnMode='isolated',posSide=None):
        try:
            # 设置杠杆
            params = {
                # 'instId': instId,
                'leverage': leverage,
                'marginMode': mgnMode
            }
            if posSide:
                params['side'] = posSide
                
            self.exchange.set_leverage(leverage, symbol=symbol, params=params)
            self.logger.info(f"{symbol} Successfully set leverage to {leverage}x")
        except Exception as e:
            error_message = f"{symbol} Error setting leverage: {e}"
            self.logger.error(error_message)        
            raise Exception(error_message)  
    # 获取价格精度
    def get_precision_length(self,symbol) -> int:
        tick_size = self.get_tick_size(symbol)
        return len(f"{tick_size:.15f}".rstrip('0').split('.')[1]) if '.' in f"{tick_size:.15f}" else 0

    def format_price(self, symbol, price:Decimal) -> str:
        precision = self.get_precision_length(symbol)
        return f"{price:.{precision}f}"
    
    def convert_contract(self, symbol, amount, price:Decimal, direction='cost_to_contract'):
        """
        进行合约与币的转换
        :param symbol: 交易对符号，如 'BTC/USDT:USDT'
        :param amount: 输入的数量，可以是合约数量或币的数量
        :param direction: 转换方向，'amount_to_contract' 表示从数量转换为合约，'cost_to_contract' 表示从金额转换为合约
        :return: 转换后的数量
        """

        # 获取合约规模
        market_contractSize = OPTools.toDecimal(self.getMarket(symbol)['contractSize'])
        amount = OPTools.toDecimal(amount)
        if direction == 'amount_to_contract':
            contract_size = amount / market_contractSize
        elif direction == 'cost_to_contract':
            contract_size = amount / price / market_contractSize
        else:
            raise Exception(f"{symbol}:{direction} 是无效的转换方向，请输入 'amount_to_contract' 或 'cost_to_contract'。")
        
        return self.amount_to_precision(symbol, contract_size)
   
     
    def cancel_all_orders(self, symbol):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 获取所有未完成订单
                params = {
                    # 'instId': instId
                }
                open_orders = self.exchange.fetch_open_orders(symbol=symbol, params=params)
                
                # 批量取消所有订单
                if open_orders:
                    order_ids = [order['id'] for order in open_orders]
                    self.exchange.cancel_orders(order_ids, symbol, params=params)
                    
                    self.logger.debug(f"{symbol}: {order_ids} 挂单取消成功.")
                else:
                    self.logger.debug(f"{symbol}: 无挂单.")
                return True
                
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_message = f"{symbol} 取消挂单失败(重试{retry_count}次): {str(e)}"
                    self.logger.error(error_message)
                    raise Exception(error_message)                
                else:
                    self.logger.warning(f"{symbol} 取消挂单失败，正在进行第{retry_count}次重试: {str(e)}")
                    time.sleep(0.1)  # 重试前等待0.1秒


    def place_order(self, symbol, price: Decimal, amount_usdt,  side, leverage=20, order_type='limit'): 
        """
        下单
        Args:
            symbol: 交易对
            price: 下单价格
            amount_usdt: 下单金额
            side: 下单方向
            order_type: 订单类型
        """       
        # 格式化价格
        adjusted_price = self.format_price(symbol, price)

        if amount_usdt > 0:
            if side == 'buy':
                pos_side = 'long' 
            else:
                pos_side = 'short'   
            # 设置杠杆 
            self.set_leverage(symbol=symbol, leverage=leverage, mgnMode='isolated',posSide=pos_side)  
            # 20250220 SWAP类型计算合约数量 
            contract_size = self.convert_contract(symbol=symbol, price = OPTools.toDecimal(adjusted_price) ,amount=amount_usdt)
    
            params = {
                
                "tdMode": 'isolated',
                "side": side,
                "ordType": order_type,
                "sz": contract_size,
                "px": adjusted_price
            } 
            
            # # 模拟盘(demo_trading)需要 posSide
            # if self.is_demo_trading == 1 :
            #     params["posSide"] = pos_side
                
            # self.logger.debug(f"---- Order placed params: {params}")
            try:
                order = {
                    'symbol': symbol,
                    'side': side,
                    'type': 'limit',
                    'amount': contract_size,
                    'price': adjusted_price,
                    'params': params
                }
                # 使用ccxt创建订单
                self.logger.debug(f"Pre Order placed:  {order} ")
                order_result = self.exchange.create_order(
                    **order
                    # symbol=symbol,
                    # type='limit',
                    # side=side,
                    # amount=amount_usdt,
                    # price=float(adjusted_price),
                    # params=params
                )
                # self.logger.debug(f"{symbol} ++ Order placed rs :  {order_result}")
            except Exception as e:
                error_message = f"{symbol} Failed to place order: {e}"
                self.logger.error(error_message)
                raise Exception(error_message)
                
        self.logger.debug(f"--------- ++ {symbol} Order placed done! --------")  
      
    def fetch_position(self, symbol):
        """_summary_

        Args:
            symbol (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                position = self.exchange.fetch_position(symbol=symbol)
                if position and position['contracts'] > 0:
                    self.logger.debug(f"{symbol} 有持仓合约数: {position['contracts']}")
                    return position
                return None
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_message = f"!!{symbol} 获取持仓失败(重试{retry_count}次): {str(e)}"
                    self.logger.error(error_message)
                    raise Exception(error_message)
                   
                self.logger.warning(f"{symbol} 检查持仓失败，正在进行第{retry_count}次重试: {str(e)}")
                time.sleep(0.1)  # 重试前等待0.1秒
      
            
    def get_historical_klines(self, symbol, bar='15m', limit=300, after:str=None, params={}):
        """
        获取历史K线数据
        Args:
            symbol: 交易对
            bar: K线周期
            limit: 数据条数
            after: 之后时间，格式为 "2025-05-21 23:00:00+08:00"
        """
           
        params = {
            **params,
            # 'instId': instId,
        }
        since = None
        if after:
            since = self.exchange.parse8601(after)
            limit = None
            if since:
                params['paginate'] = True
            
        klines = self.exchange.fetch_ohlcv(symbol, timeframe=bar,since=since, limit=limit, params=params)
        # if 'data' in response and len(response['data']) > 0:
        if klines :
            # return response['data']
            return klines
        else:
            raise Exception(f"{symbol} : Unexpected response structure or missing candlestick data")
        
    def get_historical_klines_df(self, symbol, bar='15m', limit=300, after:str=None, params={}) -> pd.DataFrame:
        klines = self.get_historical_klines(symbol, bar=bar, limit=limit, after=after, params=params)
        return self.format_klines(klines)

    def format_klines(self, klines) -> pd.DataFrame:       
        """_summary_
            格式化K线数据
        Args:
            klines (_type_): _description_
        """
        klines_df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']) 
        # 转换时间戳为日期时间
        klines_df['timestamp'] = pd.to_datetime(klines_df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
  
        return klines_df