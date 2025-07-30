import os
import click
import requests
from .bandit_test import run_bandit_on_path
from .analyzer import save_scan_report
from prettytable import PrettyTable



# def save_scan_report(report_text, filename="scan_report.txt"):
#     try:
#         with open(filename, "w", encoding="utf-8") as f:
#             f.write(report_text)
#         print(f"\n Scan report saved to {filename}")
#     except Exception as e:
#         print(f"\n Error saving scan report: {e}")

@click.command()
@click.argument('target')
@click.option('--format', default='json', help="Output format: json or table")
@click.option('--recursive', '-r', is_flag=True, help="Recursively scan directories")
def scan(target, format, recursive):
    click.echo(f" Scanning {target}...\n")

    if not os.path.exists(target):
        click.echo(f'The path {target} doesnt exist')
        return
    
    issue_list = []

    if os.path.isdir(target):
        if recursive:
            for root, _, files in os.walk(target):
                for file in files:
                    if file.endswith(".py"):
                        full_path = os.path.join(root, file)
                        issue_list.extend(run_bandit_on_path(full_path))
        else:
            click.echo(f" Skipping directory ({target}), use --recursive or -r to scan contents")
            return
    else:
        issue_list = run_bandit_on_path(target)

    report_text = ""

    if format == 'table':
        table = PrettyTable()
        table.field_names = ["File", "Line", "Issue", "Severity", "Confidence", "AI Suggestion"]

    for result in issue_list:
        issue = result.as_dict()
        issue_details = (
            "=" * 50 + "\n" +
            f"→ Issue      : {issue['issue_text']}\n" +
            f"→ File       : {issue['filename']}\n" +
            f"→ Line       : {issue['line_number']}\n" +
            f"→ Severity   : {issue['issue_severity']}\n" +
            f"→ Confidence : {issue['issue_confidence']}\n"
        )

        code_context = issue.get('code', "Code not available")
        try:
            response = requests.post(
                'https://scannerserver-ethp.onrender.com/get_suggestions',
                json={
                    "issue_text": issue['issue_text'],
                    "code_snippet": code_context
                }
            )
            if response.status_code == 200:
                # ai_suggestion = response.json().get("suggestion", "No suggestion returned")
                suggestion = response.json()
                ai_suggestion = suggestion.get('content', 'No suggestion returned')
            else:
                ai_suggestion = f"AI request failed: {response.status_code} {response.text}"
        except Exception as e:
            ai_suggestion = f"AI request error: {str(e)}"

        issue_details += f"→ AI Suggestion: {ai_suggestion}\n"

        if format == 'table':
            table.add_row([
                issue['filename'],
                issue['line_number'],
                issue['issue_text'],
                issue['issue_severity'],
                issue['issue_confidence'],
                ai_suggestion
            ])
        else:
            print(issue_details)

        report_text += issue_details + "\n"

    if format == 'table':
        print(table)

    save = input("\n Would you like to save the scan report to a file? (y/n): ").strip().lower()
    if save == 'y':
        save_scan_report(results=report_text)





if __name__ == '__main__':
    scan()
