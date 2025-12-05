"""
FastAPI Main Application
Provides REST API endpoints for PDF upload, data retrieval, and analysis
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
from typing import List, Dict, Any
import json

from pdf_extractor import pdf_to_json
from database import DynamicDatabaseManager
import config

app = FastAPI(
    title="PDF Data Extraction & Storage System",
    description="Upload PDFs, extract structured data, and store in dynamic database",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database manager
db_manager = DynamicDatabaseManager()


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve simple HTML frontend"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Data Extractor</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 { 
                color: #667eea; 
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .upload-section {
                border: 3px dashed #667eea;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                background: #f8f9ff;
            }
            input[type="file"] {
                display: none;
            }
            .file-label {
                background: #667eea;
                color: white;
                padding: 15px 30px;
                border-radius: 5px;
                cursor: pointer;
                display: inline-block;
                font-size: 1.1em;
                transition: all 0.3s;
            }
            .file-label:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .file-name {
                margin-top: 15px;
                color: #666;
                font-style: italic;
            }
            button {
                background: #764ba2;
                color: white;
                border: none;
                padding: 15px 40px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1.1em;
                margin: 10px;
                transition: all 0.3s;
            }
            button:hover {
                background: #653a8a;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(118, 75, 162, 0.4);
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            .table-section {
                margin-top: 30px;
                overflow: hidden;
            }
            .table-name {
                background: #f8f9ff;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            select {
                width: 100%;
                padding: 12px;
                border: 3px solid #667eea;
                border-radius: 5px;
                font-size: 1em;
                margin-bottom: 15px;
                background: white;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 4px 4px 8px rgba(102, 126, 234, 0.2);
                appearance: auto;
                -webkit-appearance: menulist;
                -moz-appearance: menulist;
            }
            select:hover {
                border-color: #5568d3;
                box-shadow: 4px 6px 12px rgba(102, 126, 234, 0.35);
            }
            select:focus {
                outline: none;
                border-color: #764ba2;
                box-shadow: 0 0 0 3px rgba(118, 75, 162, 0.15), 4px 4px 10px rgba(118, 75, 162, 0.3);
            }
            select option {
                padding: 12px;
                font-size: 1em;
                background: white;
                color: #333;
                border: none;
            }
            select option:checked {
                background: #667eea;
                color: white;
                font-weight: 600;
            }
            select option:hover {
                background: #f8f9ff;
                color: #333;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                font-size: 14px;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                min-width: 100%;
                table-layout: auto;
            }
            th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 12px;
                text-align: left;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 12px;
                letter-spacing: 0.5px;
                position: sticky;
                top: 0;
                z-index: 10;
                white-space: nowrap;
            }
            th:last-child {
                position: sticky;
                right: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                box-shadow: -2px 0 5px rgba(0,0,0,0.1);
            }
            td {
                padding: 12px;
                border-bottom: 1px solid #e8e8e8;
                color: #333;
                vertical-align: top;
                word-wrap: break-word;
                max-width: 300px;
                cursor: pointer;
            }
            td:last-child {
                position: sticky;
                right: 0;
                background: white;
                box-shadow: -2px 0 5px rgba(0,0,0,0.1);
                cursor: default;
            }
            tr:nth-child(even) td:last-child {
                background: #f8f9ff;
            }
            tr:hover td {
                background: #e8ecff;
            }
            tr:hover td:last-child {
                background: #e8ecff;
            }
            tbody tr:last-child td {
                border-bottom: none;
            }
            .table-container {
                overflow-x: auto;
                overflow-y: auto;
                max-height: 600px;
                max-width: 100%;
                border-radius: 8px;
                margin-top: 20px;
                display: block;
            }
            .table-container::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            .table-container::-webkit-scrollbar-track {
                background: #f1f1f1;
            }
            .table-container::-webkit-scrollbar-thumb {
                background: #667eea;
                border-radius: 4px;
            }
            .table-container::-webkit-scrollbar-thumb:hover {
                background: #5568d3;
            }
            .table-info {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px;
                background: #f8f9ff;
                border-radius: 5px;
                margin-top: 10px;
                font-size: 14px;
                color: #666;
            }
            .null-value {
                color: #999;
                font-style: italic;
            }
            .numeric-value {
                text-align: right;
                font-family: 'Courier New', monospace;
            }
            .message {
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: center;
            }
            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 PDF Data Extraction System</h1>
            <p class="subtitle">Upload PDFs to extract tables and store in dynamic database</p>
            
            <div class="upload-section">
                <input type="file" id="fileInput" accept=".pdf" />
                <label for="fileInput" class="file-label">📎 Choose PDF File</label>
                <div class="file-name" id="fileName">No file chosen</div>
            </div>
            
            <div style="text-align: center;">
                <input type="text" id="tableName" placeholder="Table name (e.g., invoices, balance_sheet)" 
                       style="width: 300px; padding: 12px; border: 2px solid #667eea; border-radius: 5px; margin-right: 10px;">
                <button onclick="uploadPDF()" id="uploadBtn" disabled>Upload & Extract</button>
                <button onclick="loadTables()">View All Tables</button>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 10px;">Processing PDF...</p>
            </div>
            
            <div id="message"></div>
            
            <div class="table-section">
                <h2>📊 View Stored Data</h2>
                <div style="background: #f8f9ff; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #667eea;">
                        Select Table:
                    </label>
                    <select id="tableSelect" onchange="loadTableData()">
                        <option value="">-- Choose a table to view data --</option>
                    </select>
                    <div id="tableCount" style="margin-top: 10px; color: #666; font-size: 0.9em;"></div>
                </div>
                
                <div style="margin: 15px 0;">
                    <button onclick="exportToExcel()" style="background: #10b981;">📥 Export to Excel</button>
                    <button onclick="showAddRowModal()" style="background: #3b82f6;">➕ Add Row</button>
                    <button onclick="confirmDeleteTable()" style="background: #ef4444;">🗑️ Delete Table</button>
                </div>
                
                <div style="padding: 10px; background: #fff3cd; border-left: 4px solid #ffc107; margin-bottom: 15px; border-radius: 4px; font-size: 0.9em;">
                    💡 <strong>Tip:</strong> Double-click any row to edit it, or use the buttons in the Actions column.
                </div>
                
                <div id="tableData"></div>
            </div>
        </div>
        
        <!-- Add/Edit Row Modal -->
        <div id="rowModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; align-items: center; justify-content: center; overflow-y: auto;">
            <div style="background: white; padding: 30px; border-radius: 10px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; margin: 20px;">
                <h2 id="modalTitle">Add New Row</h2>
                <div id="rowFields"></div>
                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <button onclick="saveRow()" style="flex: 1; background: #10b981;">Save</button>
                    <button onclick="hideRowModal()" style="flex: 1; background: #666;">Cancel</button>
                </div>
            </div>
        </div>
        
        <script>
            const fileInput = document.getElementById('fileInput');
            const fileName = document.getElementById('fileName');
            const uploadBtn = document.getElementById('uploadBtn');
            const tableNameInput = document.getElementById('tableName');
            
            fileInput.addEventListener('change', function() {
                if (this.files.length > 0) {
                    fileName.textContent = this.files[0].name;
                    uploadBtn.disabled = false;
                } else {
                    fileName.textContent = 'No file chosen';
                    uploadBtn.disabled = true;
                }
            });
            
            async function uploadPDF() {
                const file = fileInput.files[0];
                const tableName = tableNameInput.value.trim() || 'pdf_data';
                
                if (!file) {
                    showMessage('Please select a PDF file', 'error');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                
                document.getElementById('loading').style.display = 'block';
                uploadBtn.disabled = true;
                
                try {
                    const response = await fetch(`/upload?table_name=${tableName}`, {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showMessage(`✅ Success! Extracted ${result.records_inserted} records into table '${result.table_name}'`, 'success');
                        loadTables();
                        fileInput.value = '';
                        fileName.textContent = 'No file chosen';
                        tableNameInput.value = '';
                    } else {
                        showMessage('❌ Error: ' + result.detail, 'error');
                    }
                } catch (error) {
                    showMessage('❌ Error: ' + error.message, 'error');
                } finally {
                    document.getElementById('loading').style.display = 'none';
                    uploadBtn.disabled = false;
                }
            }
            
            async function loadTables() {
                try {
                    const response = await fetch('/tables');
                    const data = await response.json();
                    
                    const select = document.getElementById('tableSelect');
                    select.innerHTML = '<option value="">-- Choose a table to view data --</option>';
                    
                    data.tables.forEach(table => {
                        const option = document.createElement('option');
                        option.value = table;
                        option.textContent = `📋 ${table.replace(/_/g, ' ').toUpperCase()}`;
                        select.appendChild(option);
                    });
                    
                    // Update table count
                    const countDiv = document.getElementById('tableCount');
                    if (data.tables.length > 0) {
                        countDiv.textContent = `✓ ${data.tables.length} table${data.tables.length > 1 ? 's' : ''} available`;
                        countDiv.style.color = '#10b981';
                    } else {
                        countDiv.textContent = 'No tables found. Upload a PDF to get started.';
                        countDiv.style.color = '#666';
                    }
                } catch (error) {
                    showMessage('❌ Error loading tables: ' + error.message, 'error');
                }
            }
            
            async function loadTableData() {
                const tableName = document.getElementById('tableSelect').value;
                if (!tableName) {
                    document.getElementById('tableData').innerHTML = '';
                    return;
                }
                
                try {
                    const response = await fetch(`/data/${tableName}`);
                    const result = await response.json();
                    
                    if (result.data.length === 0) {
                        document.getElementById('tableData').innerHTML = '<p>No data found in this table.</p>';
                        return;
                    }
                    
                    const columns = Object.keys(result.data[0]).filter(col => col !== 'id');
                    
                    // Table info
                    let infoHTML = `<div class="table-info">
                        <span><strong>Table:</strong> ${tableName}</span>
                        <span><strong>Records:</strong> ${result.data.length}</span>
                        <span><strong>Columns:</strong> ${columns.length}</span>
                    </div>`;
                    
                    // Table container with scrolling
                    let tableHTML = '<div class="table-container"><table><thead><tr>';
                    
                    columns.forEach(col => {
                        tableHTML += `<th>${col.replace(/_/g, ' ').toUpperCase()}</th>`;
                    });
                    tableHTML += '<th style="width: 120px;">ACTIONS</th></tr></thead><tbody>';
                    
                    result.data.forEach(row => {
                        const rowId = row.id;
                        tableHTML += `<tr ondblclick="editRow(${rowId})" title="Double-click to edit">`;
                        columns.forEach(col => {
                            const value = row[col];
                            let cellClass = '';
                            let displayValue = value;
                            
                            if (value === null || value === '') {
                                cellClass = 'null-value';
                                displayValue = '—';
                            } else if (typeof value === 'number') {
                                cellClass = 'numeric-value';
                                displayValue = value.toLocaleString();
                            }
                            
                            tableHTML += `<td class="${cellClass}">${displayValue}</td>`;
                        });
                        
                        // Action buttons
                        tableHTML += `<td style="white-space: nowrap;">
                            <button onclick="event.stopPropagation(); editRow(${rowId})" style="padding: 5px 10px; margin: 2px; background: #3b82f6; font-size: 0.85em;">✏️</button>
                            <button onclick="event.stopPropagation(); deleteRow(${rowId})" style="padding: 5px 10px; margin: 2px; background: #ef4444; font-size: 0.85em;">🗑️</button>
                        </td>`;
                        tableHTML += '</tr>';
                    });
                    
                    tableHTML += '</tbody></table></div>';
                    document.getElementById('tableData').innerHTML = infoHTML + tableHTML;
                } catch (error) {
                    showMessage('❌ Error loading data: ' + error.message, 'error');
                }
            }
            
            function showMessage(text, type) {
                const messageDiv = document.getElementById('message');
                messageDiv.className = `message ${type}`;
                messageDiv.textContent = text;
                messageDiv.style.display = 'block';
                
                setTimeout(() => {
                    messageDiv.style.display = 'none';
                }, 5000);
            }
            
            async function exportToExcel() {
                const tableName = document.getElementById('tableSelect').value;
                if (!tableName) {
                    showMessage('❌ Please select a table first', 'error');
                    return;
                }
                
                try {
                    // Trigger file download
                    window.location.href = `/export/${tableName}`;
                    showMessage('✅ Excel file download started', 'success');
                } catch (error) {
                    showMessage('❌ Error: ' + error.message, 'error');
                }
            }
            
            async function confirmDeleteTable() {
                const tableName = document.getElementById('tableSelect').value;
                if (!tableName) {
                    showMessage('❌ Please select a table first', 'error');
                    return;
                }
                
                if (confirm(`Are you sure you want to delete the entire table '${tableName}'? This cannot be undone.`)) {
                    try {
                        const response = await fetch(`/table/${tableName}`, {
                            method: 'DELETE'
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            showMessage('✅ ' + result.message, 'success');
                            document.getElementById('tableSelect').value = '';
                            document.getElementById('tableData').innerHTML = '';
                            loadTables();
                        } else {
                            showMessage('❌ Error: ' + result.detail, 'error');
                        }
                    } catch (error) {
                        showMessage('❌ Error: ' + error.message, 'error');
                    }
                }
            }
            
            let currentEditId = null;
            let tableColumns = [];
            
            async function showAddRowModal() {
                const tableName = document.getElementById('tableSelect').value;
                if (!tableName) {
                    showMessage('❌ Please select a table first', 'error');
                    return;
                }
                
                try {
                    const response = await fetch(`/schema/${tableName}`);
                    const result = await response.json();
                    
                    tableColumns = result.columns.filter(col => col.name !== 'id');
                    currentEditId = null;
                    
                    document.getElementById('modalTitle').textContent = 'Add New Row';
                    generateFormFields({});
                    document.getElementById('rowModal').style.display = 'flex';
                } catch (error) {
                    showMessage('❌ Error: ' + error.message, 'error');
                }
            }
            
            async function editRow(rowId) {
                const tableName = document.getElementById('tableSelect').value;
                
                try {
                    // Get schema
                    const schemaResponse = await fetch(`/schema/${tableName}`);
                    const schemaResult = await schemaResponse.json();
                    tableColumns = schemaResult.columns.filter(col => col.name !== 'id');
                    
                    // Get row data
                    const dataResponse = await fetch(`/data/${tableName}`);
                    const dataResult = await dataResponse.json();
                    const rowData = dataResult.data.find(row => row.id === rowId);
                    
                    if (rowData) {
                        currentEditId = rowId;
                        document.getElementById('modalTitle').textContent = 'Edit Row';
                        generateFormFields(rowData);
                        document.getElementById('rowModal').style.display = 'flex';
                    }
                } catch (error) {
                    showMessage('❌ Error: ' + error.message, 'error');
                }
            }
            
            function generateFormFields(data) {
                let fieldsHTML = '';
                
                tableColumns.forEach(col => {
                    const value = data[col.name] || '';
                    fieldsHTML += `
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #667eea;">
                                ${col.name.replace(/_/g, ' ').toUpperCase()}
                            </label>
                            <input type="text" id="field_${col.name}" value="${value}" 
                                   style="width: 100%; padding: 10px; border: 2px solid #667eea; border-radius: 5px;">
                        </div>
                    `;
                });
                
                document.getElementById('rowFields').innerHTML = fieldsHTML;
            }
            
            async function saveRow() {
                const tableName = document.getElementById('tableSelect').value;
                const rowData = {};
                
                tableColumns.forEach(col => {
                    const input = document.getElementById(`field_${col.name}`);
                    let value = input.value;
                    
                    // Try to convert to number if possible
                    if (value && !isNaN(value)) {
                        value = value.includes('.') ? parseFloat(value) : parseInt(value);
                    }
                    
                    rowData[col.name] = value || null;
                });
                
                try {
                    let response;
                    
                    if (currentEditId) {
                        // Update existing row
                        response = await fetch(`/table/${tableName}/row/${currentEditId}`, {
                            method: 'PUT',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(rowData)
                        });
                    } else {
                        // Add new row
                        response = await fetch(`/table/${tableName}/row`, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(rowData)
                        });
                    }
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showMessage('✅ ' + result.message, 'success');
                        hideRowModal();
                        loadTableData();
                    } else {
                        showMessage('❌ Error: ' + result.detail, 'error');
                    }
                } catch (error) {
                    showMessage('❌ Error: ' + error.message, 'error');
                }
            }
            
            async function deleteRow(rowId) {
                const tableName = document.getElementById('tableSelect').value;
                
                if (confirm('Are you sure you want to delete this row?')) {
                    try {
                        const response = await fetch(`/table/${tableName}/row/${rowId}`, {
                            method: 'DELETE'
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            showMessage('✅ ' + result.message, 'success');
                            loadTableData();
                        } else {
                            showMessage('❌ Error: ' + result.detail, 'error');
                        }
                    } catch (error) {
                        showMessage('❌ Error: ' + error.message, 'error');
                    }
                }
            }
            
            function hideRowModal() {
                document.getElementById('rowModal').style.display = 'none';
                currentEditId = null;
            }
            
            function showMessage(text, type) {
                const messageDiv = document.getElementById('message');
                messageDiv.className = `message ${type}`;
                messageDiv.textContent = text;
                messageDiv.style.display = 'block';
                
                setTimeout(() => {
                    messageDiv.style.display = 'none';
                }, 5000);
            }
            
            // Load tables on page load
            window.onload = loadTables;
        </script>
    </body>
    </html>
    """


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), table_name: str = "pdf_data"):
    """
    Upload PDF file, extract data, and store in database
    
    Args:
        file: PDF file to upload
        table_name: Name of the table to store data (default: pdf_data)
    
    Returns:
        JSON response with extraction results
    """
    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file
    file_path = os.path.join(config.UPLOAD_FOLDER, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract data from PDF
        result = pdf_to_json(file_path)
        
        if not result["success"] or not result["data"]:
            raise HTTPException(status_code=400, detail="No data could be extracted from PDF")
        
        # Store in database
        db_manager.insert_data(table_name, result["data"])
        
        # Clean up uploaded file after successful processing
        try:
            os.remove(file_path)
            print(f"Deleted uploaded file: {file_path}")
        except Exception as e:
            print(f"Warning: Could not delete file {file_path}: {e}")
        
        return {
            "success": True,
            "message": "PDF processed successfully",
            "filename": file.filename,
            "table_name": table_name,
            "records_inserted": result["total_records"],
            "sample_data": result["data"][:3] if len(result["data"]) > 3 else result["data"]
        }
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.get("/tables")
async def get_tables():
    """Get list of all tables in database"""
    try:
        tables = db_manager.get_all_tables()
        return {
            "success": True,
            "tables": tables,
            "count": len(tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tables: {str(e)}")


@app.get("/data/{table_name}")
async def get_table_data(table_name: str):
    """
    Retrieve all data from a specific table
    
    Args:
        table_name: Name of the table
    
    Returns:
        JSON response with table data
    """
    try:
        data = db_manager.get_all_data(table_name)
        return {
            "success": True,
            "table_name": table_name,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@app.get("/schema/{table_name}")
async def get_table_schema(table_name: str):
    """
    Get schema/structure of a table
    
    Args:
        table_name: Name of the table
    
    Returns:
        JSON response with table schema
    """
    try:
        schema = db_manager.get_table_schema(table_name)
        if not schema:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        return {
            "success": True,
            "table_name": table_name,
            "columns": schema
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schema: {str(e)}")


@app.get("/analyze/{table_name}")
async def analyze_table(table_name: str):
    """
    Analyze data in a table (basic statistics)
    
    Args:
        table_name: Name of the table
    
    Returns:
        JSON response with analysis results
    """
    try:
        data = db_manager.get_all_data(table_name)
        
        if not data:
            return {
                "success": True,
                "table_name": table_name,
                "message": "No data to analyze"
            }
        
        # Basic analysis
        analysis = {
            "total_records": len(data),
            "columns": list(data[0].keys()) if data else [],
            "column_count": len(data[0].keys()) if data else 0
        }
        
        # Analyze numeric columns
        numeric_stats = {}
        for column in analysis["columns"]:
            values = [row[column] for row in data if row[column] is not None]
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            
            if numeric_values:
                numeric_stats[column] = {
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "avg": sum(numeric_values) / len(numeric_values),
                    "count": len(numeric_values)
                }
        
        analysis["numeric_stats"] = numeric_stats
        
        return {
            "success": True,
            "table_name": table_name,
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing data: {str(e)}")


@app.get("/export/{table_name}")
async def export_to_excel(table_name: str):
    """
    Export table data to Excel file and download
    
    Args:
        table_name: Name of the table
    
    Returns:
        Excel file as download
    """
    try:
        file_path = os.path.join(config.UPLOAD_FOLDER, f"{table_name}.xlsx")
        db_manager.export_to_excel(table_name, file_path)
        
        return FileResponse(
            path=file_path,
            filename=f"{table_name}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


@app.delete("/table/{table_name}")
async def delete_table(table_name: str):
    """
    Delete a table from the database
    
    Args:
        table_name: Name of the table to delete
    
    Returns:
        JSON response with deletion result
    """
    try:
        db_manager.delete_table(table_name)
        return {
            "success": True,
            "message": f"Table '{table_name}' deleted successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting table: {str(e)}")


@app.delete("/table/{table_name}/row/{row_id}")
async def delete_row(table_name: str, row_id: int):
    """
    Delete a specific row from a table
    
    Args:
        table_name: Name of the table
        row_id: ID of the row to delete
    
    Returns:
        JSON response with deletion result
    """
    try:
        db_manager.delete_row(table_name, row_id)
        return {
            "success": True,
            "message": f"Row {row_id} deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting row: {str(e)}")


@app.put("/table/{table_name}/row/{row_id}")
async def update_row(table_name: str, row_id: int, updates: Dict[str, Any]):
    """
    Update a specific row in a table
    
    Args:
        table_name: Name of the table
        row_id: ID of the row to update
        updates: Dictionary of column:value pairs to update
    
    Returns:
        JSON response with update result
    """
    try:
        db_manager.update_row(table_name, row_id, updates)
        return {
            "success": True,
            "message": f"Row {row_id} updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating row: {str(e)}")


@app.post("/table/{table_name}/row")
async def add_row(table_name: str, row_data: Dict[str, Any]):
    """
    Add a new row to a table
    
    Args:
        table_name: Name of the table
        row_data: Dictionary of column:value pairs for the new row
    
    Returns:
        JSON response with addition result
    """
    try:
        db_manager.add_row(table_name, row_data)
        return {
            "success": True,
            "message": "Row added successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding row: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
