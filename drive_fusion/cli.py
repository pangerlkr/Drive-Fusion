"""Drive Fusion command-line interface."""
import typer

from drive_fusion.core.service import DriveFusionService

app = typer.Typer(help="Drive Fusion CLI - manage multiple Google Drive accounts from one place.")
service = DriveFusionService()


@app.command()
def accounts():
    """List all connected accounts."""
    for a in service.list_accounts():
        typer.echo(f"{a['id']}  {a['name']:<12} {a['email']:<28} {a['used_gb']}/{a['total_gb']} GB")


@app.command()
def connect(name: str, email: str, total_gb: float = 15.0):
    """Register a new account."""
    account = service.add_account(name, email, total_gb)
    typer.echo(f"Connected account {account['id']} ({account['email']})")


@app.command()
def quota():
    """Show aggregate quota usage across accounts."""
    summary = service.usage_summary()
    typer.echo(f"Accounts: {summary['account_count']}")
    typer.echo(f"Used:     {summary['used_gb']} GB")
    typer.echo(f"Free:     {summary['free_gb']} GB")
    typer.echo(f"Total:    {summary['total_gb']} GB")
    typer.echo(f"Usage:    {summary['utilization_pct']}%")


@app.command()
def search(term: str):
    """Search the unified file index."""
    results = service.list_files(term)
    if not results:
        typer.echo("No matches found.")
        return
    for f in results:
        typer.echo(f"{f['id']}  {f['name']:<28} {f['account_id']:<14} {f['size_mb']} MB")


@app.command()
def transfer(source_account: str, target_account: str, file_ids: str, note: str = ""):
    """Queue a transfer job between two accounts. file_ids is comma separated."""
    ids = [f.strip() for f in file_ids.split(",") if f.strip()]
    job = service.create_transfer_job(source_account, target_account, ids, note or None)
    typer.echo(f"Job {job['id']} created: {job['source_account']} -> {job['target_account']} [{job['status']}]")


@app.command()
def report(output: str = "output/workspace-report.md"):
    """Export a Markdown workspace report."""
    import os
    content = service.export_report()
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as fh:
        fh.write(content)
    typer.echo(f"Report written to {output}")


if __name__ == "__main__":
    app()
