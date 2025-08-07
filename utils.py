from vnstock.explorer.fmarket.fund import Fund
import pandas as pd
import time

fund = Fund()

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class OpenData:
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
        
    def get_csv(self, dir):
        """
        Downloads NAV report data for each fund and saves it as a CSV file in the specified directory.
        Processes funds in chunks of 10 to avoid rate limits, waiting 90 seconds between each chunk.

        Args:
            dir (str): The directory where CSV files will be saved.
        """
        name_list = self.get_fund_name()
        
        for idx, name_group in enumerate(chunk_list(name_list, 10)):
            print(f"Processing fund {idx + 1}/{(len(name_list) + 9) // 10}...")
            for name in name_group:
                try:
                    # Retrieve NAV report data for the fund
                    data = fund.details.nav_report(name)
                    # Save the data to a CSV file named after the fund
                    data.to_csv(f"{dir}/{name}.csv", index=False)
                    print(f"Processed fund {name}")
                except Exception as e:
                    # Print an error message if processing fails for a fund
                    print(f"Error processing fund {name}: {e}")
                    
            # Wait 90 seconds between chunks to avoid hitting the rate limit
            if (idx + 1) * 10 < len(name_list):
                print(f"Waiting 90 seconds to avoid rate limit...")
                time.sleep(90)
        


        