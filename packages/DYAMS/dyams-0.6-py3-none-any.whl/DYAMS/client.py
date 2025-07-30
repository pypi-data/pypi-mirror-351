from .api.heartbeat import heartbeat
from .api.get_post_investment_product_list import get_post_investment_product_list
from .api.get_post_investment_product_holdings import get_post_investment_product_holdings
from .api.get_post_investment_product_performance_indicators import get_post_investment_product_performance_indicators
from .api.get_post_investment_product_net import get_post_investment_product_net
from .api.get_post_investment_product_asset_allocation import get_post_investment_product_asset_allocation
from .api.get_private_asset_net import get_private_asset_net


class Client:

    _instance = None

    def __init__(self, token='', env='prd'):
        self.token = token
        if env == 'prd':
            self.base_url = "https://gw.datayes.com/aladdin_mof"
        elif env == 'qa':
            self.base_url = "https://gw.datayes-stg.com/mom_aladdin_qa"
        elif env == 'stg':
            self.base_url = "https://gw.datayes-stg.com/mom_aladdin_stg"
        else:
            raise ValueError("error env")
        heartbeat(self)
        Client._instance = self

    @staticmethod
    def get_instance():
        if Client._instance is None:
            raise RuntimeError("Client未初始化，请先实例化Client")
        return Client._instance

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }


Client.get_post_investment_product_list = get_post_investment_product_list
Client.get_post_investment_product_holdings = get_post_investment_product_holdings
Client.get_post_investment_product_performance_indicators = get_post_investment_product_performance_indicators
Client.get_post_investment_product_net = get_post_investment_product_net
Client.get_post_investment_product_asset_allocation = get_post_investment_product_asset_allocation
Client.get_private_asset_net = get_private_asset_net
