import os
import gradio as gr
from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent
from src.tools.academic_polisher import academic_polisher
from src.tools.format_citation import format_citation
from src.tools.draft_paper import draft_paper
from src.tools.synthesize import synthesize_findings
from run_research_agent import get_research_tools


def run_research_agent(prompt):
    if not prompt or not prompt.strip():
        return "Vui lòng nhập yêu cầu nghiên cứu."
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        provider = OpenAIProvider(model_name="gpt-4o", api_key=api_key)
        tools = get_research_tools()
        agent = ReActAgent(llm=provider, tools=tools, max_steps=10)
        return agent.run(prompt)
    except Exception as e:
        return f"Lỗi hệ thống: {e}"


def run_polisher(text, tone):
    if not text or not text.strip():
        return "Vui lòng nhập văn bản nháp."
    try:
        return academic_polisher(text, tone)
    except Exception as e:
        return f"Lỗi biên tập: {e}"


def run_citation(title, authors, year, style):
    if not title or not title.strip():
        return "Vui lòng nhập tiêu đề bài báo."
    try:
        try:
            year_int = int(year)
        except ValueError:
            year_int = 2023
        return format_citation(title, authors, year_int, style)
    except Exception as e:
        return f"Lỗi tạo trích dẫn: {e}"


def run_draft_paper(topic, synthesis_notes, citation_style):
    if not topic or not topic.strip():
        return "Vui lòng nhập chủ đề nghiên cứu."
    if not synthesis_notes or not synthesis_notes.strip():
        return "Vui lòng nhập ghi chú tổng hợp nghiên cứu (synthesis notes)."
    try:
        return draft_paper(topic, synthesis_notes, citation_style)
    except Exception as e:
        return f"Lỗi tạo bản thảo: {e}"


custom_css = """
body { background-color: #f7f9fc; }
.title-header { text-align: center; margin-bottom: 20px; }
.title-header h1 {
    font-size: 2.5rem; font-weight: 800; color: #1e3a8a;
    background: linear-gradient(90deg, #1e3a8a, #3b82f6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}
.title-header p { font-size: 1.1rem; color: #4b5563; }
.card-panel {
    background: white; border-radius: 12px; padding: 20px;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
}
"""

with gr.Blocks() as demo:

    gr.HTML("""
        <div class="title-header">
            <h1>🔬 AI Scientific Research Assistant Agent</h1>
            <p>Giải pháp AI hỗ trợ viết bài nghiên cứu khoa học chuyên nghiệp dựa trên kiến trúc ReAct & Telemetry công nghiệp.</p>
        </div>
    """)

    with gr.Tabs():

        # Tab 1: Full ReAct Research Pipeline
        with gr.TabItem("🧠 ReAct Research Agent"):
            gr.Markdown("""
            ### Luồng Lập luận ReAct Tự động (Reasoning & Acting)
            Agent tự động đi qua toàn bộ pipeline 6 bước: **Làm rõ → Tìm kiếm → So sánh → Tổng hợp → Soạn thảo → Đánh bóng**.
            Nhập yêu cầu nghiên cứu và nhấn kích hoạt.
            """)
            with gr.Row():
                with gr.Column(scale=1):
                    research_prompt = gr.Textbox(
                        label="Yêu cầu Nghiên cứu (Research Prompt)",
                        placeholder="Ví dụ: Write a complete academic paper on deep learning for cancer detection.",
                        lines=4,
                        value="I want you to search the AI paper that refer to classifying cancer"
                    )
                    submit_btn = gr.Button("🚀 Kích Hoạt Agent", variant="primary")
                    gr.Markdown("#### 💡 Truy vấn Mẫu:")
                    gr.Examples(
                        examples=[
                            ["I want you to search the AI paper that refer to classifying cancer"],
                            ["Write a complete academic paper on Retrieval-Augmented Generation (RAG)"],
                            ["Search attention is all you need paper and format in IEEE"],
                            ["Find papers about unsupervised anomalous sound detection and draft a literature review"],
                        ],
                        inputs=research_prompt
                    )
                with gr.Column(scale=2):
                    gr.Markdown("#### 📊 Kết quả Phản hồi")
                    final_output = gr.Markdown(
                        label="Câu trả lời cuối cùng (Final Answer)",
                        value="*Kết quả phản hồi khoa học từ Agent sẽ xuất hiện ở đây...*"
                    )
            submit_btn.click(fn=run_research_agent, inputs=research_prompt, outputs=final_output)

        # Tab 2: Direct Paper Drafter
        with gr.TabItem("📝 Paper Drafter"):
            gr.Markdown("""
            ### Công cụ Soạn thảo Bài báo Trực tiếp
            Nhập chủ đề và ghi chú tổng hợp nghiên cứu, công cụ sẽ tạo toàn bộ bản thảo bài báo khoa học
            gồm: Abstract, Introduction, Related Work, Methodology, Results, Conclusion, References.
            """)
            with gr.Row():
                with gr.Column():
                    draft_topic = gr.Textbox(
                        label="Chủ đề Nghiên cứu (Research Topic)",
                        placeholder="Ví dụ: Deep Learning for Cancer Cell Classification in Histopathology",
                        lines=2
                    )
                    draft_synthesis = gr.Textbox(
                        label="Ghi chú Tổng hợp (Synthesis Notes)",
                        placeholder=(
                            "Dán kết quả tổng hợp nghiên cứu vào đây — từ tab ReAct Agent hoặc từ synthesize_findings.\n"
                            "Ví dụ: Paper 1 — Deep Learning Models (Jenkins et al., 2022) đạt 98.2% precision...\n"
                            "Paper 2 — BERT (Devlin et al., 2018) shows bidirectional context..."
                        ),
                        lines=10
                    )
                    draft_style = gr.Dropdown(
                        label="Định dạng Trích dẫn (Citation Style)",
                        choices=["APA", "IEEE", "BibTeX"],
                        value="APA"
                    )
                    draft_btn = gr.Button("✍️ Tạo Bản Thảo Bài Báo", variant="primary")
                with gr.Column():
                    draft_output = gr.Textbox(
                        label="Bản Thảo Bài Báo (Paper Draft)",
                        lines=30,
                        interactive=False
                    )
            draft_btn.click(
                fn=run_draft_paper,
                inputs=[draft_topic, draft_synthesis, draft_style],
                outputs=draft_output
            )

        # Tab 3: Academic Text Polisher
        with gr.TabItem("✍️ Academic Text Polisher"):
            gr.Markdown("""
            ### Công cụ Biên tập Khoa học (Cognitive Polisher Tool)
            Nhập đoạn nháp, ý tưởng thô sơ hoặc ghi chú thí nghiệm. Công cụ sẽ viết lại thành văn phong học thuật chuẩn mực.
            """)
            with gr.Row():
                with gr.Column():
                    raw_text = gr.Textbox(
                        label="Văn bản Nháp Thô (Draft Text)",
                        placeholder="Ví dụ: we ran tests on deep learning and got 95% accuracy which is cool",
                        lines=6
                    )
                    tone_dropdown = gr.Dropdown(
                        label="Văn phong Đích (Target Tone)",
                        choices=[
                            "formal academic style",
                            "concise conference abstract",
                            "highly technical paper description",
                            "grant proposal writing style"
                        ],
                        value="formal academic style"
                    )
                    polish_btn = gr.Button("✨ Đánh Bóng Văn Bản", variant="primary")
                with gr.Column():
                    polished_text = gr.Textbox(
                        label="Kết quả Đã Biên Tập (Polished Academic Prose)",
                        lines=10,
                        interactive=False
                    )
            polish_btn.click(fn=run_polisher, inputs=[raw_text, tone_dropdown], outputs=polished_text)

        # Tab 4: Citation Formatter
        with gr.TabItem("📖 Citation Formatter"):
            gr.Markdown("""
            ### Bộ Định dạng Trích dẫn Quốc tế (Citation Formatter Tool)
            Điền thông tin thư mục để sinh chuỗi tài liệu tham khảo chuẩn APA, IEEE hoặc BibTeX.
            """)
            with gr.Row():
                with gr.Column():
                    paper_title = gr.Textbox(
                        label="Tiêu đề Bài báo (Paper Title)",
                        placeholder="Ví dụ: Attention Is All You Need",
                        value="Attention Is All You Need"
                    )
                    paper_authors = gr.Textbox(
                        label="Danh sách Tác giả (Authors - cách nhau bằng dấu phẩy)",
                        placeholder="Ví dụ: Ashish Vaswani, Noam Shazeer, Niki Parmar",
                        value="Ashish Vaswani, Noam Shazeer, Niki Parmar"
                    )
                    paper_year = gr.Textbox(
                        label="Năm Xuất Bản (Year)",
                        placeholder="Ví dụ: 2017",
                        value="2017"
                    )
                    citation_style = gr.Dropdown(
                        label="Định dạng Tài liệu Tham khảo (Style)",
                        choices=["APA", "IEEE", "BIBTEX"],
                        value="APA"
                    )
                    citation_btn = gr.Button("📑 Sinh Trích Dẫn", variant="primary")
                with gr.Column():
                    citation_output = gr.Textbox(
                        label="Trích dẫn Chuẩn Hóa (Formatted Citation)",
                        lines=6,
                        interactive=False
                    )
            citation_btn.click(
                fn=run_citation,
                inputs=[paper_title, paper_authors, paper_year, citation_style],
                outputs=citation_output
            )

    gr.HTML("""
        <div style="text-align: center; margin-top: 30px; font-size: 0.9rem; color: #6b7280;
                    border-top: 1px solid #e5e7eb; padding-top: 15px;">
            Hệ thống phát triển bởi Nhóm <strong>AI Agent Hỗ Trợ Viết Bài Nghiên Cứu Khoa Học</strong>
            &bull; Lab 3 - Production-Grade Agentic System
        </div>
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"),
        css=custom_css
    )
