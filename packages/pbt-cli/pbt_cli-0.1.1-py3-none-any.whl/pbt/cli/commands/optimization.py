"""Optimization-related PBT CLI commands"""

import typer
from pathlib import Path
from typing import Optional
import json
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from pbt.core.project import PBTProject
from pbt.core.prompt_optimizer import PromptOptimizer
from pbt.core.prompt_evaluator import PromptEvaluator
from pbt.core.prompt_chunking import PromptChunker, ChunkingStrategy
from pbt.cli.utils import (
    console,
    load_prompt_file,
    save_prompt_file,
    format_prompt_display
)

def optimize_command(
    prompt_file: Path = typer.Argument(..., help="Path to the prompt file to optimize"),
    strategy: str = typer.Option("balanced", "--strategy", "-s", help="Optimization strategy"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Optimization target: cost, quality, clarity"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for optimized prompt"),
    analyze_only: bool = typer.Option(False, "--analyze", "-a", help="Only analyze, don't optimize"),
    max_reduction: float = typer.Option(0.3, "--max-reduction", "-r", help="Maximum token reduction ratio")
):
    """⚡ Optimize prompts for cost, clarity, or performance"""
    console.print(f"[bold blue]⚡ Optimizing prompt: {prompt_file}[/bold blue]")
    
    # Load prompt
    prompt_data = load_prompt_file(prompt_file)
    
    # Initialize optimizer
    project = PBTProject()
    optimizer = PromptOptimizer(project)
    
    # Analyze current prompt
    analysis = optimizer.analyze(prompt_data)
    
    # Display analysis
    console.print("\n[bold cyan]📊 Prompt Analysis:[/bold cyan]")
    console.print(f"  • Word count: {analysis['word_count']}")
    console.print(f"  • Estimated tokens: {analysis['estimated_tokens']}")
    console.print(f"  • Complexity score: {analysis['complexity_score']:.1f}/10")
    console.print(f"  • Clarity score: {analysis['clarity_score']:.1f}/10")
    
    if analyze_only:
        # Provide recommendations
        console.print("\n[bold yellow]💡 Recommendations:[/bold yellow]")
        for rec in analysis['recommendations']:
            console.print(f"  • {rec}")
        return
    
    # Determine optimization strategy
    if target:
        if target == "cost":
            strategy = "cost_reduce"
        elif target == "quality":
            strategy = "quality_enhance"
        elif target == "clarity":
            strategy = "clarity_improve"
    
    console.print(f"\n[cyan]🎯 Using strategy: {strategy}[/cyan]")
    
    # Optimize
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Optimizing prompt...", total=1)
        
        result = optimizer.optimize(
            prompt_data,
            strategy=strategy,
            constraints={'max_reduction': max_reduction}
        )
        
        progress.update(task, completed=1)
    
    if result['success']:
        optimized_prompt = result['optimized_prompt']
        
        # Display comparison
        console.print("\n[bold]📊 Optimization Results:[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Original", justify="right")
        table.add_column("Optimized", justify="right")
        table.add_column("Change", justify="right")
        
        # Token comparison
        orig_tokens = analysis['estimated_tokens']
        opt_tokens = result['metrics']['estimated_tokens']
        token_reduction = ((orig_tokens - opt_tokens) / orig_tokens) * 100
        
        table.add_row(
            "Estimated Tokens",
            str(orig_tokens),
            str(opt_tokens),
            f"[{'green' if token_reduction > 0 else 'red'}]{token_reduction:+.1f}%[/]"
        )
        
        # Clarity comparison
        if 'clarity_score' in result['metrics']:
            clarity_change = result['metrics']['clarity_score'] - analysis['clarity_score']
            table.add_row(
                "Clarity Score",
                f"{analysis['clarity_score']:.1f}/10",
                f"{result['metrics']['clarity_score']:.1f}/10",
                f"[{'green' if clarity_change > 0 else 'red'}]{clarity_change:+.1f}[/]"
            )
        
        console.print(table)
        
        # Cost savings estimate
        if token_reduction > 0:
            monthly_calls = 10000  # Estimate
            cost_per_1k_tokens = 0.01  # Example rate
            monthly_savings = (orig_tokens - opt_tokens) * monthly_calls * cost_per_1k_tokens / 1000
            
            console.print(f"\n[green]💰 Estimated monthly savings: ${monthly_savings:.2f}[/green]")
            console.print(f"   (Based on {monthly_calls:,} calls/month)")
        
        # Display optimized prompt
        console.print("\n[bold cyan]✨ Optimized Prompt:[/bold cyan]")
        format_prompt_display(optimized_prompt)
        
        # Save if output specified
        if output:
            save_prompt_file(output, optimized_prompt)
            console.print(f"\n[green]✅ Optimized prompt saved to: {output}[/green]")
        else:
            # Ask if user wants to save
            if typer.confirm("\n💾 Save optimized prompt?"):
                output_path = prompt_file.with_stem(f"{prompt_file.stem}_optimized")
                save_prompt_file(output_path, optimized_prompt)
                console.print(f"[green]✅ Saved to: {output_path}[/green]")
    else:
        console.print(f"[red]❌ Optimization failed: {result.get('error', 'Unknown error')}[/red]")
        raise typer.Exit(1)

def eval_command(
    prompts_dir: Path = typer.Option(Path("prompts"), "--dir", "-d", help="Directory containing prompts"),
    metrics: Optional[str] = typer.Option(None, "--metrics", "-m", help="Comma-separated evaluation metrics"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, csv"),
    save_report: bool = typer.Option(False, "--save", "-s", help="Save evaluation report")
):
    """📊 Evaluate prompt quality across multiple dimensions"""
    console.print(f"[bold blue]📊 Evaluating prompts in: {prompts_dir}[/bold blue]")
    
    # Find all prompt files
    prompt_files = list(prompts_dir.glob("*.prompt.yaml")) + list(prompts_dir.glob("*.yaml"))
    
    if not prompt_files:
        console.print("[yellow]⚠️ No prompt files found[/yellow]")
        raise typer.Exit(0)
    
    # Parse metrics
    metric_list = metrics.split(",") if metrics else ["clarity", "effectiveness", "efficiency"]
    
    # Initialize evaluator
    project = PBTProject()
    evaluator = PromptEvaluator(project)
    
    # Evaluate each prompt
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Evaluating {len(prompt_files)} prompts...", total=len(prompt_files))
        
        for prompt_file in prompt_files:
            try:
                prompt_data = load_prompt_file(prompt_file)
                evaluation = evaluator.evaluate_quality(prompt_data, metrics=metric_list)
                
                results.append({
                    "file": prompt_file.name,
                    "scores": evaluation['scores'],
                    "overall": evaluation.get('overall_score', 0)
                })
            except Exception as e:
                results.append({
                    "file": prompt_file.name,
                    "error": str(e)
                })
            
            progress.advance(task)
    
    # Display results
    if output_format == "table":
        table = Table(title="Prompt Quality Evaluation", show_header=True, header_style="bold magenta")
        table.add_column("Prompt File", style="cyan", no_wrap=True)
        
        for metric in metric_list:
            table.add_column(metric.title(), justify="right")
        
        table.add_column("Overall", justify="right", style="bold")
        
        for result in results:
            if "error" in result:
                row = [result["file"]] + ["ERROR"] * (len(metric_list) + 1)
            else:
                row = [result["file"]]
                for metric in metric_list:
                    score = result["scores"].get(metric, 0)
                    color = "green" if score >= 7 else "yellow" if score >= 5 else "red"
                    row.append(f"[{color}]{score:.1f}[/{color}]")
                
                overall = result["overall"]
                color = "green" if overall >= 7 else "yellow" if overall >= 5 else "red"
                row.append(f"[{color}]{overall:.1f}[/{color}]")
            
            table.add_row(*row)
        
        console.print(table)
    
    elif output_format == "json":
        console.print(json.dumps(results, indent=2))
    
    elif output_format == "csv":
        # CSV output
        headers = ["file"] + metric_list + ["overall"]
        console.print(",".join(headers))
        
        for result in results:
            if "error" in result:
                row = [result["file"]] + ["ERROR"] * (len(metric_list) + 1)
            else:
                row = [result["file"]]
                for metric in metric_list:
                    row.append(str(result["scores"].get(metric, 0)))
                row.append(str(result["overall"]))
            
            console.print(",".join(row))
    
    # Save report if requested
    if save_report:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"evaluations/quality_report_{timestamp}.json")
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "metrics": metric_list,
                "results": results
            }, f, indent=2)
        
        console.print(f"\n[green]✅ Report saved to: {report_file}[/green]")

def chunk_command(
    input_file: str = typer.Argument(..., help="File to chunk"),
    strategy: str = typer.Option("prompt_aware", "--strategy", help="Chunking strategy"),
    max_tokens: int = typer.Option(512, "--max-tokens", help="Maximum tokens per chunk"),
    overlap: int = typer.Option(50, "--overlap", help="Token overlap between chunks"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    rag_optimize: bool = typer.Option(False, "--rag", help="Optimize chunks for RAG")
):
    """📄 Create embedding-safe chunks from prompts and content"""
    console.print(f"[bold blue]📄 Chunking file: {input_file}[/bold blue]")
    
    try:
        # Read input file
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Initialize chunker
        project = PBTProject()
        chunker = PromptChunker()
        
        # Determine strategy
        chunk_strategy = ChunkingStrategy[strategy.upper()]
        
        # Create chunks
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Creating chunks...", total=1)
            
            chunks = chunker.chunk(
                content,
                strategy=chunk_strategy,
                max_tokens=max_tokens,
                overlap=overlap,
                optimize_for_rag=rag_optimize
            )
            
            progress.update(task, completed=1)
        
        console.print(f"[green]✅ Created {len(chunks)} chunks[/green]")
        
        # Display chunk summary
        table = Table(title="Chunk Summary", show_header=True, header_style="bold cyan")
        table.add_column("Chunk #", style="cyan", no_wrap=True)
        table.add_column("Tokens", justify="right")
        table.add_column("Preview")
        table.add_column("Embedding Hints")
        
        for i, chunk in enumerate(chunks[:5]):  # Show first 5
            preview = chunk.content[:50] + "..." if len(chunk.content) > 50 else chunk.content
            hints = ", ".join(chunk.embedding_hints[:3]) if chunk.embedding_hints else "None"
            
            table.add_row(
                str(i + 1),
                str(chunk.token_count),
                preview,
                hints
            )
        
        if len(chunks) > 5:
            table.add_row("...", "...", "...", "...")
        
        console.print(table)
        
        # Save chunks if output directory specified
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save individual chunks
            for i, chunk in enumerate(chunks):
                chunk_file = output_dir / f"chunk_{i:03d}.txt"
                with open(chunk_file, 'w') as f:
                    f.write(chunk.content)
                
                # Save metadata
                meta_file = output_dir / f"chunk_{i:03d}_meta.json"
                with open(meta_file, 'w') as f:
                    json.dump({
                        'index': chunk.index,
                        'token_count': chunk.token_count,
                        'embedding_hints': chunk.embedding_hints,
                        'metadata': chunk.metadata
                    }, f, indent=2)
            
            # Save summary
            summary_file = output_dir / "chunks_summary.json"
            with open(summary_file, 'w') as f:
                json.dump({
                    'total_chunks': len(chunks),
                    'strategy': strategy,
                    'config': {
                        'max_tokens': max_tokens,
                        'overlap': overlap,
                        'rag_optimized': rag_optimize
                    },
                    'chunks': [
                        {
                            'index': c.index,
                            'tokens': c.token_count,
                            'hints': c.embedding_hints
                        }
                        for c in chunks
                    ]
                }, f, indent=2)
            
            console.print(f"\n[green]✅ Chunks saved to: {output_dir}/[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Error chunking file: {e}[/red]")
        raise typer.Exit(1)