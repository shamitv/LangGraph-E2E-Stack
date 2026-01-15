import json
import os
import re
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from ...core.config import settings

def load_policy_readme(policies_dir: Path) -> str:
    readme_path = policies_dir / "README.md"
    if not readme_path.exists():
        return "(No policy index found)"
    try:
        return readme_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"(Error loading policy index: {e})"

def load_specific_policies(policies_dir: Path, policy_files: list[str]) -> str:
    if not policies_dir.exists():
        return "(Policies directory not found)"

    policy_content = []
    for policy_name in policy_files:
        clean_name = policy_name.strip().lower().replace(" ", "_")
        if clean_name.endswith(".md"):
            clean_name = clean_name[:-3]

        policy_file = policies_dir / f"{clean_name}.md"
        if policy_file.exists():
            try:
                content = policy_file.read_text(encoding="utf-8")
                policy_content.append(f"--- {clean_name.upper()} ---\n{content}")
            except Exception as e:
                policy_content.append(f"--- {clean_name.upper()} ---\n(Error loading: {e})")
        else:
            policy_content.append(f"--- {clean_name.upper()} ---\n(Policy file not found: {clean_name})")

    return "\n\n".join(policy_content) if policy_content else "(No policies loaded)"

@tool("policy_check")
def policy_check(request_type: str, details: str) -> str:
    """
    Check proposed appointments/medications/services against healthcare policy criteria.
    Returns structured JSON with status (PASS/REQUIRES_REVIEW/BLOCKED), violations, and requirements.
    """
    policies_dir = Path(settings.DATA_DIR) / "policies"
    
    # Initialize a clean LLM for policy checks
    policy_llm = ChatOpenAI(
        model=settings.OPENAI_MODEL_NAME,
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_API_BASE,
    )

    # Phase 1: Identify relevant policies from README
    readme_content = load_policy_readme(policies_dir)
    selection_prompt = f"""Identify which policy file basenames are relevant to this request.
## POLICY INDEX:
{readme_content}

## REQUEST:
- {request_type}: {details}

Return ONLY a JSON array of filenames (no extension). Example: ["controlled_substances"]"""

    try:
        selection_resp = policy_llm.invoke([SystemMessage(content=selection_prompt)])
        selection_content = re.sub(r"```json\s*", "", selection_resp.content or "").replace("```", "").strip()
        selected_policies = json.loads(selection_content)
        if not isinstance(selected_policies, list):
             selected_policies = ["visit_type_restrictions"]
    except Exception:
        selected_policies = ["visit_type_restrictions"]

    # Phase 2: Evaluate against selected policies
    policy_text = load_specific_policies(policies_dir, selected_policies)
    evaluation_prompt = f"""Evaluate this healthcare request against the policies provided.
## POLICIES:
{policy_text}

## REQUEST:
- {request_type}: {details}

Return ONLY JSON:
{{
    "status": "PASS" | "REQUIRES_REVIEW" | "BLOCKED",
    "violations": [],
    "requirements": []
}}"""

    try:
        eval_resp = policy_llm.invoke([SystemMessage(content=evaluation_prompt)])
        eval_content = re.sub(r"```json\s*", "", eval_resp.content or "").replace("```", "").strip()
        return eval_content
    except Exception as e:
        return json.dumps({"status": "REQUIRES_REVIEW", "error": str(e)})
