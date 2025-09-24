<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bank Statement Analysis - CPC Hiring Assignment</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 20px;
            background-color: #f7f7f7;
            color: #333;
        }
        h1, h2, h3, h4 {
            color: #1b1b1b;
        }
        code {
            background-color: #eee;
            padding: 2px 5px;
            border-radius: 3px;
        }
        pre {
            background-color: #eee;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        img {
            display: block;
            margin: 10px auto;
            max-width: 100%;
        }
        .section {
            background: #fff;
            padding: 15px 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.05);
        }
        a {
            color: #1a73e8;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        ul {
            padding-left: 20px;
        }
    </style>
</head>
<body>

    <div class="section">
        <h1>🏦 Bank Statement Analysis - CPC Hiring Assignment</h1>

        <h2>📌 Project Objective</h2>
        <p>The objective of this project is to build a <strong>robust data extraction and analysis tool</strong> that can:</p>
        <ul>
            <li>Extract structured information from PDF bank statements (HDFC and ICICI).</li>
            <li>Parse and standardize transactions into CSV files.</li>
            <li>Apply analysis rules to <strong>flag suspicious or high-value transactions</strong>.</li>
            <li>Generate a <strong>summary report (PDF)</strong> and <strong>visualization</strong> for insights.</li>
        </ul>
        <p>This solution automates manual data entry and supports <strong>financial investigators</strong> in quickly identifying key patterns and anomalies.</p>
    </div>

    <div class="section">
        <h2>📂 Project Structure</h2>
        <pre>
bank-statement-analysis/
│── bank_statement_extractor.py
│── requirements.txt
│── HDFC.pdf
│── ICICI.pdf
│── output_HDFC/
│   ├─ account_info.csv
│   ├─ transactions.csv
│   ├─ report.pdf
│── output_ICICI/
│   ├─ account_info.csv
│   ├─ transactions.csv
│   ├─ timeline.png
│   ├─ report.pdf
│── README.md
        </pre>
    </div>

    <div class="section">
        <h2>🛠️ Tools & Technologies</h2>
        <ul>
            <li><strong>Programming Language:</strong> Python 3.10</li>
            <li><strong>Libraries:</strong>
                <ul>
                    <li>pdfplumber → extract text from PDFs</li>
                    <li>camelot-py → extract structured tables from PDFs</li>
                    <li>pandas, numpy → data preprocessing & manipulation</li>
                    <li>matplotlib → visualization (timeline plot)</li>
                    <li>reportlab → generate summary PDF report</li>
                </ul>
            </li>
            <li><strong>Environment:</strong> VS Code / Anaconda</li>
            <li><strong>Version Control:</strong> Git & GitHub</li>
        </ul>
    </div>

    <div class="section">
        <h2>📊 Methodology</h2>
        <ol>
            <li><strong>PDF Data Extraction</strong>
                <ul>
                    <li>Extract account information (account number, IFSC, MICR, holder name, etc.).</li>
                    <li>Parse transaction tables into standardized columns:
                        <ul>
                            <li>transaction_date</li>
                            <li>description</li>
                            <li>withdrawal_amount</li>
                            <li>deposit_amount</li>
                            <li>balance</li>
                        </ul>
                    </li>
                </ul>
            </li>
            <li><strong>Transaction Analysis & Flagging</strong>
                <ul>
                    <li>DD Large Withdrawal: Identify withdrawals &gt; ₹10,000 via Demand Draft (DD).</li>
                    <li>RTGS Large Deposit: Flag deposits &gt; ₹50,000 via RTGS.</li>
                    <li>Entity Check: Flag transactions with entities “Guddu”, “Prabhat”, “Arif”, or “Coal India”.</li>
                </ul>
            </li>
            <li><strong>Visualization</strong>
                <ul>
                    <li>Create a <strong>timeline plot</strong> for ICICI statements showing withdrawals vs deposits.</li>
                </ul>
            </li>
            <li><strong>Report Generation</strong>
                <ul>
                    <li>Auto-generate <code>report.pdf</code> (max 3 pages, font Times 11pt) containing:
                        <ul>
                            <li>Methodology</li>
                            <li>Account details</li>
                            <li>Summary of flagged transactions</li>
                            <li>Visualization</li>
                        </ul>
                    </li>
                </ul>
            </li>
        </ol>
    </div>

    <div class="section">
        <h2>📈 Key Results</h2>
        <ul>
            <li>Successfully extracted account and transaction details from <strong>HDFC</strong> and <strong>ICICI</strong> sample statements.</li>
            <li>Generated <strong>standardized CSV files</strong> with clean, structured data.</li>
            <li>Implemented <strong>flagging rules</strong> to highlight suspicious transactions.</li>
            <li>Created a <strong>timeline chart</strong> for ICICI deposits & withdrawals.</li>
            <li>Produced <strong>summary reports</strong> for both statements.</li>
        </ul>
    </div>

    <div class="section">
        <h2>📌 Features</h2>
        <ul>
            <li>🔄 Works with both <strong>HDFC</strong> and <strong>ICICI</strong> bank statements.</li>
            <li>📑 Extracts <strong>account details</strong> and <strong>transactions</strong> into CSV.</li>
            <li>🚩 Flags transactions that meet suspicious criteria.</li>
            <li>📊 Generates <strong>visual insights</strong> (timeline plot).</li>
            <li>📝 Creates a <strong>PDF report</strong> with methodology and findings.</li>
        </ul>
    </div>

    <div class="section">
        <h2>🚀 How to Run Locally</h2>
        <h4>1. Clone the repository</h4>
        <pre>git clone https://github.com/yourusername/bank-statement-analysis.git
cd bank-statement-analysis</pre>

        <h4>2. Create & activate virtual environment</h4>
        <pre>python -m venv venv
# Activate:
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux</pre>

        <h4>3. Install dependencies</h4>
        <pre>pip install -r requirements.txt</pre>

        <h4>4. Run the script</h4>
        <p>For ICICI statement:</p>
        <pre>python bank_statement_extractor.py --pdf "ICICI.pdf" --outdir output_ICICI --name "Pratik Sutar" --email "pratik@example.com"</pre>
        <p>For HDFC statement:</p>
        <pre>python bank_statement_extractor.py --pdf "HDFC.pdf" --outdir output_HDFC --name "Pratik Sutar" --email "pratik@example.com"</pre>
    </div>

    <div class="section">
        <h2>📂 Output Files</h2>
        <ul>
            <li>account_info.csv → account details (account number, holder name, IFSC, MICR, etc.)</li>
            <li>transactions.csv → structured transactions with flags:
                <ul>
                    <li>flag_DD_large_withdrawal</li>
                    <li>flag_RTGS_large_deposit</li>
                    <li>flag_entities</li>
                </ul>
            </li>
            <li>timeline.png → deposits vs withdrawals plot (only for ICICI).</li>
            <li>report.pdf → summary report with methodology, flagged transactions, and visualization.</li>
        </ul>
        <p>Example: ICICI Timeline Plot</p>
        <img src="output_ICICI/timeline.png" alt="ICICI Bank Timeline Plot">
        <p>Example: Report PDF</p>
        <img src="output_ICICI/report_preview.png" alt="Sample Report PDF">
    </div>

    <div class="section">
        <h2>🙋‍♂️ Author</h2>
        <p>Pratik Prashant Sutar<br>
        B.Tech in Computer Science & Engineering (Data Science)</p>
        <ul>
            <li>GitHub: <a href="https://github.com/pratiksutar841">pratiksutar841</a></li>
            <li>LinkedIn: <a href="https://www.linkedin.com/in/pratik-sutar">Pratik Sutar</a></li>
        </ul>
        <p>📧 Submission: Zip your folder (including bank_statement_extractor.py, requirements.txt, outputs, and this README.md) and email it to <a href="mailto:judy@cpc-analytics.com">judy@cpc-analytics.com</a> before 28th Sept 2025, 17:00 IST.</p>
    </div>

</body>
</html>
