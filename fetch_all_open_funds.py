from take_data import OpenData

def main():
    import os
    # Download bond fund data
    print('Downloading bond funds...')
    bond_dir = 'data/bond_fund'
    if not os.path.exists(bond_dir):
        os.makedirs(bond_dir)
    OpenData(fund_type=1).get_csv(bond_dir)
    
    # Download balanced fund data
    print('Downloading balanced funds...')
    balanced_dir = 'data/balanced_fund'
    if not os.path.exists(balanced_dir):
        os.makedirs(balanced_dir)
    OpenData(fund_type=2).get_csv(balanced_dir)
    
    # Download stock fund data
    print('Downloading stock funds...')
    stock_dir = 'data/stock_fund'
    if not os.path.exists(stock_dir):
        os.makedirs(stock_dir)
    OpenData(fund_type=3).get_csv(stock_dir)
    
    print('All fund data downloaded.')

if __name__ == '__main__':
    main()
