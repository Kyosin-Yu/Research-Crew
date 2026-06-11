# app.py
import streamlit as st
import threading
import queue
import time
from datetime import datetime
from crew import run_research_crew
from memory.vectorStore import ResearchMemory
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Page Configuration ────────────────────────────────────────────
st.set_page_config(
    page_title="Research Crew",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #58a6ff;
        text-align: center;
        padding: 1rem 0;
    }
    .agent-card {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #ddd;
        color: #e6edf3;
    }
    .agent-waiting  { 
        border-left-color: #8b949e; 
        background: #21262d; 
    }
    .agent-running  { 
        border-left-color: #d29922; 
        background: #272115; 
        color: #e3b341;
    }
    .agent-complete { 
        border-left-color: #3fb950; 
        background: #12261e; 
        color: #3fb950;
    }
    .agent-error    { 
        border-left-color: #f85149; 
        background: #2d1117; 
        color: #f85149;
    }
    .report-box {
        background: #161b22;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid #30363d;
        color: #e6edf3;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State Initialization ──────────────────────────────────
# Session state persists values between Streamlit reruns
def init_session_state():
    defaults = {
        "running": False,
        "completed": False,
        "result": None,
        "error": None,
        "agent_status": {
            "Researcher":  {"status": "waiting", "message": ""},
            "Analyzer":    {"status": "waiting", "message": ""},
            "Writer":      {"status": "waiting", "message": ""},
            "Reviewer":    {"status": "waiting", "message": ""},
        },
        "logs": [],
        "start_time": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


# ── Helper Functions ──────────────────────────────────────────────
def get_status_icon(status: str) -> str:
    icons = {
        "waiting":  "⬜",
        "running":  "⏳",
        "complete": "✅",
        "error":    "❌"
    }
    return icons.get(status, "⬜")


def reset_state():
    """Resets all state for a fresh run."""
    st.session_state.running = False
    st.session_state.completed = False
    st.session_state.result = None
    st.session_state.error = None
    st.session_state.logs = []
    st.session_state.start_time = None
    for agent in st.session_state.agent_status:
        st.session_state.agent_status[agent] = {
            "status": "waiting",
            "message": ""
        }


def run_crew_thread(topic: str, result_queue: queue.Queue):
    """
    Runs the crew in a background thread so Streamlit UI stays responsive.
    Results are passed back via a Queue.
    """
    try:
        result = run_research_crew(topic)
        result_queue.put({"success": True, "result": result})
    except Exception as e:
        result_queue.put({"success": False, "error": str(e)})


# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("📚 Research History")

    try:
        memory = ResearchMemory()
        topics = memory.list_all_topics()

        if topics:
            st.write(f"**{len(topics)} topics researched:**")
            for topic in topics:
                st.write(f"• {topic}")
        else:
            st.info("No research history yet.")

    except Exception as e:
        st.warning("Memory unavailable")

    st.divider()
    st.header("ℹ️ About")
    st.write("""
    **Research Crew** uses 4 AI agents:
    - 🔍 **Researcher** — gathers information
    - 🧠 **Analyzer** — synthesizes findings
    - ✍️ **Writer** — writes the report
    - ✔️ **Reviewer** — ensures quality
    """)

    st.divider()
    st.caption("Built with CrewAI + Streamlit")


# ── Main Content ──────────────────────────────────────────────────
st.markdown(
    '<div class="main-header">🔬 Research & Report Generation Crew</div>',
    unsafe_allow_html=True
)
st.markdown(
    "Enter any research topic and let your AI crew autonomously "
    "research, analyze, write, and review a comprehensive report.",
    )

st.divider()

# ── Input Section ─────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])

with col1:
    topic = st.text_input(
        label="Research Topic",
        placeholder="e.g. The impact of artificial intelligence on healthcare",
        disabled=st.session_state.running,
        label_visibility="collapsed"
    )

with col2:
    start_button = st.button(
        label="🚀 Start Research" if not st.session_state.running else "⏳ Running...",
        disabled=st.session_state.running or not topic,
        use_container_width=True,
        type="primary"
    )

# ── Handle Start Button ───────────────────────────────────────────
if start_button and topic and not st.session_state.running:
    reset_state()
    st.session_state.running = True
    st.session_state.start_time = datetime.now()

    # Run crew in background thread
    result_queue = queue.Queue()
    thread = threading.Thread(
        target=run_crew_thread,
        args=(topic, result_queue),
        daemon=True
    )
    thread.start()

    # Store thread and queue in session state
    st.session_state.thread = thread
    st.session_state.result_queue = result_queue
    st.rerun()

# ── Progress Section ──────────────────────────────────────────────
if st.session_state.running or st.session_state.completed:

    st.subheader("📊 Agent Progress")

    # Check for results from background thread
    if st.session_state.running:
        try:
            result_data = st.session_state.result_queue.get_nowait()

            if result_data["success"]:
                st.session_state.result = result_data["result"]
                st.session_state.completed = True
                # Mark all agents complete
                for agent in st.session_state.agent_status:
                    st.session_state.agent_status[agent]["status"] = "complete"
            else:
                st.session_state.error = result_data["error"]
                st.session_state.completed = True

            st.session_state.running = False

        except queue.Empty:
            pass  # Still running, no result yet

    # Display agent status cards
    agents_info = {
        "Researcher": "🔍 Searching the web and gathering information",
        "Analyzer":   "🧠 Synthesizing findings into structured insights",
        "Writer":     "✍️ Crafting the research report",
        "Reviewer":   "✔️ Reviewing and polishing the final report",
    }

    for agent_name, description in agents_info.items():
        status = st.session_state.agent_status[agent_name]["status"]
        icon = get_status_icon(status)
        css_class = f"agent-{status}"

        st.markdown(
            f'<div class="agent-card {css_class}">'
            f'{icon} <strong>{agent_name}</strong> — {description}'
            f'</div>',
            unsafe_allow_html=True
        )

    # Auto-refresh while running
    if st.session_state.running:
        elapsed = (datetime.now() - st.session_state.start_time).seconds
        st.info(f"⏱️ Research in progress... {elapsed}s elapsed")
        time.sleep(2)
        st.rerun()

# ── Result Section ────────────────────────────────────────────────
if st.session_state.completed:

    if st.session_state.error:
        st.error(f"❌ Research failed: {st.session_state.error}")

    elif st.session_state.result:
        st.divider()
        st.subheader("📄 Research Complete!")

        # Show elapsed time
        if st.session_state.start_time:
            elapsed = (datetime.now() - st.session_state.start_time).seconds
            st.success(f"✅ Completed in {elapsed} seconds")

        # Display report
        st.markdown("### Final Report")
        st.markdown(
            '<div class="report-box">',
            unsafe_allow_html=True
        )
        st.markdown(st.session_state.result)  # renders proper Markdown
        st.markdown('</div>', unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="⬇️ Download Report",
            data=str(st.session_state.result),
            file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )

    # New research button
    if st.button("🔄 New Research", type="secondary"):
        reset_state()
        st.rerun()