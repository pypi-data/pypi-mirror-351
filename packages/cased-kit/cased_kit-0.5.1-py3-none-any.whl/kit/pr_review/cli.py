"""CLI interface for PR review functionality."""

from pathlib import Path

import click

from .reviewer import PRReviewer


@click.command("review")
@click.argument("pr_url", required=False)
@click.option("--config", "-c", type=click.Path(), help="Path to config file (default: ~/.kit/review-config.yaml)")
@click.option("--dry-run", "-n", is_flag=True, help="Don't post comment, just show what would be posted")
@click.option("--init-config", is_flag=True, help="Create a default configuration file and exit")
@click.option("--agentic", is_flag=True, help="Use agentic multi-turn analysis (experimental)")
@click.option("--agentic-turns", type=int, default=20, help="Maximum turns for agentic analysis (default: 20)")
def review(pr_url: str, config: str, dry_run: bool, init_config: bool, agentic: bool, agentic_turns: int):
    """Review a GitHub PR using kit's analysis capabilities.

    Examples:

    # Initialize configuration
    kit review --init-config

    # Review a PR (posts comment by default)
    kit review https://github.com/cased/kit/pull/47

    # Dry run (don't post comment)
    kit review --dry-run https://github.com/cased/kit/pull/47

    # Use agentic multi-turn analysis (experimental)
    kit review --agentic https://github.com/cased/kit/pull/47

    # Agentic mode with custom turn limit
    kit review --agentic --agentic-turns 30 https://github.com/cased/kit/pull/47
    """
    if init_config:
        try:
            # Create default config without needing ReviewConfig.from_file()
            config_path = config or "~/.kit/review-config.yaml"
            config_path = Path(config_path).expanduser()

            # Create a temporary ReviewConfig just to use the create_default_config_file method
            from .config import GitHubConfig, LLMConfig, LLMProvider, ReviewConfig

            temp_config = ReviewConfig(
                github=GitHubConfig(token="temp"),
                llm=LLMConfig(provider=LLMProvider.ANTHROPIC, model="temp", api_key="temp"),
            )

            created_path = temp_config.create_default_config_file(str(config_path))
            click.echo(f"✅ Created default config file at: {created_path}")
            click.echo("\n📝 Next steps:")
            click.echo("1. Edit the config file to add your tokens")
            click.echo("2. Set GITHUB_TOKEN and ANTHROPIC_API_KEY environment variables, or")
            click.echo("3. Update the config file with your actual tokens")
            return
        except Exception as e:
            click.echo(f"❌ Failed to create config: {e}", err=True)
            raise click.Abort()

    if not pr_url:
        click.echo("❌ PR URL is required", err=True)
        raise click.Abort()

    try:
        # Load configuration
        review_config = ReviewConfig.from_file(config)

        # Override comment posting if dry run
        if dry_run:
            review_config.post_as_comment = False
            click.echo("🔍 Dry run mode - will not post comments")

        # Configure agentic settings if requested
        if agentic:
            review_config.agentic_max_turns = agentic_turns
            click.echo(f"🤖 Agentic mode enabled - max turns: {agentic_turns}")

        # Create reviewer and run review
        if agentic:
            from .agentic_reviewer import AgenticPRReviewer

            reviewer = AgenticPRReviewer(review_config)
            comment = reviewer.review_pr_agentic(pr_url)
        else:
            reviewer = PRReviewer(review_config)
            comment = reviewer.review_pr(pr_url)

        if dry_run:
            click.echo("\n" + "=" * 60)
            click.echo("REVIEW COMMENT THAT WOULD BE POSTED:")
            click.echo("=" * 60)
            click.echo(comment)
            click.echo("=" * 60)
        else:
            click.echo("✅ Review completed and comment posted!")

    except ValueError as e:
        click.secho(f"❌ Configuration error: {e}", fg=click.colors.RED)
        click.echo("\n💡 Try running: kit review --init-config")
        click.exit(1)
    except Exception as e:
        click.echo(f"❌ Review failed: {e}", err=True)
        raise click.Abort()
