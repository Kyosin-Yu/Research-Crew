import pytest
from unittest.mock import patch, MagicMock
from workflows.researchWorkflow import create_research_tasks
from config.settings import validate_settings

#manually set required attributes for mock test
def make_mock_agent():
    agent_mock = MagicMock()
    agent_mock.role = "Test Agent"
    agent_mock.goal = "Test goal"
    agent_mock.backstory = "Test backstory"
    agent_mock.allow_delegation = False
    agent_mock.tools = []
    agent_mock.verbose = False
    agent_mock.max_iter = 10
    agent_mock.max_rpm = 10
    agent_mock.llm = MagicMock()
    return agent_mock

#settings test
class TestSetting:
    def test_validate_setting_raises_on_missing_keys(self):
        """validate_settings should raise ValueError if keys missing."""
        with patch("config.settings.OPENROUTER_API_KEY", None), \
             patch("config.settings.SERPER_API_KEY", None):
            with pytest.raises(ValueError) as exc_info:
                validate_settings()
            assert "OPENROUTER_API_KEY" in str(exc_info.value)

    def test_validate_settings_passes_with_keys(self):
        """validate_settings should pass silently when keys present."""
        with patch("config.settings.OPENROUTER_API_KEY", "fake-key"), \
             patch("config.settings.SERPER_API_KEY", "fake-key"):
            #should not raise
            validate_settings()

#workflow tests
class TestResearchWorkFlow:
    def test_creates_four_tasks(self):
        tasks, agents = create_research_tasks("test topic")
        assert len(tasks) == 4

    def test_creates_four_agents(self):
        tasks, agents = create_research_tasks("test topic")
        assert len(agents) == 4

    def test_topic_appears_in_task_description(self):
        topic = "quantum computing applications"
        tasks, _ = create_research_tasks(topic)
        assert topic in tasks[0].description

    def test_past_context_injected_when_provided(self):
        past_context = "PAST RESEARCH: previous findings here"
        tasks, _ = create_research_tasks(
            topic="test topic",
            past_context=past_context
        )
        assert past_context in tasks[0].description