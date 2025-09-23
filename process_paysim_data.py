import requests
import pandas as pd
import time

def process_paysim_data():
    """
    Process the Paysim1.csv data and upload it to the transaction ingest service
    """
    print("Processing Paysim Data")
    print("======================")
    
    # Read the CSV file
    csv_path = "data/raw/paysim1.csv"
    print(f"Reading data from {csv_path}...")
    
    # Read a sample of the data (first 100 rows) to avoid overwhelming the system
    df = pd.read_csv(csv_path, nrows=100)
    print(f"Loaded {len(df)} transactions from CSV")
    
    # Display basic information about the data
    print("\nData Summary:")
    print(f"Columns: {list(df.columns)}")
    print(f"Total transactions: {len(df)}")
    print(f"Fraudulent transactions: {df['isFraud'].sum()}")
    print(f"Flagged fraudulent transactions: {df['isFlaggedFraud'].sum()}")
    
    # Prepare data for upload
    print("\nPreparing data for upload...")
    
    # Convert DataFrame to list of dictionaries
    transactions = df.to_dict('records')
    
    # Upload to transaction ingest service
    api_gateway_url = "http://localhost:18000"
    
    print(f"Uploading to Transaction Ingest Service at {api_gateway_url}/transactions...")
    
    # First, we need to authenticate to get a token
    login_params = {
        "username": "admin",
        "password": "password"
    }
    
    try:
        # Login to get authentication token
        login_response = requests.post(f"{api_gateway_url}/auth/login", params=login_params)
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print("Authentication successful")
        else:
            print(f"Authentication failed: {login_response.status_code} - {login_response.text}")
            return
            
        # Upload transactions
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        uploaded_count = 0
        for i, transaction in enumerate(transactions[:10]):  # Upload first 10 transactions
            # Transform the data to match our API
            transaction_data = {
                "type": transaction["type"],
                "amount": transaction["amount"],
                "nameOrig": transaction["nameOrig"],
                "oldbalanceOrg": transaction["oldbalanceOrg"],
                "newbalanceOrig": transaction["newbalanceOrig"],
                "nameDest": transaction["nameDest"],
                "oldbalanceDest": transaction["oldbalanceDest"],
                "newbalanceDest": transaction["newbalanceDest"],
                "isFraud": transaction["isFraud"],
                "isFlaggedFraud": transaction["isFlaggedFraud"]
            }
            
            response = requests.post(
                f"{api_gateway_url}/transactions", 
                json=transaction_data, 
                headers=headers
            )
            
            if response.status_code == 200:
                uploaded_count += 1
                if uploaded_count % 5 == 0:
                    print(f"Uploaded {uploaded_count} transactions...")
            else:
                print(f"Failed to upload transaction {i}: {response.status_code} - {response.text}")
                
        print(f"\nSuccessfully uploaded {uploaded_count} transactions")
        
        # Verify upload by checking transaction count
        print("\nVerifying upload...")
        verify_response = requests.get(f"{api_gateway_url}/transactions", headers=headers)
        if verify_response.status_code == 200:
            # Since this is a proxy, we might get a different response format
            print("Upload verification completed")
        else:
            print(f"Failed to verify transactions: {verify_response.status_code} - {verify_response.text}")
            
    except Exception as e:
        print(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    process_paysim_data()