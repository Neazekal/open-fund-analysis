from vnstock.explorer.fmarket.fund import Fund
import pandas as pd
class FundData:
    """
    Class to retrieve fund data from VnStock.

    Attributes:
        fund_type (int, optional): Type of fund.
            1 - Bond fund (Quỹ trái phiếu)
            2 - Balanced fund (Quỹ cân bằng)
            3 - Equity fund (Quỹ cổ phiếu)
    """

    def __init__(self, fund_type=None):
        """
        Initializes the FundData class with fund type and date range.

        Args:
            fund_type (int, optional): Type of fund (1: Bond, 2: Balanced, 3: Equity).
        """
        self.fund_type = fund_type

    def take_list_fund_info(self):
        """
        Retrieves the list of available fund info from VnStock.

        Returns:
            A DataFrame containing listed fund information.
        """
        return Fund().listing()
    
    def get_fund_name(self):
    """
    Retrieves a list of fund short names based on the specified fund type.

    Returns:
        list or DataFrame: 
            - If fund_type is 1 (Bond fund), 2 (Balanced fund), or 3 (Equity fund),
              returns a list of short names for the corresponding fund type.
            - If fund_type is None or invalid, returns the full DataFrame of all listed funds.
    
    Notes:
        fund_type mapping:
            1 - Bond fund (Quỹ trái phiếu)
            2 - Balanced fund (Quỹ cân bằng)
            3 - Equity fund (Quỹ cổ phiếu)
    """
        all_funds = self.take_list_fund_info()
        if self.fund_type == 1:
            return all_funds[all_funds['fund_type'].str.contains('Quỹ trái phiếu', case=False, na=False)]['short_name'].tolist()
        elif self.fund_type == 2:
            return all_funds[all_funds['fund_type'].str.contains('Quỹ cân bằng', case=False, na=False)]['short_name'].tolist()
        elif self.fund_type == 3:
            return all_funds[all_funds['fund_type'].str.contains('Quỹ cổ phiếu', case=False, na=False)]['short_name'].tolist()
        else:
            return all_funds


        