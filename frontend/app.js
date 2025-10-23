// Global variables
let currentPage = 'dashboard';
let authToken = null;

// DOM Elements
const pages = document.querySelectorAll('.page');
const navLinks = document.querySelectorAll('nav a');
const logoutBtn = document.getElementById('logout-btn');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Set up navigation
    setupNavigation();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load initial data
    loadDashboardData();
});

// Set up navigation
function setupNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            switchPage(page);
        });
    });
}

// Switch between pages
function switchPage(page) {
    // Hide all pages
    pages.forEach(p => p.classList.remove('active'));
    
    // Show selected page
    document.getElementById(page).classList.add('active');
    
    // Update navigation
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === page) {
            link.classList.add('active');
        }
    });
    
    // Load page-specific data
    switch(page) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'policies':
            loadPolicies();
            break;
        case 'scan':
            loadViolations();
            break;
        case 'reports':
            loadReports();
            break;
    }
    
    currentPage = page;
}

// Set up event listeners
function setupEventListeners() {
    // Logout
    logoutBtn.addEventListener('click', logout);
    
    // Data Upload
    setupUploadListeners();
    
    // Policy Management
    setupPolicyListeners();
    
    // Compliance Scan
    setupScanListeners();
    
    // Reports
    setupReportListeners();
}

// Authentication functions
function login() {
    // In a real implementation, this would authenticate with the API
    authToken = 'dummy-token'; // Placeholder
    console.log('User logged in');
}

function logout() {
    authToken = null;
    console.log('User logged out');
    // Redirect to login page or show login modal
}

// Dashboard functions
function loadDashboardData() {
    // In a real implementation, this would fetch from the API
    // For now, we'll use simulated data based on what we processed
    
    // Simulate API calls to get dashboard data
    document.getElementById('total-transactions').textContent = '5,000';
    document.getElementById('active-policies').textContent = '12';
    document.getElementById('violations-count').textContent = '40';
    document.getElementById('high-risk-alerts').textContent = '15';
    
    // Initialize charts
    initializeCharts();
}

function initializeCharts() {
    // Risk level chart
    const riskCtx = document.getElementById('risk-chart').getContext('2d');
    new Chart(riskCtx, {
        type: 'bar',
        data: {
            labels: ['High', 'Medium', 'Low'],
            datasets: [{
                label: 'Violations',
                data: [15, 20, 5],
                backgroundColor: [
                    'rgba(239, 71, 111, 0.8)',
                    'rgba(255, 209, 102, 0.8)',
                    'rgba(6, 214, 160, 0.8)'
                ],
                borderColor: [
                    'rgba(239, 71, 111, 1)',
                    'rgba(255, 209, 102, 1)',
                    'rgba(6, 214, 160, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 5
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    // Trend chart - transaction types
    const trendCtx = document.getElementById('trend-chart').getContext('2d');
    new Chart(trendCtx, {
        type: 'pie',
        data: {
            labels: ['CASH_IN', 'PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT'],
            datasets: [{
                label: 'Transaction Types',
                data: [1082, 2587, 437, 631, 263],
                backgroundColor: [
                    'rgba(67, 97, 238, 0.8)',
                    'rgba(114, 9, 183, 0.8)',
                    'rgba(30, 60, 114, 0.8)',
                    'rgba(41, 182, 246, 0.8)',
                    'rgba(38, 198, 218, 0.8)'
                ],
                borderColor: [
                    'rgba(67, 97, 238, 1)',
                    'rgba(114, 9, 183, 1)',
                    'rgba(30, 60, 114, 1)',
                    'rgba(41, 182, 246, 1)',
                    'rgba(38, 198, 218, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Transaction Types Distribution'
                }
            }
        }
    });
}

// Data Upload functions
function setupUploadListeners() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const processBtn = document.getElementById('process-btn');
    
    // Click browse button
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File selected
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('dragover');
    }
    
    function unhighlight() {
        dropArea.classList.remove('dragover');
    }
    
    // Handle dropped file
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        // Assign dropped files to the hidden input so existing flow works
        fileInput.files = files;
        // Trigger change to reuse validation/UI updates
        const changeEvent = new Event('change');
        fileInput.dispatchEvent(changeEvent);
        handleFiles(files);
    }
    
    // Handle selected file
    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }
    
    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            // Accept both CSV and PDF files
            if (file.type === 'text/csv' || file.name.endsWith('.csv') || 
                file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
                displayUploadStatus(`Selected file: ${file.name}`, 'success');
                document.getElementById('process-btn').disabled = false;
            } else {
                displayUploadStatus('Please select a CSV or PDF file', 'error');
                document.getElementById('process-btn').disabled = true;
            }
        }
    }
    
    function displayUploadStatus(message, type) {
        const statusDiv = document.getElementById('upload-status');
        statusDiv.textContent = message;
        statusDiv.className = type;
        statusDiv.style.display = 'block';
    }
    
    // Process transactions
    processBtn.addEventListener('click', processTransactions);
    
    function processTransactions() {
        const fileInput = document.getElementById('file-input');
        const file = fileInput.files[0];
        
        if (!file) {
            displayUploadStatus('Please select a file first', 'error');
            return;
        }
        
        displayUploadStatus('Processing transactions...', 'processing');
        
        // Create FormData object for file upload
        const formData = new FormData();
        formData.append('file', file);
        
        // Upload file to the API
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Upload failed');
            }
        })
        .then(data => {
            displayUploadStatus(data.message || 'Successfully processed transactions', 'success');
            // Reset file input
            fileInput.value = '';
            document.getElementById('process-btn').disabled = true;
        })
        .catch(error => {
            console.error('Error processing transactions:', error);
            displayUploadStatus('Error processing transactions: ' + error.message, 'error');
        });
    }
}

// Policy Management functions
function setupPolicyListeners() {
    const addPolicyBtn = document.getElementById('add-policy-btn');
    const policyModal = document.getElementById('policy-modal');
    const viewPolicyModal = document.getElementById('view-policy-modal');
    const closeButtons = document.querySelectorAll('.close');
    const policyForm = document.getElementById('policy-form');
    
    // Open add policy modal
    addPolicyBtn.addEventListener('click', () => {
        policyModal.style.display = 'block';
    });
    
    // Close modals
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            policyModal.style.display = 'none';
            viewPolicyModal.style.display = 'none';
        });
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === policyModal) {
            policyModal.style.display = 'none';
        }
        if (e.target === viewPolicyModal) {
            viewPolicyModal.style.display = 'none';
        }
    });
    
    // Submit form
    policyForm.addEventListener('submit', (e) => {
        e.preventDefault();
        savePolicy();
    });
}

function savePolicy() {
    // Get form data
    const title = document.getElementById('policy-title').value;
    const jurisdiction = document.getElementById('policy-jurisdiction').value;
    const category = document.getElementById('policy-category').value;
    const content = document.getElementById('policy-content').value;
    
    // Create policy object
    const policyData = {
        id: Date.now().toString(), // Simple ID generation
        title: title,
        content: content,
        jurisdiction: jurisdiction,
        category: category,
        created_at: new Date().toISOString(),
        embeddings: null
    };
    
    // Save to API
    fetch('/api/policies', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(policyData)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to save policy');
        }
    })
    .then(data => {
        console.log('Policy saved:', data);
        // Close modal
        document.getElementById('policy-modal').style.display = 'none';
        // Reset form
        document.getElementById('policy-form').reset();
        // Reload policies
        loadPolicies();
    })
    .catch(error => {
        console.error('Error saving policy:', error);
        alert('Error saving policy: ' + error.message);
    });
}

function loadPolicies() {
    // Fetch from the API through the Nginx proxy
    fetch('/api/policies')
        .then(response => response.json())
        .then(policies => {
            const tbody = document.querySelector('#policies-table tbody');
            tbody.innerHTML = '';
            
            policies.forEach(policy => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${policy.title}</td>
                    <td>${policy.jurisdiction}</td>
                    <td>${policy.category}</td>
                    <td>${new Date(policy.created_at).toLocaleDateString()}</td>
                    <td>
                        <button onclick="viewPolicy('${policy.id}')">View</button>
                        <button onclick="deletePolicy('${policy.id}')">Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading policies:', error);
            // Fallback to simulated data
            const policies = [
                { id: '1', title: 'AML Policy', jurisdiction: 'US', category: 'Anti-Money Laundering', created_at: '2023-01-15' },
                { id: '2', title: 'KYC Guidelines', jurisdiction: 'EU', category: 'Know Your Customer', created_at: '2023-02-20' },
                { id: '3', title: 'Data Protection', jurisdiction: 'Global', category: 'Privacy', created_at: '2023-03-10' }
            ];
            
            const tbody = document.querySelector('#policies-table tbody');
            tbody.innerHTML = '';
            
            policies.forEach(policy => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${policy.title}</td>
                    <td>${policy.jurisdiction}</td>
                    <td>${policy.category}</td>
                    <td>${policy.created_at}</td>
                    <td>
                        <button onclick="viewPolicy('${policy.id}')">View</button>
                        <button onclick="deletePolicy('${policy.id}')">Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        });
}

function viewPolicy(id) {
    // Fetch policy details from API through the Nginx proxy
    fetch(`/api/policies/${id}`)
        .then(response => response.json())
        .then(policy => {
            // Display policy in modal
            document.getElementById('view-policy-title').textContent = policy.title;
            document.getElementById('view-policy-content').innerHTML = `
                <div class="policy-details">
                    <p><strong>Jurisdiction:</strong> ${policy.jurisdiction}</p>
                    <p><strong>Category:</strong> ${policy.category}</p>
                    <p><strong>Created:</strong> ${new Date(policy.created_at).toLocaleDateString()}</p>
                    <hr>
                    <div class="policy-content">
                        <h3>Policy Content:</h3>
                        <p>${policy.content.replace(/\n/g, '<br>')}</p>
                    </div>
                </div>
            `;
            document.getElementById('view-policy-modal').style.display = 'block';
        })
        .catch(error => {
            console.error('Error loading policy:', error);
            alert(`Error loading policy: ${error.message}`);
        });
}

function deletePolicy(id) {
    // Delete policy via API
    if (confirm('Are you sure you want to delete this policy?')) {
        fetch(`/api/policies/${id}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                console.log(`Policy ${id} deleted successfully`);
                loadPolicies(); // Reload the list
            } else {
                throw new Error('Failed to delete policy');
            }
        })
        .catch(error => {
            console.error('Error deleting policy:', error);
            alert('Error deleting policy: ' + error.message);
        });
    }
}

// Compliance Scan functions
function setupScanListeners() {
    const runScanBtn = document.getElementById('run-scan-btn');
    runScanBtn.addEventListener('click', runComplianceScan);
    
    // Close violation modal when clicking close button or outside
    const violationModal = document.getElementById('view-violation-modal');
    if (violationModal) {
        const closeButtons = violationModal.querySelectorAll('.close');
        closeButtons.forEach(button => {
            button.addEventListener('click', () => {
                violationModal.style.display = 'none';
            });
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === violationModal) {
                violationModal.style.display = 'none';
            }
        });
    }
}

function runComplianceScan() {
    const statusDiv = document.getElementById('scan-status');
    const runScanBtn = document.getElementById('run-scan-btn');
    const originalBtnText = runScanBtn.innerHTML;
    
    // Show loading spinner
    runScanBtn.innerHTML = '<span class="loading-spinner"></span> Scanning...';
    runScanBtn.disabled = true;
    
    statusDiv.textContent = 'Running compliance scan...';
    statusDiv.className = 'processing';
    statusDiv.style.display = 'block';
    
    // In a real implementation, this would send data to the compliance service
    // For now, we'll call the compliance scan endpoint
    fetch('/api/compliance/scan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: 'Compliance scan initiated',
            timestamp: new Date().toISOString()
        })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Scan failed');
        }
    })
    .then(data => {
        statusDiv.textContent = 'Compliance scan completed.';
        statusDiv.className = 'success';
        loadViolations(); // Reload violations
    })
    .catch(error => {
        console.error('Error running compliance scan:', error);
        statusDiv.textContent = 'Error running compliance scan: ' + error.message;
        statusDiv.className = 'error';
    })
    .finally(() => {
        // Restore button
        runScanBtn.innerHTML = originalBtnText;
        runScanBtn.disabled = false;
    });
}

function loadViolations() {
    // Fetch violations from the API
    fetch('/api/compliance/violations')
        .then(response => response.json())
        .then(violations => {
            const tbody = document.querySelector('#violations-table tbody');
            tbody.innerHTML = '';
            
            violations.forEach(violation => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${violation.transactionId || 'N/A'}</td>
                    <td>${violation.policy || 'N/A'}</td>
                    <td class="risk-${violation.risk || 'low'}">${violation.risk ? violation.risk.charAt(0).toUpperCase() + violation.risk.slice(1) : 'Low'}</td>
                    <td>${violation.description || 'No description'}</td>
                    <td>
                        <button onclick="viewViolation('${violation.id}')">Details</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading violations:', error);
            // Fallback to simulated data
            const violations = [
                { id: '1', transactionId: 'TXN-001', policy: 'AML Policy', risk: 'high', description: 'Large cash transaction over $10,000' },
                { id: '2', transactionId: 'TXN-002', policy: 'KYC Guidelines', risk: 'medium', description: 'Incomplete customer information' },
                { id: '3', transactionId: 'TXN-003', policy: 'Data Protection', risk: 'low', description: 'Missing encryption for data transfer' }
            ];
            
            const tbody = document.querySelector('#violations-table tbody');
            tbody.innerHTML = '';
            
            violations.forEach(violation => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${violation.transactionId}</td>
                    <td>${violation.policy}</td>
                    <td class="risk-${violation.risk}">${violation.risk.charAt(0).toUpperCase() + violation.risk.slice(1)}</td>
                    <td>${violation.description}</td>
                    <td>
                        <button onclick="viewViolation('${violation.id}')">Details</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        });
}

function viewViolation(id) {
    // Fetch violation details from API
    fetch(`/api/compliance/violations/${id}`)
        .then(response => response.json())
        .then(violation => {
            // Display violation in modal
            document.getElementById('view-violation-title').textContent = 'Violation Details';
            document.getElementById('view-violation-content').innerHTML = `
                <div class="violation-details">
                    <p><strong>Transaction ID:</strong> ${violation.transaction_id}</p>
                    <p><strong>Policy:</strong> ${violation.policy_id}</p>
                    <p><strong>Risk Level:</strong> <span class="risk-${violation.risk_level}">${violation.risk_level.charAt(0).toUpperCase() + violation.risk_level.slice(1)}</span></p>
                    <p><strong>Created:</strong> ${new Date(violation.created_at).toLocaleString()}</p>
                    <hr>
                    <div class="violation-content">
                        <h3>Description:</h3>
                        <p>${violation.description}</p>
                        <h3>Recommendation:</h3>
                        <p>${violation.recommendation}</p>
                    </div>
                </div>
            `;
            document.getElementById('view-violation-modal').style.display = 'block';
            
            // Add event listener to close button
            const closeButtons = document.querySelectorAll('#view-violation-modal .close');
            closeButtons.forEach(button => {
                button.onclick = function() {
                    document.getElementById('view-violation-modal').style.display = 'none';
                }
            });
            
            // Close modal when clicking outside
            window.onclick = function(event) {
                const modal = document.getElementById('view-violation-modal');
                if (event.target == modal) {
                    modal.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error loading violation:', error);
            alert(`Error loading violation: ${error.message}`);
        });
}

// Reports functions
function setupReportListeners() {
    const generateReportBtn = document.getElementById('generate-report-btn');
    generateReportBtn.addEventListener('click', generateReport);
    
    // Close report modal when clicking close button or outside
    const reportModal = document.getElementById('view-report-modal');
    if (reportModal) {
        const closeButtons = reportModal.querySelectorAll('.close');
        closeButtons.forEach(button => {
            button.addEventListener('click', () => {
                reportModal.style.display = 'none';
            });
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === reportModal) {
                reportModal.style.display = 'none';
            }
        });
    }
}

function generateReport() {
    const generateReportBtn = document.getElementById('generate-report-btn');
    const originalBtnText = generateReportBtn.innerHTML;
    
    // Show loading spinner
    generateReportBtn.innerHTML = '<span class="loading-spinner"></span> Generating...';
    generateReportBtn.disabled = true;
    
    // First, we need to fetch the required data for report generation
    Promise.all([
        fetch('/api/compliance/violations').then(res => res.json()),
        fetch('/api/transactions').then(res => res.json()),
        fetch('/api/policies').then(res => res.json())
    ])
    .then(([violations, transactions, policies]) => {
        // Call the API to generate a report with the required data
        return fetch('/api/reports/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                violations_data: violations,
                transactions_data: transactions,
                policies_data: policies
            })
        });
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Report generation failed');
        }
    })
    .then(data => {
        alert('Report generated successfully!');
        loadReports(); // Reload reports
    })
    .catch(error => {
        console.error('Error generating report:', error);
        alert('Error generating report: ' + error.message);
    })
    .finally(() => {
        // Restore button
        generateReportBtn.innerHTML = originalBtnText;
        generateReportBtn.disabled = false;
    });
}

function loadReports() {
    // Fetch reports from the API
    fetch('/api/reports')
        .then(response => response.json())
        .then(reports => {
            const tbody = document.querySelector('#reports-table tbody');
            tbody.innerHTML = '';
            
            reports.forEach(report => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${report.id || 'N/A'}</td>
                    <td>${report.generated || new Date().toLocaleString()}</td>
                    <td>
                        <button onclick="viewReport('${report.id}')">View</button>
                        <button onclick="downloadReport('${report.id}')">Download</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading reports:', error);
            // Fallback to simulated data
            const reports = [
                { id: '1', generated: '2023-06-15 14:30:00' },
                { id: '2', generated: '2023-06-10 09:15:00' },
                { id: '3', generated: '2023-06-05 16:45:00' }
            ];
            
            const tbody = document.querySelector('#reports-table tbody');
            tbody.innerHTML = '';
            
            reports.forEach(report => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${report.id}</td>
                    <td>${report.generated}</td>
                    <td>
                        <button onclick="viewReport('${report.id}')">View</button>
                        <button onclick="downloadReport('${report.id}')">Download</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        });
}

function viewReport(id) {
    // Fetch report details from API
    fetch(`/api/reports/${id}`)
        .then(response => response.json())
        .then(report => {
            // Display report in modal
            document.getElementById('view-report-title').textContent = `Report ${report.id || id}`;
            document.getElementById('view-report-content').innerHTML = `
                <div class="report-details">
                    <p><strong>Generated:</strong> ${report.generated ? new Date(report.generated).toLocaleString() : 'N/A'}</p>
                    <p><strong>Status:</strong> ${report.status || 'Completed'}</p>
                    <hr>
                    <div class="report-content">
                        <h3>Summary:</h3>
                        <p>${report.summary || 'No summary available'}</p>
                        <h3>Details:</h3>
                        <p>${report.details || 'No details available'}</p>
                    </div>
                </div>
            `;
            document.getElementById('view-report-modal').style.display = 'block';
            
            // Add event listener to close button
            const closeButtons = document.querySelectorAll('#view-report-modal .close');
            closeButtons.forEach(button => {
                button.onclick = function() {
                    document.getElementById('view-report-modal').style.display = 'none';
                }
            });
            
            // Close modal when clicking outside
            window.onclick = function(event) {
                const modal = document.getElementById('view-report-modal');
                if (event.target == modal) {
                    modal.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error loading report:', error);
            alert(`Error loading report: ${error.message}`);
        });
}

function downloadReport(id) {
    // Fetch report details from API
    fetch(`/api/reports/${id}`)
        .then(response => response.json())
        .then(report => {
            // Create a blob with the report data
            const reportData = JSON.stringify(report, null, 2);
            const blob = new Blob([reportData], { type: 'application/json' });
            
            // Create a download link
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `report-${id}.json`;
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }, 100);
        })
        .catch(error => {
            console.error('Error downloading report:', error);
            alert(`Error downloading report: ${error.message}`);
        });
}

// Initialize the app
login();