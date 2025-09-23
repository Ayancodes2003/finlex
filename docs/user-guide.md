# FinLex User Guide

## Introduction

FinLex is a comprehensive financial compliance auditing platform that leverages AI to analyze transaction data against regulatory policies. This guide will help you navigate and use the platform effectively.

## Getting Started

### Logging In

1. Open your web browser and navigate to `http://localhost:3000`
2. Enter your username and password
3. Click "Login"

### Navigation

The platform features a navigation bar at the top with the following sections:

- **Dashboard** - Overview of system metrics and compliance status
- **Data Upload** - Upload transaction data for analysis
- **Policy Management** - Manage compliance policies
- **Compliance Scan** - Run compliance checks on transactions
- **Reports** - View and generate compliance reports

## Dashboard

The dashboard provides an overview of key compliance metrics:

- Total transactions processed
- Active policies
- Violations detected
- High-risk alerts

Two charts visualize:
1. Violations by risk level
2. Compliance trends over time

## Data Upload

### Uploading Transaction Data

1. Navigate to the "Data Upload" section
2. Drag and drop your CSV file or click "Browse Files"
3. Select your transaction data file (CSV format)
4. Click "Process Transactions"

### CSV File Format

Your CSV file should include the following columns:
- `amount` - Transaction amount
- `date` - Transaction date
- `type` - Transaction type
- `description` - Transaction description
- `metadata` (optional) - Additional transaction information

Example:
```csv
amount,date,type,description,metadata
1000.00,2023-01-15,deposit,Client deposit,"{""client_id"": ""C12345""}"
500.00,2023-01-16,withdrawal,ATM withdrawal,
```

## Policy Management

### Adding a New Policy

1. Navigate to the "Policy Management" section
2. Click "Add New Policy"
3. Fill in the policy details:
   - Title
   - Jurisdiction
   - Category
   - Content
4. Click "Save Policy"

### Viewing Policies

All active policies are displayed in a table with:
- Title
- Jurisdiction
- Category
- Creation date
- Action buttons (View, Delete)

## Compliance Scan

### Running a Compliance Scan

1. Navigate to the "Compliance Scan" section
2. Click "Run Compliance Scan"
3. Wait for the scan to complete
4. View detected violations in the table below

### Violation Details

Violations are categorized by risk level:
- **High** - Requires immediate attention
- **Medium** - Needs review
- **Low** - Informational

Each violation includes:
- Transaction ID
- Applicable policy
- Risk level
- Description
- Action button (Details)

## Reports

### Generating a Report

1. Navigate to the "Reports" section
2. Click "Generate New Report"
3. Wait for the report to be generated
4. View the report in the table below

### Viewing Reports

All generated reports are listed with:
- Report ID
- Generation date and time
- Action buttons (View, Download)

## User Management

### Logging Out

Click the "Logout" button in the top right corner of the navigation bar.

## Best Practices

1. **Regular Scanning** - Run compliance scans regularly to catch violations early
2. **Policy Updates** - Keep policies up-to-date with changing regulations
3. **Data Quality** - Ensure transaction data is clean and complete
4. **Report Review** - Review generated reports for compliance insights
5. **Risk Management** - Address high-risk violations immediately

## Troubleshooting

### Common Issues

1. **Upload Fails** - Ensure your CSV file follows the required format
2. **Scan Takes Too Long** - Large datasets may take longer to process
3. **Login Issues** - Verify your username and password

### Support

For technical support, contact your system administrator or refer to the developer documentation.