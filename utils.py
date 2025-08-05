from vnstock.explorer.fmarket.fund import Fund
import pandas as pd
class FundData:
    """
    Class to retrieve fund data from VnStock.

    Attributes:
        start_date (str, optional): Start date of the fund data in 'YYYY-MM-DD' format.
        end_date (str, optional): End date of the fund data in 'YYYY-MM-DD' format.
        fund_type (int, optional): Type of fund.
            1 - Bond fund (Quỹ trái phiếu)
            2 - Balanced fund (Quỹ cân bằng)
            3 - Equity fund (Quỹ cổ phiếu)
    """

    def __init__(self, start_date=None, end_date=None, fund_type=None):
        """
        Initializes the FundData class with fund type and date range.

        Args:
            start_date (str, optional): Start date in 'YYYY-MM-DD' format.
            end_date (str, optional): End date in 'YYYY-MM-DD' format.
            fund_type (int, optional): Type of fund (1: Bond, 2: Balanced, 3: Equity).
        """
        self.fund_type = fund_type
        self.start_date = start_date
        self.end_date = end_date

    def take_list_fund_name(self):
        """
        Retrieves the list of available fund names from VnStock.

        Returns:
            A DataFrame containing listed fund names and metadata.
        """
        return Fund().listing()
    

        