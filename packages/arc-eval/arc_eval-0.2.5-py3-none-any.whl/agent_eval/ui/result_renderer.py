"""
Result rendering for ARC-Eval CLI.

Provides specialized renderers for different types of evaluation results
including compliance results, reliability metrics, and performance analytics.
"""

import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from agent_eval.core.types import EvaluationResult
from agent_eval.exporters.pdf import PDFExporter
from agent_eval.exporters.csv import CSVExporter  
from agent_eval.exporters.json import JSONExporter

console = Console()


class ResultRenderer:
    """Handles rendering of evaluation results in various formats."""
    
    def __init__(self):
        self.console = console
    
    def display_agent_judge_results(self, improvement_report: dict, domain: str, 
                                   performance_metrics: Optional[dict] = None, 
                                   reliability_metrics: Optional[dict] = None) -> None:
        """Display Agent-as-a-Judge specific results with continuous feedback."""
        console.print(f"\n[bold blue]🤖 Agent-as-a-Judge Improvement Report[/bold blue]")
        console.print("[blue]" + "═" * 60 + "[/blue]")
        
        # Summary metrics
        summary = improvement_report.get("summary", {})
        console.print(f"\n[bold green]📊 Evaluation Summary:[/bold green]")
        console.print(f"• Total Scenarios: {summary.get('total_scenarios', 0)}")
        console.print(f"• Passed: [green]{summary.get('passed', 0)}[/green]")
        console.print(f"• Failed: [red]{summary.get('failed', 0)}[/red]")  
        console.print(f"• Warnings: [yellow]{summary.get('warnings', 0)}[/yellow]")
        console.print(f"• Pass Rate: [{'green' if summary.get('pass_rate', 0) > 0.8 else 'yellow'}]{summary.get('pass_rate', 0):.1%}[/]")
        console.print(f"• Average Confidence: {summary.get('average_confidence', 0):.2f}")
        console.print(f"• Total Cost: [dim]${summary.get('total_cost', 0):.4f}[/dim]")
        
        # Check if verification was used and display verification metrics
        detailed_results = improvement_report.get("detailed_results", [])
        verification_used = any(
            hasattr(result, "verification") and result.get("verification") 
            for result in detailed_results
        )
        
        if verification_used:
            console.print(f"\n[bold cyan]🔍 Verification Layer:[/bold cyan]")
            # Calculate verification stats from detailed results
            verified_count = 0
            total_with_verification = 0
            avg_confidence_delta = 0
            
            for result in detailed_results:
                verification = result.get("verification")
                if verification:
                    total_with_verification += 1
                    if verification.get("verified", False):
                        verified_count += 1
                    avg_confidence_delta += abs(verification.get("confidence_delta", 0))
            
            if total_with_verification > 0:
                verification_rate = verified_count / total_with_verification
                avg_confidence_delta = avg_confidence_delta / total_with_verification
                
                console.print(f"• Verification Rate: [{'green' if verification_rate > 0.8 else 'yellow'}]{verification_rate:.1%}[/]")
                console.print(f"• Avg Confidence Delta: {avg_confidence_delta:.2f}")
                console.print(f"• Verified Judgments: [green]{verified_count}[/green]/{total_with_verification}")
        
        # Display bias detection results
        bias_detection = improvement_report.get("bias_detection")
        if bias_detection:
            console.print(f"\n[bold magenta]⚖️ Bias Detection:[/bold magenta]")
            
            # Overall bias risk with color coding
            risk_level = bias_detection.get("overall_risk", "unknown")
            risk_color = "green" if risk_level == "low" else "yellow" if risk_level == "medium" else "red"
            console.print(f"• Overall Bias Risk: [{risk_color}]{risk_level.upper()}[/{risk_color}]")
            
            # Individual bias scores
            length_bias = bias_detection.get("length_bias", 0)
            position_bias = bias_detection.get("position_bias", 0)
            style_bias = bias_detection.get("style_bias", 0)
            
            console.print(f"• Length Bias Score: {length_bias:.3f}")
            console.print(f"• Position Bias Score: {position_bias:.3f}")
            console.print(f"• Style Bias Score: {style_bias:.3f}")
            console.print(f"• Evaluations Analyzed: {bias_detection.get('total_evaluations', 0)}")
            
            # Show bias recommendations if any
            recommendations = bias_detection.get("recommendations", [])
            if recommendations:
                console.print(f"\n[bold magenta]🔧 Bias Mitigation:[/bold magenta]")
                for i, rec in enumerate(recommendations[:3], 1):  # Show top 3 recommendations
                    console.print(f"  {i}. {rec}")
        
        # Continuous feedback
        feedback = improvement_report.get("continuous_feedback", {})
        
        if feedback.get("strengths"):
            console.print(f"\n[bold green]💪 Strengths:[/bold green]")
            for strength in feedback["strengths"]:
                console.print(f"  ✅ {strength}")
        
        if feedback.get("training_suggestions"):
            console.print(f"\n[bold purple]📚 Training Suggestions:[/bold purple]")
            for suggestion in feedback["training_suggestions"]:
                console.print(f"  📖 {suggestion}")
        
        # Performance metrics display
        if performance_metrics:
            console.print(f"\n[bold cyan]⚡ Performance Metrics:[/bold cyan]")
            
            runtime = performance_metrics.get("runtime", {})
            memory = performance_metrics.get("memory", {})
            latency = performance_metrics.get("latency", {})
            cost_efficiency = performance_metrics.get("cost_efficiency", {})
            resources = performance_metrics.get("resources", {})
            
            console.print(f"• Total Execution Time: {runtime.get('total_execution_time', 0):.2f}s")
            console.print(f"• Judge Execution Time: {runtime.get('judge_execution_time', 0):.2f}s")
            console.print(f"• Throughput: {runtime.get('scenarios_per_second', 0):.2f} scenarios/sec")
            console.print(f"• Peak Memory: {memory.get('peak_memory_mb', 0):.1f} MB")
            console.print(f"• P95 Latency: {latency.get('p95_seconds', 0):.3f}s")
            console.print(f"• Cost per Scenario: ${cost_efficiency.get('cost_per_scenario', 0):.4f}")
            
            if resources.get('avg_cpu_percent'):
                console.print(f"• Avg CPU Usage: {resources.get('avg_cpu_percent', 0):.1f}%")
        
        # Reliability metrics display
        if reliability_metrics:
            console.print(f"\n[bold magenta]🔧 Reliability Metrics:[/bold magenta]")
            
            console.print(f"• Overall Reliability Score: {reliability_metrics.get('overall_reliability_score', 0):.2f}")
            console.print(f"• Tool Call Accuracy: {reliability_metrics.get('tool_call_accuracy', 0):.1%}")
            console.print(f"• Error Recovery Rate: {reliability_metrics.get('error_recovery_rate', 0):.1%}")
            console.print(f"• Framework Detection Rate: {reliability_metrics.get('framework_detection_rate', 0):.1%}")
            
            # Show framework distribution
            framework_dist = reliability_metrics.get('framework_distribution', {})
            if framework_dist:
                frameworks = ', '.join([f"{fw}: {count}" for fw, count in framework_dist.items()])
                console.print(f"• Framework Distribution: {frameworks}")
            
            # Show reliability issues if any
            issues = reliability_metrics.get('reliability_issues', [])
            if issues and issues != ["No major reliability issues detected"]:
                console.print(f"\n[bold red]⚠️  Reliability Issues:[/bold red]")
                for issue in issues[:3]:  # Show top 3 issues
                    console.print(f"  • {issue}")
        
        if feedback.get("compliance_gaps"):
            console.print(f"\n[bold red]⚠️  Compliance Gaps:[/bold red]")
            console.print(f"Failed scenarios: {', '.join(feedback['compliance_gaps'])}")
        
        console.print(f"\n[dim]💡 Agent-as-a-Judge provides continuous feedback to improve your agent's {domain} compliance performance.[/dim]")
    
    def display_results(self, results: List[EvaluationResult], output_format: str, 
                       dev_mode: bool, workflow_mode: bool, domain: str = "finance",
                       summary_only: bool = False, format_template: Optional[str] = None,
                       improvement_report: Optional[dict] = None,
                       no_interaction: bool = False) -> None:
        """Display evaluation results in the specified format."""
        
        if output_format == "json":
            click.echo(json.dumps([r.to_dict() for r in results], indent=2))
            return
        
        if output_format == "csv":
            # Simple CSV output for scripting
            click.echo("scenario,status,severity,compliance,description")
            for result in results:
                click.echo(f"{result.scenario_name},{result.status},{result.severity},{';'.join(result.compliance)},{result.description}")
            return
        
        # Table output (default)
        self._display_table_results(results, dev_mode, workflow_mode, domain, summary_only, format_template)
        
        # Interactive Results Analyst Integration - Replace dense recommendations
        if improvement_report:
            failed_results = [r for r in results if not r.passed]
            if failed_results:
                try:
                    from agent_eval.analysis.interactive_analyst import InteractiveAnalyst
                    
                    # Check if we can run interactive mode
                    # Enable interactive mode unless explicitly disabled or no API key
                    can_interact = not no_interaction and os.getenv("ANTHROPIC_API_KEY")
                    if can_interact:
                        analyst = InteractiveAnalyst(
                            improvement_report=improvement_report,
                            judge_results=improvement_report.get("detailed_results", []),
                            domain=domain,
                            performance_metrics=improvement_report.get("performance_metrics"),
                            reliability_metrics=improvement_report.get("reliability_metrics")
                        )
                        
                        # Display concise summary + start interactive chat
                        analyst.display_concise_summary_and_chat(console)
                    else:
                        # Fallback: show condensed recommendations for non-interactive mode
                        analyst = InteractiveAnalyst(
                            improvement_report=improvement_report,
                            judge_results=improvement_report.get("detailed_results", []),
                            domain=domain,
                            performance_metrics=improvement_report.get("performance_metrics"),
                            reliability_metrics=improvement_report.get("reliability_metrics")
                        )
                        analyst.display_condensed_recommendations(console)
                except (ImportError, ValueError):
                    # Fallback to original display if InteractiveAnalyst fails - but this is already handled in _display_table_results
                    pass
    
    def _display_table_results(self, results: List[EvaluationResult], dev_mode: bool, 
                              workflow_mode: bool, domain: str = "finance", 
                              summary_only: bool = False, format_template: Optional[str] = None) -> None:
        """Display results in a rich table format."""
        
        # Summary statistics
        total_scenarios = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)
        critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
        high_failures = sum(1 for r in results if r.severity == "high" and not r.passed)
        medium_failures = sum(1 for r in results if r.severity == "medium" and not r.passed)
        
        # Dynamic header based on domain
        domains_info = self._get_domain_info()
        domain_title = domains_info.get(domain, {}).get("name", "Compliance")
        
        # Enhanced summary header with executive dashboard
        console.print(f"\n[bold blue on white] 📊 {domain_title} Evaluation Report [/bold blue on white]")
        console.print("[blue]" + "═" * 70 + "[/blue]")
        
        # Executive summary box
        summary_table = Table(
            show_header=False,
            box=None,
            expand=True,
            padding=(0, 2)
        )
        summary_table.add_column("", style="bold", width=20)
        summary_table.add_column("", style="", width=15, justify="center")
        summary_table.add_column("", style="bold", width=20)
        summary_table.add_column("", style="", width=15, justify="center")
        
        # Calculate pass rate
        pass_rate = (passed / total_scenarios * 100) if total_scenarios > 0 else 0
        
        # Risk status indicator
        if critical_failures > 0:
            risk_status = "[red]🔴 HIGH RISK[/red]"
        elif high_failures > 0:
            risk_status = "[yellow]🟡 MEDIUM RISK[/yellow]"
        elif medium_failures > 0:
            risk_status = "[blue]🔵 LOW RISK[/blue]"
        else:
            risk_status = "[green]🟢 COMPLIANT[/green]"
        
        summary_table.add_row(
            "📈 Pass Rate:", f"[bold]{pass_rate:.1f}%[/bold]",
            "⚠️  Risk Level:", risk_status
        )
        summary_table.add_row(
            "✅ Passed:", f"[green]{passed}[/green]",
            "❌ Failed:", f"[red]{failed}[/red]"
        )
        summary_table.add_row(
            "🔴 Critical:", f"[red]{critical_failures}[/red]", 
            "🟡 High:", f"[yellow]{high_failures}[/yellow]"
        )
        summary_table.add_row(
            "🔵 Medium:", f"[blue]{medium_failures}[/blue]",
            "📊 Total:", f"[bold]{total_scenarios}[/bold]"
        )
        
        console.print(summary_table)
        console.print("[blue]" + "─" * 70 + "[/blue]")
        
        # Show compliance framework summary
        compliance_frameworks = set()
        failed_frameworks = set()
        for result in results:
            compliance_frameworks.update(result.compliance)
            if not result.passed:
                failed_frameworks.update(result.compliance)
        
        # Compliance Framework Dashboard
        if compliance_frameworks:
            console.print("\n[bold blue]⚖️  Compliance Framework Dashboard[/bold blue]")
            
            # Create framework summary table
            framework_table = Table(
                show_header=True,
                header_style="bold white on blue",
                border_style="blue",
                expand=True
            )
            framework_table.add_column("Framework", style="bold", width=15)
            framework_table.add_column("Status", style="bold", width=12, justify="center")
            framework_table.add_column("Scenarios", style="", width=10, justify="center")
            framework_table.add_column("Pass Rate", style="", width=12, justify="center")
            framework_table.add_column("Issues", style="", width=20)
            
            # Calculate framework-specific metrics
            for framework in sorted(compliance_frameworks):
                framework_results = [r for r in results if framework in r.compliance]
                total_scenarios = len(framework_results)
                passed_scenarios = sum(1 for r in framework_results if r.passed)
                failed_scenarios = total_scenarios - passed_scenarios
                pass_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
                
                # Determine status
                if failed_scenarios == 0:
                    status = "[green]✅ COMPLIANT[/green]"
                elif any(r.severity == "critical" and not r.passed for r in framework_results):
                    status = "[red]🔴 CRITICAL[/red]"
                elif any(r.severity == "high" and not r.passed for r in framework_results):
                    status = "[yellow]🟡 HIGH RISK[/yellow]"
                else:
                    status = "[blue]🔵 MEDIUM[/blue]"
                
                # Issue summary
                critical_issues = sum(1 for r in framework_results if r.severity == "critical" and not r.passed)
                high_issues = sum(1 for r in framework_results if r.severity == "high" and not r.passed)
                
                issue_summary = ""
                if critical_issues > 0:
                    issue_summary += f"🔴 {critical_issues} Critical"
                if high_issues > 0:
                    if issue_summary:
                        issue_summary += ", "
                    issue_summary += f"🟡 {high_issues} High"
                if not issue_summary:
                    issue_summary = "[dim]No issues[/dim]"
                
                framework_table.add_row(
                    framework,
                    status,
                    f"{passed_scenarios}/{total_scenarios}",
                    f"{pass_rate:.1f}%",
                    issue_summary
                )
            
            console.print(framework_table)
            console.print("[blue]" + "─" * 70 + "[/blue]")
        
        # Executive Summary only mode - skip detailed table
        if summary_only:
            console.print(f"\n[bold blue]📋 Executive Summary Generated[/bold blue]")
            console.print("[dim]Use without --summary-only to see detailed scenario results[/dim]")
            return
        
        # Detailed results table
        if failed > 0 or dev_mode:
            console.print("\n[bold blue]📊 Detailed Evaluation Results[/bold blue]")
            
            # Enhanced table with better styling for executives
            table = Table(
                show_header=True, 
                header_style="bold white on blue",
                border_style="blue",
                row_styles=["", "dim"],
                expand=True,
                title_style="bold blue"
            )
            
            table.add_column("🏷️  Status", style="bold", width=12, justify="center")
            table.add_column("⚡ Risk Level", style="bold", width=12, justify="center") 
            table.add_column("📋 Scenario", style="", min_width=25)
            table.add_column("⚖️  Compliance Frameworks", style="", min_width=20)
            if dev_mode:
                table.add_column("🔍 Technical Details", style="dim", min_width=30)
            
            # Sort results: Critical failures first, then by severity
            sorted_results = sorted(results, key=lambda r: (
                r.passed,  # Failed first
                {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(r.severity, 4)
            ))
            
            for result in sorted_results:
                # Enhanced status presentation
                if result.passed:
                    status_display = "[green]✅ PASS[/green]"
                else:
                    status_display = "[red]❌ FAIL[/red]"
                
                # Enhanced severity with risk indicators
                severity_display = {
                    "critical": "[red]🔴 CRITICAL[/red]",
                    "high": "[yellow]🟡 HIGH[/yellow]", 
                    "medium": "[blue]🔵 MEDIUM[/blue]",
                    "low": "[dim]⚪ LOW[/dim]"
                }.get(result.severity, result.severity.upper())
                
                # Improved compliance formatting
                compliance_frameworks = result.compliance
                if len(compliance_frameworks) > 3:
                    compliance_display = f"{', '.join(compliance_frameworks[:3])}\n[dim]+{len(compliance_frameworks)-3} more[/dim]"
                else:
                    compliance_display = ", ".join(compliance_frameworks)
                
                # Scenario name with truncation for readability
                scenario_display = result.scenario_name
                if len(scenario_display) > 40:
                    scenario_display = scenario_display[:37] + "..."
                
                row = [
                    status_display,
                    severity_display,
                    scenario_display,
                    compliance_display,
                ]
                
                if dev_mode:
                    details = result.failure_reason or "[dim]Passed all checks[/dim]"
                    if len(details) > 50:
                        details = details[:47] + "..."
                    row.append(details)
                
                table.add_row(*row)
            
            console.print(table)
        
        # Risk assessment for workflow mode
        if workflow_mode and critical_failures > 0:
            console.print("\n[bold red]Risk Assessment[/bold red]")
            console.print("🔴 Critical compliance violations detected")
            
            failed_results = [r for r in results if not r.passed]
            compliance_frameworks = set()
            for result in failed_results:
                compliance_frameworks.update(result.compliance)
            
            if compliance_frameworks:
                console.print(f"📋 Regulatory frameworks affected: {', '.join(sorted(compliance_frameworks))}")
            console.print("⚡ Immediate remediation required")
    
    def display_timing_metrics(self, evaluation_time: float, input_size: int, result_count: int) -> None:
        """Display enhanced timing and performance metrics."""
        console.print("\n[bold blue]⚡ Performance Analytics[/bold blue]")
        console.print("[blue]" + "═" * 70 + "[/blue]")
        
        # Create performance metrics table
        perf_table = Table(
            show_header=False,
            box=None,
            expand=True,
            padding=(0, 2)
        )
        perf_table.add_column("", style="bold", width=25)
        perf_table.add_column("", style="", width=20, justify="center")
        perf_table.add_column("", style="bold", width=25)
        perf_table.add_column("", style="", width=20, justify="center")
        
        # Format input size
        if input_size < 1024:
            size_str = f"{input_size} bytes"
        elif input_size < 1024 * 1024:
            size_str = f"{input_size / 1024:.1f} KB"
        else:
            size_str = f"{input_size / (1024 * 1024):.1f} MB"
        
        # Calculate processing speed
        scenarios_per_sec = result_count / evaluation_time if evaluation_time > 0 else 0
        
        # Performance grade
        if evaluation_time < 1.0:
            grade = "[green]🚀 EXCELLENT[/green]"
        elif evaluation_time < 5.0:
            grade = "[blue]⚡ GOOD[/blue]"
        elif evaluation_time < 15.0:
            grade = "[yellow]⏳ MODERATE[/yellow]"
        else:
            grade = "[red]🐌 SLOW[/red]"
        
        # Memory efficiency
        if input_size < 1024 * 1024:  # < 1MB
            memory_grade = "[green]✅ EFFICIENT[/green]"
        elif input_size < 10 * 1024 * 1024:  # < 10MB
            memory_grade = "[blue]📊 MODERATE[/blue]"
        else:
            memory_grade = "[yellow]⚠️  HEAVY[/yellow]"
        
        perf_table.add_row(
            "⏱️  Evaluation Time:", f"[bold]{evaluation_time:.3f}s[/bold]",
            "📊 Input Size:", f"[bold]{size_str}[/bold]"
        )
        perf_table.add_row(
            "🚀 Processing Speed:", f"[bold]{scenarios_per_sec:.1f}/sec[/bold]",
            "📋 Scenarios Processed:", f"[bold]{result_count}[/bold]"
        )
        perf_table.add_row(
            "⚡ Performance Grade:", grade,
            "💾 Memory Efficiency:", memory_grade
        )
        
        # Throughput analysis
        data_per_sec = input_size / evaluation_time if evaluation_time > 0 else 0
        if data_per_sec < 1024:
            throughput_str = f"{data_per_sec:.1f} B/s"
        elif data_per_sec < 1024 * 1024:
            throughput_str = f"{data_per_sec / 1024:.1f} KB/s"
        else:
            throughput_str = f"{data_per_sec / (1024 * 1024):.1f} MB/s"
        
        perf_table.add_row(
            "📈 Data Throughput:", f"[bold]{throughput_str}[/bold]",
            "🎯 Avg Time/Scenario:", f"[bold]{evaluation_time / result_count * 1000:.1f}ms[/bold]"
        )
        
        console.print(perf_table)
        console.print("[blue]" + "─" * 70 + "[/blue]")
        
        # Performance recommendations
        console.print("\n[bold blue]💡 Performance Insights[/bold blue]")
        
        recommendations = []
        if evaluation_time > 30:
            recommendations.append("🐌 [yellow]Long evaluation time detected. Consider smaller input batches.[/yellow]")
        if input_size > 10 * 1024 * 1024:
            recommendations.append("💾 [yellow]Large input detected. Consider data preprocessing or streaming.[/yellow]")
        if scenarios_per_sec < 1:
            recommendations.append("⚡ [yellow]Low processing speed. Check input complexity or system resources.[/yellow]")
        
        if not recommendations:
            if evaluation_time < 1.0:
                recommendations.append("🚀 [green]Excellent performance! Your setup is optimized.[/green]")
            else:
                recommendations.append("✅ [green]Good performance within acceptable ranges.[/green]")
        
        for rec in recommendations:
            console.print(f"  • {rec}")
        
        # Scaling projections
        if scenarios_per_sec > 0:
            console.print(f"\n[bold blue]📊 Scaling Projections[/bold blue]")
            console.print(f"• 100 scenarios: ~{100 / scenarios_per_sec:.1f}s")
            console.print(f"• 1,000 scenarios: ~{1000 / scenarios_per_sec:.1f}s")
            if scenarios_per_sec >= 1:
                console.print(f"• 10,000 scenarios: ~{10000 / scenarios_per_sec / 60:.1f} minutes")
    
    def _get_domain_info(self) -> dict:
        """Get centralized domain information to avoid duplication."""
        return {
            "finance": {
                "name": "Financial Services Compliance",
                "description": "Enterprise-grade evaluations for financial AI systems",
                "frameworks": ["SOX", "KYC", "AML", "PCI-DSS", "GDPR", "FFIEC", "DORA", "OFAC", "CFPB", "EU-AI-ACT"],
                "scenarios": 110,
                "use_cases": "Banking, Fintech, Payment Processing, Insurance, Investment",
                "examples": "Transaction approval, KYC verification, Fraud detection, Credit scoring",
                "categories": [
                    "SOX & Financial Reporting Compliance",
                    "KYC & AML Compliance Framework", 
                    "PCI-DSS & Data Protection",
                    "Fraud Detection & Risk Management",
                    "Investment & Trading Compliance",
                    "Insurance & Actuarial Analysis",
                    "Digital Banking & API Security"
                ]
            },
            "security": {
                "name": "Cybersecurity & AI Agent Security", 
                "description": "AI safety evaluations for security-critical applications",
                "frameworks": ["OWASP-LLM-TOP-10", "NIST-AI-RMF", "ISO-27001", "SOC2-TYPE-II", "MITRE-ATTACK"],
                "scenarios": 120,
                "use_cases": "AI Agents, Chatbots, Code Generation, Security Tools",
                "examples": "Prompt injection, Data leakage, Code security, Access control",
                "categories": [
                    "OWASP LLM Top 10 (Prompt Injection, Data Leakage, etc.)",
                    "Purple Llama CyberSecEval Benchmarks",
                    "Agent-Specific Security Testing",
                    "Multi-Step Attack Chain Detection",
                    "Automated Patch Generation Assessment"
                ]
            },
            "ml": {
                "name": "ML Infrastructure & Safety",
                "description": "ML ops, safety, and bias evaluation for AI systems",
                "frameworks": ["NIST-AI-RMF", "IEEE-2857", "ISO-23053", "GDPR-AI", "EU-AI-ACT"],
                "scenarios": 107,
                "use_cases": "ML Models, AI Pipelines, Model Serving, Training",
                "examples": "Bias detection, Model safety, Explainability, Performance",
                "categories": [
                    "Bias Detection & Fairness Assessment",
                    "Explainability & Interpretability Testing",
                    "Model Safety & Robustness Evaluation",
                    "Data Quality & Pipeline Validation",
                    "Performance Monitoring & Drift Detection",
                    "Multi-Modal Model Assessment"
                ]
            }
        }