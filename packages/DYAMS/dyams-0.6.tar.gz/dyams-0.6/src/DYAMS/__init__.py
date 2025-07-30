from .client import Client

__all__ = ['Client']


def get_post_investment_product_list(*args, **kwargs):
    return Client.get_instance().get_post_investment_product_list(*args, **kwargs)


def get_post_investment_product_holdings(*args, **kwargs):
    return Client.get_instance().get_post_investment_product_holdings(*args, **kwargs)


def get_post_investment_product_performance_indicators(*args, **kwargs):
    return Client.get_instance().get_post_investment_product_performance_indicators(*args, **kwargs)


def get_post_investment_product_net(*args, **kwargs):
    return Client.get_instance().get_post_investment_product_net(*args, **kwargs)


def get_post_investment_product_asset_allocation(*args, **kwargs):
    return Client.get_instance().get_post_investment_product_asset_allocation(*args, **kwargs)


def get_private_asset_net(*args, **kwargs):
    return Client.get_instance().get_private_asset_net(*args, **kwargs)
