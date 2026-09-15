from pathlib import Path

import yaml


def test_ai_discovery_agent_and_browser_handoff_exist():
    agent_path = Path(".github/agents/fabric-adoption-discovery.agent.md")
    content = agent_path.read_text(encoding="utf-8")
    _, frontmatter, body = content.split("---", maxsplit=2)
    metadata = yaml.safe_load(frontmatter)
    html = Path("index.html").read_text(encoding="utf-8")

    assert metadata["name"] == "Fabric Adoption Discovery"
    assert "microsoft-learn/*" in metadata["tools"]
    assert "adaptive conversation" in body
    assert 'id="startAiDiscoveryBtn"' in html
    assert 'readiness === null ? "N/A"' in html