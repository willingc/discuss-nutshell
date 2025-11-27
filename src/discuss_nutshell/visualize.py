"""Visualize Discourse posts as cards."""

import json
from pathlib import Path
from typing import Any

import gradio as gr


def load_posts_json(file_path: str | Path) -> list[dict[str, Any]]:
    """Load posts from a JSON file.

    Parameters
    ----------
    file_path : str | Path
        Path to the JSON file containing posts.

    Returns
    -------
    list[dict[str, Any]]
        List of post dictionaries.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    json.JSONDecodeError
        If the file is not valid JSON.
    """
    path = Path(file_path)
    if not path.exists():
        msg = f"File not found: {file_path}"
        raise FileNotFoundError(msg)

    with path.open(encoding="utf-8") as f:
        return json.load(f)


def create_post_card(post: dict[str, Any]) -> str:
    """Create an HTML card for a single post.

    Parameters
    ----------
    post : dict[str, Any]
        Post dictionary with keys: id, author, number, created_at, clean_content.

    Returns
    -------
    str
        HTML string representing the post card.
    """
    post_id = post.get("id", "Unknown")
    author = post.get("author", "Unknown")
    number = post.get("number", "?")
    created_at = post.get("created_at", "Unknown")
    content = post.get("clean_content", "")

    # Escape HTML special characters in content
    content_escaped = (
        content.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )

    # Replace newlines with <br> for HTML display
    content_formatted = content_escaped.replace("\n", "<br>")

    return f"""
    <div style="
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    ">
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #f0f0f0;
        ">
            <div>
                <strong style="color: #1976d2; font-size: 14px;">Post #{number}</strong>
                <span style="color: #666; font-size: 12px; margin-left: 8px;">ID: {post_id}</span>
            </div>
            <div style="text-align: right;">
                <div style="color: #333; font-weight: 500; font-size: 14px;">{author}</div>
                <div style="color: #999; font-size: 12px;">{created_at}</div>
            </div>
        </div>
        <div style="
            color: #333;
            line-height: 1.6;
            font-size: 14px;
            max-height: 400px;
            overflow-y: auto;
        ">
            {content_formatted}
        </div>
    </div>
    """


def display_posts(file_path: str | Path) -> str:
    """Load and display all posts as HTML cards.

    Parameters
    ----------
    file_path : str | Path
        Path to the JSON file containing posts.

    Returns
    -------
    str
        HTML string containing all post cards.
    """
    posts = load_posts_json(file_path)
    cards = [create_post_card(post) for post in posts]
    return f"""
    <div style="
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f5f5f5;
    ">
        <h1 style="
            color: #1976d2;
            margin-bottom: 24px;
            font-size: 24px;
            text-align: center;
        ">Discourse Posts</h1>
        <div>
            {"".join(cards)}
        </div>
    </div>
    """


def create_visualization_app(json_file: str | Path) -> gr.Blocks:
    """Create a Gradio app to visualize posts.

    Parameters
    ----------
    json_file : str | Path
        Path to the JSON file containing posts.

    Returns
    -------
    gr.Blocks
        Gradio Blocks interface for the visualization.
    """
    file_path = Path(json_file)
    if not file_path.exists():
        msg = f"File not found: {json_file}"
        raise FileNotFoundError(msg)

    posts = load_posts_json(file_path)
    total_posts = len(posts)

    def update_display(post_number: int) -> str:
        """Update the display based on selected post number.

        Parameters
        ----------
        post_number : int
            The post number to display (1-indexed).

        Returns
        -------
        str
            HTML content for the selected post.
        """
        if post_number < 1 or post_number > total_posts:
            return "<p>Invalid post number</p>"
        post = posts[post_number - 1]
        return create_post_card(post)

    def show_all_posts() -> str:
        """Display all posts.

        Returns
        -------
        str
            HTML content for all posts.
        """
        return display_posts(file_path)

    with gr.Blocks(
        title="Discourse Posts Visualization", theme=gr.themes.Soft()
    ) as app:
        gr.Markdown(
            f"# Discourse Posts Visualization\n\n**Total Posts:** {total_posts}"
        )
        with gr.Row():
            with gr.Column(scale=1):
                post_slider = gr.Slider(
                    minimum=1,
                    maximum=total_posts,
                    step=1,
                    value=1,
                    label="Post Number",
                )
                view_single_btn = gr.Button("View Single Post", variant="primary")
                view_all_btn = gr.Button("View All Posts", variant="secondary")
            with gr.Column(scale=3):
                output = gr.HTML(label="Post Content")
                view_single_btn.click(
                    fn=update_display,
                    inputs=post_slider,
                    outputs=output,
                )
                view_all_btn.click(
                    fn=show_all_posts,
                    outputs=output,
                )
                # Auto-update when slider changes
                post_slider.change(
                    fn=update_display,
                    inputs=post_slider,
                    outputs=output,
                )

    return app


def main(json_file: str | Path | None = None) -> None:
    """Launch the visualization app.

    Parameters
    ----------
    json_file : str | Path | None, optional
        Path to the JSON file. If None, defaults to data/104906_all_posts.json.
    """
    if json_file is None:
        current_path = Path.cwd()
        json_file = current_path / "data" / "104906_all_posts.json"

    app = create_visualization_app(json_file)
    app.launch()


if __name__ == "__main__":
    main()
