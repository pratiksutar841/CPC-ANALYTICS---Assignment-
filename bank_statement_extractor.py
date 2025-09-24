#!/usr/bin/env python3
"""
bank_statement_extractor.py
Usage:
  python bank_statement_extractor.py --pdf "ICICI.pdf" --outdir output

What it does:
  - Extracts account info (account_number, account_holder_name, account_type, ifsc, micr, bank_name, address)
  - Extracts transactions: transaction_date, description, withdrawal_amount, deposit_amount, balance
  - Flags: DD large withdrawals (>10k), RTGS large deposits (>50k), entities Guddu/Prabhat/Arif/Coal India
  - Saves account_info.csv and transactions.csv (standardized)
  - Produces a timeline PNG (deposits & withdrawals) and a one-page PDF report (report.pdf)
Notes:
  - Tries camelot first (table extraction). If camelot not available or fails, falls back to text parsing with heuristics.
  - For scanned PDFs you will need OCR (pytesseract) — not covered here.
"""
import os, re, argparse, warnings
from datetime import datetime
import pandas as pd
import pdfplumber
import matplotlib.pyplot as plt

# Try to import camelot (optional)
try:
    import camelot
    HAS_CAMELOT = True
except Exception:
    HAS_CAMELOT = False

# ---------- helper functions ----------
AMOUNT_RE = re.compile(r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)')

def clean_amount(s):
    if s is None: 
        return None
    s = str(s).replace('Cr','').replace('DR','').replace('-', '').strip()
    s = s.replace(',', '')
    s = re.sub(r'[^\d\.]', '', s)
    if s == '':
        return None
    try:
        return float(s)
    except:
        return None

def parse_date_try(s):
    # Try common formats; dayfirst=True
    for fmt in ("%d-%m-%Y","%d/%m/%Y","%d-%m-%y","%d/%m/%y","%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except:
            pass
    # fallback to pandas
    try:
        return pd.to_datetime(s, dayfirst=True, errors='coerce').date()
    except:
        return None

# ---------- extract account info ----------
def extract_account_info(pdf_path):
    """Searches the first 2 pages for IFSC, MICR, account number, holder name, bank name."""
    with pdfplumber.open(pdf_path) as pdf:
        text = '\n'.join((pdf.pages[i].extract_text() or '') for i in range(min(3, len(pdf.pages))))
    # Account number
    m = re.search(r'Account(?:\s+No(?:\.|)|(?:\s+number)|\s*[:\-])\s*[:\-]?\s*([A-Za-z0-9\-]{6,})', text, re.I)
    account_number = m.group(1).strip() if m else None
    # IFSC
    m = re.search(r'IFSC\s*[:\-]?\s*([A-Z0-9]{11})', text, re.I)
    ifsc = m.group(1) if m else None
    # MICR
    m = re.search(r'MICR\s*[:\-]?\s*([0-9]{6,9})', text, re.I)
    micr = m.group(1) if m else None
    # account holder name: try lines with MR./MRS. or first uppercase line blocks
    name = None
    m = re.search(r'^(MR\.|MRS\.|MS\.|MRS|MR|Mrs|Mr)\s*([A-Z][A-Za-z \.&-]{2,})', text, re.M)
    if m:
        name = m.group(0).strip()
    else:
        # fallback: first long line of letters
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for ln in lines[:10]:
            if len(ln) > 5 and any(c.isalpha() for c in ln) and ln.upper()==ln:
                name = ln
                break
    # bank name - top of doc (first line of first page)
    with pdfplumber.open(pdf_path) as pdf:
        first_page_text = (pdf.pages[0].extract_text() or '').splitlines()
    bank_name = first_page_text[0].strip() if first_page_text else None
    # address attempt
    m = re.search(r'Address\s*[:\-]?\s*(.+?)\n\n', text, re.S|re.I)
    address = m.group(1).strip() if m else None
    # account type (search for "Savings" / "Current")
    m = re.search(r'\b(Savings|Current)\b', text, re.I)
    account_type = m.group(1).title() if m else None
    return {
        'account_number': account_number,
        'account_holder_name': name,
        'account_type': account_type,
        'ifsc': ifsc,
        'micr': micr,
        'bank_name': bank_name,
        'address': address
    }

# ---------- extract transaction table ----------
def extract_transactions(pdf_path):
    """
    Returns a DataFrame with columns:
    transaction_date, description, withdrawal_amount, deposit_amount, balance
    """
    # 1) Try camelot (table extraction)
    if HAS_CAMELOT:
        try:
            tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
            # look for tables where first col has lots of dates
            date_pattern = re.compile(r'\d{2}[-/]\d{2}[-/]\d{2,4}')
            for t in tables:
                df = t.df.copy()
                # check if first col has date-like entries (>=2)
                firstcol = df.iloc[:,0].astype(str)
                hits = sum(1 for v in firstcol if date_pattern.search(v))
                if hits >= 2:  # likely the transactions table
                    # heuristic: last 2-3 columns contain amounts
                    # standardize columns to strings
                    df = df.applymap(lambda x: x.strip() if isinstance(x,str) else x)
                    records = []
                    for _, row in df.iterrows():
                        first = str(row.iloc[0])
                        m = date_pattern.search(first)
                        if not m:
                            continue
                        date = m.group(0)
                        # description = join middle columns (1 .. -3)
                        if df.shape[1] >= 4:
                            desc_cols = df.columns[1:df.shape[1]-3] if df.shape[1] > 4 else df.columns[1:-2]
                            desc = ' '.join(str(row[c]) for c in desc_cols).strip()
                            # last three columns -> amounts
                            tail = [str(row[c]) for c in df.columns[-3:]]
                            w = clean_amount(tail[0]) if tail and tail[0] else None
                            d = clean_amount(tail[1]) if len(tail) > 1 and tail[1] else None
                            b = clean_amount(tail[-1]) if tail[-1] else None
                        else:
                            # fallback: put the rest as description and try to extract numbers
                            rest = ' '.join(str(x) for x in row.iloc[1:])
                            desc = rest
                            nums = AMOUNT_RE.findall(rest)
                            w = d = b = None
                            if len(nums) >= 3:
                                w = clean_amount(nums[-3]); d = clean_amount(nums[-2]); b = clean_amount(nums[-1])
                        records.append({
                            'transaction_date': date,
                            'description': desc,
                            'withdrawal_amount': w,
                            'deposit_amount': d,
                            'balance': b
                        })
                    if records:
                        df_out = pd.DataFrame(records)
                        # normalize columns
                        df_out['transaction_date'] = pd.to_datetime(df_out['transaction_date'], dayfirst=True, errors='coerce')
                        df_out['withdrawal_amount'] = pd.to_numeric(df_out['withdrawal_amount'], errors='coerce')
                        df_out['deposit_amount'] = pd.to_numeric(df_out['deposit_amount'], errors='coerce')
                        df_out['balance'] = pd.to_numeric(df_out['balance'], errors='coerce')
                        return df_out[['transaction_date','description','withdrawal_amount','deposit_amount','balance']]
        except Exception as e:
            warnings.warn(f'Camelot extraction failed: {e}')

    # 2) Fallback: text parsing using pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        pages_text = [page.extract_text() or '' for page in pdf.pages]
    full_text = '\n'.join(pages_text)
    lines = full_text.splitlines()
    date_rx = re.compile(r'^\s*(\d{2}[/-]\d{2}[/-]\d{2,4})\b')
    records = []
    current = None
    for line in lines:
        line = line.rstrip()
        m = date_rx.match(line)
        if m:
            if current:
                records.append(current)
            date_str = m.group(1)
            after = line[m.end():].strip()
            nums = AMOUNT_RE.findall(line)
            # heuristics for mapping numbers to withdraw/deposit/balance
            w = d = b = None
            if len(nums) >= 3:
                w = clean_amount(nums[-3]); d = clean_amount(nums[-2]); b = clean_amount(nums[-1])
            elif len(nums) == 2:
                # often deposit + balance or withdrawal + balance; we'll assume deposit + balance if the earlier text contains 'CR' or amounts order
                d = clean_amount(nums[-2]); b = clean_amount(nums[-1])
            elif len(nums) == 1:
                b = clean_amount(nums[-1])
            current = {'transaction_date': date_str, 'description': after, 'withdrawal_amount': w, 'deposit_amount': d, 'balance': b}
        else:
            # continuation of description
            if current:
                current['description'] = (current.get('description') or '') + ' ' + line.strip()
    if current:
        records.append(current)
    df_out = pd.DataFrame(records)
    if df_out.empty:
        return df_out  # empty DataFrame
    # normalize
    df_out['transaction_date'] = pd.to_datetime(df_out['transaction_date'], dayfirst=True, errors='coerce')
    df_out['withdrawal_amount'] = pd.to_numeric(df_out['withdrawal_amount'], errors='coerce')
    df_out['deposit_amount'] = pd.to_numeric(df_out['deposit_amount'], errors='coerce')
    df_out['balance'] = pd.to_numeric(df_out['balance'], errors='coerce')
    return df_out[['transaction_date','description','withdrawal_amount','deposit_amount','balance']]

# ---------- analysis / flagging ----------
def flag_transactions(df):
    df = df.copy()
    df['description'] = df['description'].fillna('').astype(str)
    df['flag_DD_large_withdrawal'] = df.apply(
        lambda r: (r['withdrawal_amount'] or 0) > 10000 and bool(re.search(r'\bDD\b', r['description'], re.I)),
        axis=1
    )
    df['flag_RTGS_large_deposit'] = df.apply(
        lambda r: (r['deposit_amount'] or 0) > 50000 and bool(re.search(r'RTGS', r['description'], re.I)),
        axis=1
    )
    # entities: Guddu, Prabhat, Arif, Coal India
    pattern = re.compile(r'\b(guddu|prabhat|arif|coal india)\b', re.I)
    df['flag_entities'] = df['description'].apply(lambda s: bool(pattern.search(s)))
    return df

# ---------- plotting ----------
def plot_timeline(df, out_png):
    df2 = df.copy()
    df2['date'] = pd.to_datetime(df2['transaction_date'], errors='coerce')
    group = df2.groupby('date').agg({'deposit_amount':'sum','withdrawal_amount':'sum'}).fillna(0).sort_index()
    plt.figure(figsize=(10,4))
    plt.plot(group.index, group['deposit_amount'], label='Deposits', marker='o')
    plt.plot(group.index, group['withdrawal_amount'], label='Withdrawals', marker='o')
    plt.legend()
    plt.title('Daily deposits and withdrawals')
    plt.xlabel('Date')
    plt.ylabel('Amount (INR)')
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()

# ---------- small report (reportlab) ----------
def make_report(account_info, transactions_df, plot_png, out_pdf, name='Your Name', email='you@example.com'):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
    from reportlab.lib.styles import getSampleStyleSheet
    doc = SimpleDocTemplate(out_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    normal.fontName = 'Times-Roman'
    normal.fontSize = 11
    story = []
    story.append(Paragraph(f"<b>Bank Statement Extraction Report</b>", normal))
    story.append(Spacer(1,8))
    story.append(Paragraph(f"Name: {name}", normal))
    story.append(Paragraph(f"Email: {email}", normal))
    story.append(Spacer(1,8))
    story.append(Paragraph("<b>Methodology (brief)</b>", normal))
    story.append(Paragraph("1) Try structured table extraction using Camelot. 2) If that fails, fallback to text parsing using date regex and amount heuristics. 3) Standardize columns and run flagging rules.", normal))
    story.append(Spacer(1,8))
    # account info table
    acc_items = [[k, str(v)] for k,v in account_info.items()]
    story.append(Paragraph("<b>Account Info</b>", normal))
    story.append(Table(acc_items))
    story.append(Spacer(1,8))
    # summary counts
    story.append(Paragraph("<b>Flags summary</b>", normal))
    flag_counts = [
        ['DD large withdrawals (>10k)', str(int(transactions_df['flag_DD_large_withdrawal'].sum()))],
        ['RTGS large deposits (>50k)', str(int(transactions_df['flag_RTGS_large_deposit'].sum()))],
        ['Named entities (Guddu/Prabhat/Arif/Coal India)', str(int(transactions_df['flag_entities'].sum()))]
    ]
    story.append(Table(flag_counts))
    story.append(Spacer(1,8))
    # attach the plot
    if os.path.exists(plot_png):
        story.append(Paragraph("<b>Timeline (deposits & withdrawals)</b>", normal))
        story.append(Image(plot_png, width=400, height=160))
    doc.build(story)

# ---------- main driver ----------
def main(pdf_path, outdir, name, email):
    os.makedirs(outdir, exist_ok=True)
    print("Extracting account info...")
    acc = extract_account_info(pdf_path)
    print("Extracting transactions (this may take a moment)...")
    tx = extract_transactions(pdf_path)
    if tx.empty:
        print("Warning: No transactions extracted. Check if PDF is scanned image (OCR required) or layout unknown.")
    tx_flags = flag_transactions(tx)
    # Save CSVs
    acc_df = pd.DataFrame([acc])
    acc_df.to_csv(os.path.join(outdir,'account_info.csv'), index=False)
    tx_flags.to_csv(os.path.join(outdir,'transactions.csv'), index=False)
    print(f"Saved account_info.csv and transactions.csv in {outdir}")
    # Plot timeline (if any)
    png = os.path.join(outdir, 'timeline.png')
    try:
        plot_timeline(tx_flags, png)
        print("Timeline plot saved to", png)
    except Exception as e:
        print("Could not create timeline:", e)
    # report
    report_pdf = os.path.join(outdir, 'report.pdf')
    try:
        make_report(acc, tx_flags, png, report_pdf, name=name, email=email)
        print("Report saved to", report_pdf)
    except Exception as e:
        print("Could not create report:", e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Bank statement extractor")
    parser.add_argument('--pdf', required=True, help='Path to PDF file')
    parser.add_argument('--outdir', default='output', help='Output folder')
    parser.add_argument('--name', default='Your Name', help='Your name for report')
    parser.add_argument('--email', default='you@example.com', help='Your email for report')
    args = parser.parse_args()
    main(args.pdf, args.outdir, args.name, args.email)
